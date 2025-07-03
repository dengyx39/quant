import tushare as ts
import pandas as pd
import os
from fetch import *

# ========== 初始化配置 ==========
# 路径配置（使用绝对路径避免相对路径问题）
base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, "..", "数据源csv", "周线数据")
os.makedirs(output_dir, exist_ok=True)  # 自动创建目录

# Tushare初始化
token = get_token()
pro = ts.pro_api(token)

# 参数配置
buy_KCB_CYB = False  # 是否排除科创板/创业板
start_date = "20180701"
stock_list_path = os.path.join(base_dir, "..", "数据源csv", "股票列表.csv")

# ========== 数据处理 ==========
# 读取股票列表
try:
    data = pd.read_csv(stock_list_path)
    index = data["ts_code"].tolist()
except FileNotFoundError:
    raise FileNotFoundError(f"股票列表文件未找到，请检查路径: {stock_list_path}")

# 周线数据列名映射（根据Tushare官方文档调整）
week_column_mapping = {
    'ts_code': '股票代码',
    'trade_date': '交易日期',
    'open': '开盘价',
    'high': '最高价',
    'low': '最低价',
    'close': '收盘价',  # 周线数据中字段名是'close'而非'close_x'
    'pre_close': '昨收价',
    'change': '涨跌额',
    'pct_chg': '涨跌幅',
    'vol': '成交量',
    'amount': '成交额（千元）'
    # 其他财务指标字段根据实际需求添加
}

# ========== 主循环 ==========
for code in index:
    # 跳过科创板/创业板股票（688/300/301开头）
    if not buy_KCB_CYB:
        if code.startswith(('688', '300', '301')):
            continue

    try:
        print(f"正在处理: {code}")

        # 获取周线数据（后复权）
        df_week = pro.stk_week_month_adj(
            ts_code=code,
            freq='W',  # 周线频率
            start_date=start_date,
            adj='hfq'  # 后复权
        )

        if df_week.empty:
            print(f"警告: {code} 无周线数据，已跳过")
            continue

        # 数据处理
        df_week.rename(columns=week_column_mapping, inplace=True)

        # 保存文件
        output_path = os.path.join(output_dir, f"{code}.csv")
        df_week.to_csv(output_path, index=False, encoding='utf-8-sig')

    except Exception as e:
        print(f"处理 {code} 时出错: {str(e)}")
        continue

print("所有股票周线数据处理完成！")