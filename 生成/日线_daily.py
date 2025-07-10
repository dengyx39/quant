import os
import time
import tushare as ts
import pandas as pd
import numpy as np
from tqdm import tqdm
from datetime import datetime, timedelta
from fetch import *

# 初始化路径
base_dir = os.path.dirname(os.path.abspath(__file__))  # 脚本所在目录
output_dir = os.path.join(base_dir, "..", "数据源csv", "日线数据")
os.makedirs(output_dir, exist_ok=True)
# 初始化Tushare
token = get_token()
pro = ts.pro_api(token)
# 获取上一个交易日
# start_date, end_date = get_start_end_date(pro,output_dir+"/000001.SZ.csv")
# print(start_date,end_date)
date = get_prev_trade_date()
start_date = "20220427"
stock_list_path = os.path.join(base_dir, "..", "数据源csv", "股票列表.csv")
data = pd.read_csv(stock_list_path)
index = data["ts_code"].tolist()

column_mapping = {
    'ts_code': '股票代码',
    'trade_date': '交易日期',
    'open': '开盘价',
    'high': '最高价',
    'low': '最低价',
    'close_x': '收盘价',
    'pre_close': '昨收价【除权价，前复权】',
    'change': '涨跌额',
    'pct_chg': '涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收 】',
    'vol': '成交量',
    'amount': '成交额（千元）',
    'turnover_rate': '换手率',
    'turnover_rate_f': '换手率（自由流通股）',
    'volume_ratio': '量比',
    'pe': '市盈率（总市值/净利润，亏损的PE为空）',
    'pe_ttm': '市盈率（TTM，亏损的PE为空）',
    'pb': '市净率（总市值/净资产）',
    'ps': '市销率',
    'ps_ttm': '市销率（TTM）',
    'dv_ratio': '股息率 （%）',
    'dv_ttm': '股息率（TTM）（%）',
    'total_share': '总股本 （万股）',
    'float_share': '流通股本 （万股）',
    'free_share': '自由流通股本 （万）',
    'total_mv': '总市值 （万元）',
    'circ_mv': '流通市值（万元）'
}

for code in tqdm(index, total=len(index), desc="A‑share download", unit="stk"):
    max_try = 3
    try_count = 0
    while try_count < max_try:
        try:
            df_daily = pro.daily(ts_code=code, start_date=start_date, end_date=date)
            df_daily_basic = pro.daily_basic(ts_code=code, start_date=start_date, end_date=date)

            if df_daily.empty or df_daily_basic.empty:
                print(f"{code} 无 {date} 的数据，跳过")
                break

            df_new = pd.merge(df_daily, df_daily_basic, on=['trade_date', 'ts_code'])
            df_new.rename(columns=column_mapping, inplace=True)
            output_path = os.path.join(output_dir, f"{code}.csv")

            if os.path.exists(output_path):
                df_old = pd.read_csv(output_path)
                existing_dates = set(df_old['交易日期'].astype(str).values)
                df_new = df_new[~df_new['交易日期'].astype(str).isin(existing_dates)]

                if df_new.empty:
                    print(f"{code} 所有日期已存在，跳过写入")
                    break

                df_all = pd.concat([df_new, df_old], ignore_index=True)
            else:
                df_all = df_new

            df_all.to_csv(output_path, mode='w', header=True, index=False)
            print(f"{code} 写入完成，共 {len(df_new)} 条新数据")
            break
        except Exception as e:
            print(f"处理股票 {code} 时出错：{e}")
            try_count += 1
            time.sleep(20)
    if try_count >= max_try:
        print(f"{code}多次写入失败")
