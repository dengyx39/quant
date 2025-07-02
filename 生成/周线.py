import tushare as ts
import pandas as pd
import datetime
import config
import numpy as np
from arch import arch_model
import matplotlib.pyplot as plt
import seaborn as sns

# 设置是否不买入科创板和创业板股票
buy_able = True
start_date = "20200101"
data = pd.read_csv(r"C:\Users\24645\Desktop\量化/数据源csv/股票列表.csv")
index = data["ts_code"]
pro = ts.pro_api(config.token)
for code in list(index):
    if buy_able:
    #如果code非科创板创业板（即60和00开头）才会执行
        if not ((code[0] == '6' or code[0] == '0') and code[1] == '0'):
            continue
    print(code)
    df_week_adj = pro.stk_week_month_adj(ts_code=code, freq='week', start_date=start_date, adj='hfq')
    #设计一个英文列名到中文列名的转换map
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

    df_week_adj.rename(columns=column_mapping, inplace=True)
    df_week_adj.to_csv(rf'C:\Users\24645\Desktop\量化\数据源csv\周线数据\{code}.csv', mode='w', header=True)
