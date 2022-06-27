from asyncio.windows_events import NULL
import Price
import datetime as dt

#------------------------------------------------------------------------------------------

# Returns the True Range for the given ticker at the given trade time
# This is used to caluclate the ATR

def TrueRange(Ticker: str, Trade_Time: dt.datetime):
    
    CurrentCandle = Price.OHLCV(Ticker, Trade_Time)
    PreviousCandle = Price.OHLCV(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL))
    
    if (CurrentCandle != None) and (PreviousCandle != None):
        
        val1 = CurrentCandle["High"] - CurrentCandle["Low"]
        val2 = abs(CurrentCandle["High"] - PreviousCandle["Close"])
        val3 = abs(CurrentCandle["Low"] - PreviousCandle["Close"])
        
        return max([val1, val2, val3])
    
    return NULL

#------------------------------------------------------------------------------------------

# Calculates the ATR for a given ticker at the given time.
# Used to determine the value of the DI+ and DI- 

def ATR(Ticker: str, Trade_Time: dt.datetime, Period: float):
    
    if(TrueRange(Ticker, Trade_Time - dt.timedelta( minutes = ((Period - 1) * Price.CANDLESTICK_INTERVAL))) != NULL):
        
        ATR = 0.0
        
        for i in range (0, Period):
            
            ATR += TrueRange(Ticker, Trade_Time - dt.timedelta( minutes = (i * Price.CANDLESTICK_INTERVAL))) / Period
        
        return ATR
    
    return NULL

#------------------------------------------------------------------------------------------

# Calculates the DM+ for the given ticker and time
# Used to calculate the DI+ and DI-

def PlusDM(Ticker: str, Trade_Time: dt.datetime):
    
    CurrentCandle = Price.OHLCV(Ticker, Trade_Time)
    PreviousCandle = Price.OHLCV(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL))
    
    if (CurrentCandle != None) and (PreviousCandle != None):
        
        PlusDM = CurrentCandle["High"] - PreviousCandle["High"]
        MinusDM = PreviousCandle["Low"] - CurrentCandle["Low"]
        
        if (PlusDM > MinusDM):
            return max([PlusDM, 0.0])
        
        return 0.0
    
    return NULL

#------------------------------------------------------------------------------------------

# Calculates the DM- for the given ticker and time
# Used to calculate the DI+ and DI-

def MinusDM(Ticker: str, Trade_Time: dt.datetime):
    
    CurrentCandle = Price.OHLCV(Ticker, Trade_Time)
    PreviousCandle = Price.OHLCV(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL))
    
    if (CurrentCandle != None) and (PreviousCandle != None):
        
        PlusDM = CurrentCandle["High"] - PreviousCandle["High"]
        MinusDM = PreviousCandle["Low"] - CurrentCandle["Low"]
        
        if (MinusDM > PlusDM):
            return max([MinusDM, 0.0])
        
        return 0.0
    
    return NULL

#------------------------------------------------------------------------------------------

# Calculates the DI- for the given ticker and time
# An essential indicator used to produce buy and sell signals for this strategy
# The DI+ also helps us calculate the ADX

def PlusDI(Ticker: str, Trade_Time: dt.datetime, Period: float):
    
    CurrentATR = ATR(Ticker, Trade_Time, Period)
    
    if (CurrentATR != NULL):
        
        DMIPlus = 0.0
        
        for i in range (0, Period):
            
            DMIPlus += PlusDM(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL * i)) / Period
        
        return DMIPlus * 100 / CurrentATR
    
    return NULL

#------------------------------------------------------------------------------------------

# Calculates the DI- for the given ticker and time
# An essential indicator used to produce buy and sell signals for this strategy
# The DI- also helps us calculate the ADX

def MinusDI(Ticker: str, Trade_Time: dt.datetime, Period: float):
    
    CurrentATR = ATR(Ticker, Trade_Time, Period)
    
    if (CurrentATR != NULL):
        
        DMIMinus = 0.0
        
        
        for i in range (0, Period):
            
            DMIMinus += MinusDM(Ticker, Trade_Time - dt.timedelta(minutes = Price.CANDLESTICK_INTERVAL * i)) / Period
        
        return DMIMinus * 100 / CurrentATR
    
    return NULL

#------------------------------------------------------------------------------------------

# Calculates the ADX for the given ticker and time
# An essential indicator used to produce buy and sell signals for this strategy

def ADX(Ticker: str, Trade_Time: dt.datetime, Period: float):
    
    if(PlusDI(Ticker, Trade_Time - dt.timedelta(minutes = ((Period - 1) * Price.CANDLESTICK_INTERVAL)), Period) != NULL):
        
        ADX = 0.0
        
        for i in range (0, Period):
            
            tempPlusDI = PlusDI(Ticker, Trade_Time - dt.timedelta(minutes = (i * Price.CANDLESTICK_INTERVAL)), Period)
            tempMinusDI = MinusDI(Ticker, Trade_Time - dt.timedelta(minutes = (i * Price.CANDLESTICK_INTERVAL)), Period)
            
            if (tempPlusDI == 0) and (tempMinusDI == 0):
                ADX += 0
                
            else: 
                ADX += (1 / Period) * abs(tempPlusDI - tempMinusDI) / abs(tempPlusDI + tempMinusDI)
        
        return 100 * ADX
    
    return NULL