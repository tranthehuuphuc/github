import pandas as pd
import argparse
import os

def convert_xlsx_to_csv(xlsx_path, output_path=None, sheet_name=0):
    try:
        df = pd.read_excel(xlsx_path, sheet_name=sheet_name, engine='openpyxl')
        
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(xlsx_path))[0]
            output_path = f"{base_name}.csv"

        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"✅ Converted '{xlsx_path}' to '{output_path}' successfully.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert .xlsx file to .csv format")

    parser.add_argument("-i", "--input", help="Path to the .xlsx file")
    parser.add_argument("-o", "--output", help="Path to save the .csv file (default is the same as the input file name)")
    parser.add_argument("-s", "--sheet", help="Name or index of the sheet (default is the first sheet)", default=0)

    args = parser.parse_args()

    # If sheet is a number, convert to int
    try:
        sheet_arg = int(args.sheet)
    except ValueError:
        sheet_arg = args.sheet

    convert_xlsx_to_csv(args.input, args.output, sheet_arg)
