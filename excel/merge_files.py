"""
동일 폴더의 CSV / XLSX 파일을 time 컬럼 기준 수평 병합(outer join).
- time 파싱: AM/PM 등 다양한 형식 → YYYY-MM-DD HH:MM:SS 통일
- 동일 time에 여러 행 → 순서대로 1:1 매칭
- 파일 간 동일 컬럼명 → 값 병합(coalesce, 앞 파일 우선)
- 없는 값 → 빈 셀
결과: merged_output.csv (동일 위치)
"""

import os
import glob
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "merged_output.xlsx")
TIME_COL = "time"
ROW_IDX = "_row_idx"


def read_file(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".xlsx":
        df = pd.read_excel(path, dtype=str)
    else:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            first_line = f.readline()
        sep = "\t" if first_line.count("\t") > first_line.count(",") else ","
        df = pd.read_csv(path, sep=sep, dtype=str, encoding="utf-8-sig")

    df.columns = df.columns.str.strip()

    if TIME_COL not in df.columns and len(df.columns) > 0:
        df = df.rename(columns={df.columns[0]: TIME_COL})

    return df


def parse_time(series: pd.Series) -> pd.Series:
    """다양한 time 형식(AM/PM 포함)을 datetime으로 파싱."""
    formats = [
        "%Y-%m-%d %I:%M:%S %p",   # 2026-03-14 12:01:36 AM
        "%Y-%m-%d %I:%M %p",      # 2026-03-14 12:01 AM
        "%Y-%m-%d %H:%M:%S",      # 2026-03-14 00:01:36
        "%Y-%m-%d %H:%M",         # 2026-03-14 00:01
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%Y %H:%M:%S",
    ]
    cleaned = series.str.strip()
    for fmt in formats:
        parsed = pd.to_datetime(cleaned, format=fmt, errors="coerce")
        success = parsed.notna().sum()
        if success == len(series.dropna()):
            return parsed
        if success > 0:
            # 일부 성공: 나머지는 fallback
            result = parsed.copy()
            mask = result.isna() & cleaned.notna()
            result[mask] = pd.to_datetime(cleaned[mask], errors="coerce")
            return result

    # 모두 실패하면 pandas 자동 파싱
    return pd.to_datetime(cleaned, errors="coerce")


def coalesce(s1: pd.Series, s2: pd.Series) -> pd.Series:
    """s1 우선, 빈 곳은 s2로 채움."""
    return s1.where(s1.notna() & (s1.str.strip() != ""), s2)


def main():
    patterns = ["*.csv", "*.xlsx"]
    files = []
    for pat in patterns:
        files.extend(glob.glob(os.path.join(SCRIPT_DIR, pat)))
    output_stem = os.path.splitext(os.path.basename(OUTPUT_FILE))[0]
    files = [f for f in files if os.path.splitext(os.path.basename(f))[0] != output_stem]

    if not files:
        print("합칠 파일이 없습니다.")
        return

    print(f"발견된 파일 ({len(files)}개):")
    dfs = []
    for f in sorted(files):
        print(f"  {os.path.basename(f)}", end=" ... ")
        try:
            df = read_file(f)
            df[TIME_COL] = parse_time(df[TIME_COL])

            unparsed = df[TIME_COL].isna().sum()
            if unparsed:
                print(f"[경고] 파싱 실패 {unparsed}행 ", end="")

            # 동일 time 내 행 번호 (순서 보존)
            df[ROW_IDX] = df.groupby(TIME_COL).cumcount()
            dfs.append(df)
            print(f"{len(df):,} rows, {len(df.columns)-2} value cols")
        except Exception as e:
            print(f"오류: {e}")

    if not dfs:
        return

    # 순차 outer join, 중복 컬럼은 coalesce
    merged = dfs[0]
    for df in dfs[1:]:
        # 이미 merged에 있는 컬럼 vs 새 컬럼 구분
        existing_cols = set(merged.columns) - {TIME_COL, ROW_IDX}
        new_cols = set(df.columns) - {TIME_COL, ROW_IDX}
        overlap = existing_cols & new_cols
        unique_new = new_cols - overlap

        if overlap:
            # 겹치는 컬럼만 임시 suffix로 merge 후 coalesce
            df_renamed = df.rename(columns={c: c + "__new__" for c in overlap})
            merged = pd.merge(merged, df_renamed, on=[TIME_COL, ROW_IDX], how="outer")
            for c in overlap:
                merged[c] = coalesce(merged[c].astype(str).replace("nan", pd.NA),
                                     merged[c + "__new__"].astype(str).replace("nan", pd.NA))
                merged = merged.drop(columns=[c + "__new__"])
        else:
            merged = pd.merge(merged, df[[TIME_COL, ROW_IDX] + list(unique_new)],
                              on=[TIME_COL, ROW_IDX], how="outer")

    merged = merged.drop(columns=[ROW_IDX])

    # time 맨 앞, 정렬
    cols = [TIME_COL] + [c for c in merged.columns if c != TIME_COL]
    merged = merged[cols].sort_values(TIME_COL, kind="stable").reset_index(drop=True)

    # time → 문자열
    merged[TIME_COL] = merged[TIME_COL].dt.strftime("%Y-%m-%d %H:%M:%S")

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        merged.to_excel(writer, index=False, sheet_name="merged", na_rep="")
        ws = writer.sheets["merged"]
        ws.freeze_panes = "B2"  # A열(time) + 1행(헤더) 고정

    print(f"\n저장 완료: {OUTPUT_FILE}")
    print(f"총 {len(merged):,} rows × {len(merged.columns)} cols")


if __name__ == "__main__":
    main()
