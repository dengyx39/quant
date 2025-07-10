import os
import time
import tushare as ts
import pandas as pd
import numpy as np
from tqdm import tqdm
from fetch import *

# ========== 初始化配置 ==========
# 路径配置
base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, "..", "数据源csv", "周线数据")
os.makedirs(output_dir, exist_ok=True)

# Tushare初始化
token = get_token()
pro = ts.pro_api(token)

# 参数配置
date = get_prev_trade_date()
start_date = "20220427"
stock_list_path = os.path.join(base_dir, "..", "数据源csv", "股票列表.csv")

# 读取股票列表
data = pd.read_csv(stock_list_path)
index = data["ts_code"].tolist()

# 周线数据列名映射
week_column_mapping = {
    'ts_code': '股票代码',
    'trade_date': '交易日期',
    'open': '开盘价',
    'high': '最高价',
    'low': '最低价',
    'close': '收盘价',
    'pre_close': '昨收价',
    'change': '涨跌额',
    'pct_chg': '涨跌幅',
    'vol': '成交量',
    'amount': '成交额（千元）'
}

# ========== 主循环 ==========
for code in tqdm(index, total=len(index), desc="A-share weekly", unit="stk"):
    max_try = 3
    try_count = 0
    while try_count < max_try:
        try:
            # 获取数据
            df_week = pro.stk_week_month_adj(
                ts_code=code,
                freq='W',
                start_date=start_date,
                adj='hfq'
            )

            if df_week.empty:
                print(f"{code} 无数据，跳过")
                break

            df_week.rename(columns=week_column_mapping, inplace=True)
            output_path = os.path.join(output_dir, f"{code}.csv")

            if os.path.exists(output_path):
                df_old = pd.read_csv(output_path)
                existing_dates = set(df_old['交易日期'].astype(str).values)
                df_week = df_week[~df_week['交易日期'].astype(str).isin(existing_dates)]

                if df_week.empty:
                    print(f"{code} 所有日期已存在，跳过写入")
                    break

                df_all = pd.concat([df_week, df_old], ignore_index=True)
            else:
                df_all = df_week

            df_all.to_csv(output_path, mode='w', header=True, index=False, encoding='utf-8-sig')
            print(f"{code} 写入完成，共 {len(df_week)} 条新数据")
            break

        except Exception as e:
            print(f"处理股票 {code} 时出错：{e}")
            try_count += 1
            time.sleep(20)
    if try_count >= max_try:
        print(f"{code} 多次写入失败")

print("所有股票周线数据处理完成！")
