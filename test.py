#输出今日日期的YYMMDDDD字符串
# import datetime
# print(datetime.date.today().strftime('%Y%m%d'))
import pandas as pd
df = pd.read_csv(r'C:\Users\24645\Desktop\量化\数据源csv\日线数据\000001.SZ.csv')
#输出df每一列的类型
print(df.dtypes)