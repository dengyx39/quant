import tushare as ts
import pandas as pd
from torch.mps.profiler import start

import config
from pattern import *
import numpy as np
from arch import arch_model
import matplotlib.pyplot as plt
import seaborn as sns
import os

path = r"C:\Users\24645\Desktop\量化\数据源csv\日线数据"
ls = []
count = 0
for filename in os.listdir(path):
    df = pd.read_csv(path + '/' + filename, encoding='utf-8')
    start_date, end_date = 20250427, df['交易日期'].max()
    if is_bowl_pattern(df,start_date, end_date):
        ls.append(filename)
        plot_kline(df, start_date, end_date)
        count+=1
    if count > 5:break

