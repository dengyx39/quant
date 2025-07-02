import tushare as ts
import pandas as pd
import config
import numpy as np
from arch import arch_model
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import mplfinance as mpf
import os
from sklearn.linear_model import LinearRegression

# today = datetime.date.today().strftime('%Y%m%d')

def plot_kline(df: pd.DataFrame, start_date: str, end_date: str):
    # 1. 筛选指定股票和时间段
    code = df['股票代码'].unique()[0]
    df_filtered = df[(df['交易日期'] >= start_date) &
                     (df['交易日期'] <= end_date)].copy()

    if df_filtered.empty:
        print("无数据：请检查股票代码或日期范围")
        return

    # 2. 格式整理
    df_filtered = df_filtered.sort_values('交易日期')
    df_filtered['交易日期'] = pd.to_datetime(df_filtered['交易日期'])
    df_filtered.set_index('交易日期', inplace=True)

    # 3. 构建K线所需的列名：Open、High、Low、Close、Volume
    df_plot = df_filtered.rename(columns={
        '开盘价': 'Open',
        '最高价': 'High',
        '最低价': 'Low',
        '收盘价': 'Close',
        '成交量': 'Volume'
    })[['Open', 'High', 'Low', 'Close', 'Volume']]

    plt.rcParams['font.family'] = 'Microsoft YaHei'  # 设置中文字体为黑体
    plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

    # 4. 绘图
    mpf.plot(df_plot,
             type='candle',
             style='charles',  # 也可选 'yahoo', 'binance', 'mike'
             title=f"{code} 日K线图 ({start_date} ~ {end_date})",
             ylabel='价格',
             ylabel_lower='成交量',
             volume=True,
             mav=(5, 10, 20),  # 可选：添加均线
             figratio=(12, 6),
             tight_layout=True,
             show_nontrading=False)

def is_bowl_pattern(df: pd.DataFrame, start_date: int = None, end_date: int = None) -> bool:
    # 1. 筛选日期
    if end_date is None:
        end_date = df['交易日期'].max()
    if start_date is None:
        start_date = df['交易日期'].min()

    df_filtered = df[(df['交易日期'] >= start_date) & (df['交易日期'] <= end_date)].copy()
    df_filtered = df_filtered.sort_values('交易日期')

    if len(df_filtered) < 10:
        return False

    close_prices = df_filtered['收盘价'].values
    volumes = df_filtered['成交量'].values
    n = len(close_prices)

    # 2. 找最低点
    min_index = np.argmin(close_prices)

    # 2.1 最低点靠近最近3分之一（更偏右）
    if not (n * 2/3 < min_index < n - 2):
        return False

    # 3. 前后段线性趋势
    x1 = np.arange(min_index).reshape(-1, 1)
    y1 = close_prices[:min_index].reshape(-1, 1)
    x2 = np.arange(n - min_index).reshape(-1, 1)
    y2 = close_prices[min_index:].reshape(-1, 1)

    model1 = LinearRegression().fit(x1, y1)
    model2 = LinearRegression().fit(x2, y2)

    slope1 = model1.coef_[0][0]
    slope2 = model2.coef_[0][0]

    if slope1 >= -0.01 or slope2 <= 0.01:
        return False

    # 4. 振幅判断（排除横盘）
    amplitude = (np.max(close_prices) - np.min(close_prices)) / np.min(close_prices)
    if amplitude < 0.1:
        return False

    # 5. 左右段高点对比（右侧不能高于左侧）
    left_max = np.max(close_prices[:min_index])
    right_max = np.max(close_prices[min_index:])
    if right_max > left_max * 1.03:  # 给个3%容忍空间
        return False

    # 6. 成交量是否逐渐放大（后1/3平均量 > 前1/3平均量）
    left_vol_avg = np.mean(volumes[:n // 3])
    right_vol_avg = np.mean(volumes[-n // 3:])
    if right_vol_avg < left_vol_avg * 1.2:  # 后段成交量需至少放大20%
        return False

    return True
