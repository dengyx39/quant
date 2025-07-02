import tushare as ts
from datetime import datetime

def get_token():
    token = '31e5536e4d0ffbfb47a74e9832fd35c711fdaa2405bec6559b62d22d'
    return token

token = get_token()
pro = ts.pro_api(token)

# 获取上一个交易日
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