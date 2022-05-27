import sqlite3 as sq
import pprint as pp

DB_Connection = sq.connect("AlgoData.db")
DB_Cursor = DB_Connection.cursor()

cursor = DB_Connection.cursor()


def CreateTimesaleTable(Ticker):
    
    TableName = Ticker.replace("/", "")
    TableName += "Timesales"
    
    Query = "CREATE TABLE IF NOT EXISTS " + TableName + "( Ticker TEXT NOT NULL, TradeTime TEXT NOT NULL, TradePrice FLOAT NOT NULL, TradeVolume FLOAT NOT NULL);"
    cursor.execute(Query)


def InsertIntoTimesaleTable(Ticker, Time, Price, Volume):
    
    TableName = Ticker.replace("/", "")
    TableName += "Timesales"
    
    Query = "INSERT INTO " + TableName + "(Ticker, TradeTime, TradePrice, TradeVolume) VALUES ('" + str(Ticker) + "', '" + str(Time) + "', " + str(Price) +  ", " +  str(Volume) + ");"
    cursor.execute(Query)


def CreateCandlestickTable(TimesaleTable):
    return None


def PrintTimesales(Ticker):
    
    TableName = Ticker.replace("/", "")
    TableName += "Timesales"
    
    Query = "SELECT * FROM " + TableName
    cursor.execute(Query)
    pp.pprint(cursor.fetchall())