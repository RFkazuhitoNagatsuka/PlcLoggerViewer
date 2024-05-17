# Viewer for csv files generated with logger software
# Version 1.0
# 2024/5/17

import pandas as pd
import xlsxwriter
import re
import os
import sys
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename

def create_excel_with_sparklines(csv_file_path):
    # CSVファイルの読み込み（エンコーディングをShift-JISに設定）
    df = pd.read_csv(csv_file_path, encoding='shift_jis')

    # Tkinterの初期化
    root = Tk()
    root.withdraw()  # Tkinterウィンドウを非表示にする

    # ファイル保存ダイアログを表示
    output_file_path = asksaveasfilename(defaultextension='.xlsx', filetypes=[("Excel files", "*.xlsx")])
    if not output_file_path:
        print("ファイル保存がキャンセルされました。")
        return

    # 新しいExcelワークブックの作成
    workbook = xlsxwriter.Workbook(output_file_path)
    worksheet = workbook.add_worksheet()

    # 列ヘッダーの追加
    headers = ['name', 'explanation', 'min', 'max', 'ave', 'graph'] + list(range(1, len(df) + 1))
    worksheet.write_row('A1', headers)

    # dateとtimeの行を追加
    worksheet.write_row('A2', ['date', '', '', '', '', ''] + df['date'].tolist())
    worksheet.write_row('A3', ['time', '', '', '', '', ''] + df['time'].tolist())

    # データ行の追加
    row_num = 3
    for index, row in df.set_index(['date', 'time']).T.iterrows():
        name = re.sub(r'\(.*?\)', '', index)
        explanation = re.findall(r'\((.*?)\)', index)[0] if re.findall(r'\((.*?)\)', index) else ''
        worksheet.write_row(row_num, 0, [name, explanation] + ['']*4 + row.tolist())
        row_num += 1

    # min, max, ave のExcel式を追加
    for row in range(3, 3 + len(df.columns) - 2):
        data_range = f'G{row+1}:{xlsxwriter.utility.xl_col_to_name(6 + len(df) - 1)}{row+1}'
        worksheet.write_formula(row, 2, f'=MIN({data_range})')
        worksheet.write_formula(row, 3, f'=MAX({data_range})')
        worksheet.write_formula(row, 4, f'=AVERAGE({data_range})')

    # スパークラインの追加
    for row in range(3, 3 + len(df.columns) - 2):
        data_range = f'G{row+1}:{xlsxwriter.utility.xl_col_to_name(6 + len(df) - 1)}{row+1}'
        worksheet.add_sparkline(f'F{row+1}', {'range': data_range, 'type': 'line'})

    # ワークブックの保存
    workbook.close()

    print(f"Excelファイルが作成されました: {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv_file_path>")
    else:
        csv_file_path = sys.argv[1]
        create_excel_with_sparklines(csv_file_path)
