# Git Guide — savvy773/empty

## 이 프로젝트 기본 명령어

```bash
# 변경사항 올리기 (자동으로 Home / Office 감지)
python _push_home.py
python _push_home.py "커밋 메시지 직접 입력"

# 최신 코드 받기
git pull origin main

# 상태 확인
git status
git log --oneline
```

---

## 브랜치(Branch) 개념

```
main           ──●──────────────────────●── 완성된 코드
                  \                    /
feature/login      ●──●──●──●──●──●      기능 개발 중
```

| 브랜치 종류 | 역할 |
|---|---|
| `main` | 완성된 코드만 있는 메인 라인 |
| `feature/xxx` | 기능 하나를 개발하는 작업 브랜치 |
| `hotfix/xxx` | 급한 버그 수정용 브랜치 |

---

## 브랜치 실습 (순서대로 따라하기)

### 1. 현재 브랜치 확인
```bash
git branch
# * main  ← 별표가 현재 위치
```

### 2. feature 브랜치 만들기
```bash
git checkout -b feature/test
# = 브랜치 생성 + 이동을 한 번에
```

### 3. 파일 수정 후 커밋
```bash
# 아무 파일이나 수정 후
git add .
git commit -m "Add test feature"
```

### 4. main으로 돌아오기
```bash
git checkout main
# 이 순간 수정한 내용이 "사라진 것처럼" 보임
# (feature 브랜치에만 있는 것, 삭제된 게 아님)
```

### 5. 브랜치 목록 확인
```bash
git branch
#   feature/test
# * main
```

### 6. merge — 브랜치를 main에 합치기
```bash
git merge feature/test
# feature/test 의 커밋이 main으로 합쳐짐
```

### 7. 다 쓴 브랜치 삭제
```bash
git branch -d feature/test
```

---

## 자주 쓰는 Git 명령어 모음

### 조회
```bash
git status                  # 변경된 파일 목록
git log --oneline           # 커밋 히스토리 한 줄씩
git log --oneline --graph   # 브랜치 그래프로 보기
git diff                    # 수정 내용 상세 비교
git branch                  # 로컬 브랜치 목록
git branch -a               # 원격 포함 전체 브랜치
```

### 커밋
```bash
git add .                   # 모든 변경사항 스테이징
git add 파일명              # 특정 파일만 스테이징
git commit -m "메시지"      # 커밋
git commit --amend          # 마지막 커밋 메시지 수정
```

### 브랜치
```bash
git checkout -b 브랜치명    # 브랜치 생성 + 이동
git checkout 브랜치명       # 브랜치 이동
git merge 브랜치명          # 현재 브랜치에 합치기
git branch -d 브랜치명      # 브랜치 삭제
```

### 원격 (GitHub)
```bash
git push origin main        # main 브랜치 올리기
git push origin 브랜치명    # 특정 브랜치 올리기
git pull origin main        # main 최신화
git clone URL               # 레포 복제
```

### 되돌리기
```bash
git restore 파일명          # 수정 전으로 되돌리기 (커밋 전)
git reset HEAD~1            # 마지막 커밋 취소 (파일은 유지)
git stash                   # 작업 임시 저장 (브랜치 이동 전에 유용)
git stash pop               # 임시 저장 복원
```

---

## Home ↔ Office 작업 흐름

```
[Home]                              [Office]
python _push_home.py          →     git pull origin main
  커밋: [Home] 2026-03-21 ...         작업 시작
                               ←     python _push_home.py
                                       커밋: [Office] 2026-03-21 ...
git pull origin main          →     (반복)
```

> 규칙: 작업 시작 전 항상 `git pull`, 끝나면 항상 `push`

---

## Pull Request (PR) 흐름

PR = 내가 만든 브랜치를 main에 합쳐달라는 "요청서"
혼자 쓸 때도 PR 습관을 들이면 변경 이력이 깔끔하게 남음

### 전체 그림

```
GitHub
─────────────────────────────────────────────
main           ──●─────────────────────────●──
                  \                       /
feature/login      ●──●──●  →  [PR 열기] → (리뷰) → Merge
```

---

### A. 내가 feature 만들어서 PR 올리는 흐름

```bash
# 1. main 최신화
git checkout main
git pull origin main

# 2. feature 브랜치 생성
git checkout -b feature/login

# 3. 작업 후 커밋
git add .
git commit -m "Add login page"

# 4. GitHub에 브랜치 올리기
git push origin feature/login
```

GitHub에서:
1. 레포 접속 → **Compare & pull request** 버튼 클릭
2. 제목 / 설명 작성
3. **Create pull request** 클릭

---

### B. 다른 사람이 PR 올렸을 때 내가 받아서 merge하는 흐름

GitHub에서:
1. **Pull requests** 탭 클릭
2. PR 클릭 → 변경 내용 확인 (Files changed 탭)
3. 문제 없으면 **Merge pull request** → **Confirm merge**
4. 브랜치 삭제 버튼 클릭 (Delete branch)

로컬에서 최신화:
```bash
git checkout main
git pull origin main
# 이제 로컬 main에도 merge된 내용이 들어옴
```

---

### C. PR + Home/Office 합친 실전 흐름

```
[Home]
  git checkout -b feature/xxx
  작업 → commit
  git push origin feature/xxx
  → GitHub에서 PR 오픈
        ↓
[GitHub]
  PR 리뷰 → Merge
        ↓
[Office]
  git checkout main
  git pull origin main      ← merge된 코드 받기
  다음 feature 작업 시작
```

---

### PR 관련 명령어

```bash
git push origin 브랜치명          # 브랜치 GitHub에 올리기 (PR 전 필수)
git pull origin main              # merge 후 로컬 최신화
git branch -d feature/xxx         # 로컬 브랜치 정리
git push origin --delete feature/xxx  # 원격 브랜치 삭제
```
