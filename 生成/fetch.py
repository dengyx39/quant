import tushare as ts
from datetime import datetime
import pandas as pd

def get_token():
    token = '31e5536e4d0ffbfb47a74e9832fd35c711fdaa2405bec6559b62d22d'
    return token

token = get_token()
pro = ts.pro_api(token)

def get_prev_trade_date(today=None):
    if today is None:
        today = datetime.today().strftime("%Y%m%d")
    else:
        today = today.strftime("%Y%m%d")

    cal = pro.trade_cal(exchange='SSE', start_date='20200101', end_date=today)
    cal = cal[cal['is_open'] == 1]  # 只保留交易日
    cal = cal[cal['cal_date'] < today]
    prev_date = cal.iloc[0]['cal_date']
    return prev_date

def get_start_end_date(pro, output_path, today=None):
    if today is None:
        today_str = datetime.today().strftime("%Y%m%d")
    else:
        today_str = today.strftime("%Y%m%d")

    # 1. 读取已有CSV最大交易日
    try:
        df_old = pd.read_csv(output_path, usecols=['交易日期'])
        max_date_in_csv = df_old['交易日期'].max()
    except Exception as e:
        print(f"读取已有文件失败或无数据，默认 start_date 从 20220427 开始: {e}")
        max_date_in_csv = '20220427'  # 你可根据情况改默认起始

    # 2. 获取交易日历（包含 today）
    cal = pro.trade_cal(exchange='SSE', start_date='20220427', end_date=today_str)
    cal = cal[cal['is_open'] == 1].sort_values('cal_date').reset_index(drop=True)

    # 3. 找 max_date_in_csv 在交易日历中的位置
    idx = cal[cal['cal_date'] == max_date_in_csv].index
    if len(idx) == 0:
        # csv中的最大日期不在交易日历，取最早交易日为起点
        start_date = cal.iloc[0]['cal_date']
    else:
        idx = idx[0]
        # 取下一个交易日（如果有）
        if idx + 1 < len(cal):
            start_date = cal.iloc[idx + 1]['cal_date']
        else:
            # 已经是最新交易日，不能再往后了，直接用最大日期
            start_date = max_date_in_csv

    # 4. 计算 end_date：今天或之前最近的交易日
    end_cal = cal[cal['cal_date'] <= today_str]
    if len(end_cal) == 0:
        raise ValueError("交易日历中没有今天之前的交易日")
    end_date = end_cal.iloc[-1]['cal_date']

    return start_date, end_date
