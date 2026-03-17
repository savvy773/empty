import os
import win32com.client

def clean_excel(file_path, output_path):
    print(f"Cleaning {file_path}")
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    
    try:
        workbook = excel.Workbooks.Open(file_path)
        for sheet in workbook.Worksheets:
            print(f"Processing sheet: {sheet.Name}")
            
            # Find the last used row and column based on actual values
            # Using Find to get the very last cell with data
            last_cell = sheet.Cells.Find(What="*", After=sheet.Cells(1,1), SearchOrder=1, SearchDirection=2) # xlRows=1, xlPrevious=2
            last_row = last_cell.Row if last_cell else 1
            
            last_cell_col = sheet.Cells.Find(What="*", After=sheet.Cells(1,1), SearchOrder=2, SearchDirection=2) # xlByColumns=2, xlPrevious=2
            last_col = last_cell_col.Column if last_cell_col else 1
            
            # Delete rows below the last used row
            max_rows = sheet.Rows.Count
            if last_row < max_rows:
                sheet.Range(sheet.Rows(last_row + 1), sheet.Rows(max_rows)).Delete()
                
            # Delete columns to the right of the last used column
            max_cols = sheet.Columns.Count
            if last_col < max_cols:
                # Convert column number to letter or use Cells
                sheet.Range(sheet.Columns(last_col + 1), sheet.Columns(max_cols)).Delete()
                
            # Access UsedRange to reset it
            _ = sheet.UsedRange
            
        workbook.SaveAs(output_path)
        print(f"Saved cleaned file to {output_path}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        workbook.Close(SaveChanges=False)
        excel.Quit()

if __name__ == "__main__":
    input_file = os.path.abspath("ISL_Taglist_Atlas9_260311_Rev28.xlsx")
    output_file = os.path.abspath("ISL_Taglist_Atlas9_260311_Rev28_Cleaned.xlsx")
    clean_excel(input_file, output_file)
