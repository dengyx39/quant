import tushare as ts
import pandas as pd
import numpy as np
from arch import arch_model
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime, timedelta
from fetch import *

# 初始化路径
base_dir = os.path.dirname(os.path.abspath(__file__))  # 脚本所在目录
output_dir = os.path.join(base_dir, "..", "数据源csv", "日线数据")
os.makedirs(output_dir, exist_ok=True)  # 若没有，自动创建目录
# 初始化Tushare
token = get_token()
pro = ts.pro_api(token)
#获取上一个交易日
date = get_prev_trade_date()

# 设置是否不买入科创板和创业板股票
buy_KCB_CYB= False
start_date = "20180701"
data = pd.read_csv("../数据源csv/股票列表.csv")
index = data["ts_code"]

for code in list(index):
    if not buy_KCB_CYB:
        # 如果code是科创板创业板就直接略过
        if not ((code[0] == '6' or code[0] == '0') and code[1] == '0'):
            continue

    print(f"处理股票：{code}")

    # 只取今天的数据
    df_daily = pro.daily(ts_code=code, start_date=date, end_date=date)
    df_daily_basic = pro.daily_basic(ts_code=code, start_date=date, end_date=date)

    if df_daily.empty or df_daily_basic.empty:
        print(f"{code} 无 {date} 的数据，跳过")
        continue

    df_new = pd.merge(df_daily, df_daily_basic, on=['trade_date','ts_code'])

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

    df_new.rename(columns=column_mapping, inplace=True)
    output_path = os.path.join(output_dir, f"{code}.csv")

    # 如果文件存在，读原数据，加在新数据后面
    if os.path.exists(output_path):
        df_old = pd.read_csv(output_path)
        # 检查是否已有当天数据，避免重复插入
        if str(date) in df_old['交易日期'].astype(str).values:
            print(f"{code} 已存在 {date} 数据，跳过写入")
            continue
        df_all = pd.concat([df_new, df_old], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_csv(output_path, mode='w', header=True, index=False)
