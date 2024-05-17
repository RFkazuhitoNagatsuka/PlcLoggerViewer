# Logger Plc data
# Version 1.0
# 2024/5/17

import pandas as pd
import sys
import os
import time
import schedule
from datetime import datetime
from keyenceKV import kvHostLink
from melsecMCP3E import MCProtcol3E

def read_csv_to_list(file_path):
    try:
        df = pd.read_csv(file_path)
        data_list = df.to_dict(orient='records')
        return data_list
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return []

def read_csv_with_headers(file_name):
    try:
        df = pd.read_csv(file_name, header=None)
        columns = df.apply(lambda row: f"{row[0]}({row[1]})", axis=1).tolist()
        return columns
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return []

def identify_consecutive_elements(lst):
    consecutive_elements = []
    if not lst:
        return consecutive_elements

    current_element = lst[0]
    count = 1

    def get_prefix(element):
        return ''.join([c for c in element if not c.isdigit()])

    current_prefix = get_prefix(current_element)

    for i in range(1, len(lst)):
        element = lst[i]
        element_prefix = get_prefix(element)

        if element_prefix == current_prefix:
            count += 1
        else:
            consecutive_elements.append((current_element, count))
            current_element = element
            current_prefix = element_prefix
            count = 1

    consecutive_elements.append((current_element, count))
    return consecutive_elements

def read_from_plc(plc_type, ip, port, read_list):
    if plc_type == "kv-nano":
        plc = kvHostLink(ip, port, 2, 10)
    elif plc_type == "fx5u":
        plc = MCProtcol3E(ip, port)
    else:
        print(f"Unknown PLC type: {plc_type}")
        return {}

    plc_data = {}

    for no, elements in read_list.items():
        data_for_no = {}
        for address, count in elements.items():
            raw_data = plc.reads(address, count)
            if plc_type == "kv-nano":
                parsed_data = [int(value) for value in raw_data.decode().strip().split()]
            elif plc_type == "fx5u":
                parsed_data = raw_data  # int型配列
            data_for_no[address] = parsed_data
        plc_data[no] = data_for_no

    return plc_data

def save_to_csv(file_name, data, headers):
    df = pd.DataFrame(data, columns=headers)
    df.to_csv(file_name, index=False, mode='a', header=not os.path.exists(file_name), encoding='shift_jis')

def collect_data(no, plc_type, ip, port):
    global is_collecting
    if is_collecting[no]:
        return
    is_collecting[no] = True
    try:
        current_time = datetime.now()
        date_str = current_time.strftime("%Y/%m/%d")
        time_str = current_time.strftime("%H:%M:%S")

        plc_data = read_from_plc(plc_type, ip, port, {no: ReadList2[no]})

        data = plc_data[no]
        record = [date_str, time_str]

        for address, values in data.items():
            record.extend(values)

        if row_counts[no] >= max_rows_per_file:
            current_files[no] = f"{data_list[no-1]['ファイル名']}_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
            row_counts[no] = 0

        save_to_csv(current_files[no], [record], Headers[no])
        row_counts[no] += 1
    finally:
        is_collecting[no] = False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv_file_path>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    data_list = read_csv_to_list(csv_file_path)

    ReadList = {}
    ReadList2 = {}
    Headers = {}
    current_files = {}
    row_counts = {}
    max_rows_per_file = 10000
    is_collecting = {}

    for record in data_list:
        no = record['No']
        file_name = record['ファイル名'] + '.csv'
        collection_interval = record['収集周期[s]']
        ip_address = record['収集対象機器IPアドレス']
        port_number = record['収集対象機器ポート番号']
        plc_type = record['機種']

        if os.path.exists(file_name):
            ReadList[no] = read_csv_with_headers(file_name)
            Headers[no] = ['date', 'time'] + ReadList[no]  # CSVのヘッダー情報を取得
            consecutive_elements = identify_consecutive_elements(ReadList[no])
            ReadList2[no] = {elem.split('(')[0]: count for elem, count in consecutive_elements}
            current_files[no] = f"{record['ファイル名']}_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
            row_counts[no] = 0
            is_collecting[no] = False
            # スケジュールの設定
            schedule.every(collection_interval).seconds.do(collect_data, no, plc_type, ip_address, port_number)
        else:
            print(f"ファイルが存在しません: {file_name}")

    try:
        while True:
            schedule.run_pending()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("データ収集を終了しました")
