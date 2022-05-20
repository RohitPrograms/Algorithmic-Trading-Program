from dataclasses import dataclass

from Authenticate import * 
from Data import *

import numpy as np
import pandas as pd
import datetime as dt
import pandas_ta as ta
import pprint as pp



@dataclass
class Signals():
    
    Ticker: str
    all_signals: pd.DataFrame
    
for stock in ALL_PRICE_DATA:
    print(stock.ticker)