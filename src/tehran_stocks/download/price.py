import re
import time

import pandas as pd
import requests

import tehran_stocks.config as db
from tehran_stocks.models import StockPrice, Stocks


def update_stock_price(code: str):
    """
    Update (or download for the first time) Stock prices


    params:
    ----------------
    code: str or intege

    example
    ----------------
    `update_stock_price('44891482026867833') #Done`
    or use inside Stock object
    ```
    from tehran_stocks.models import Stocks
    stock = Stocks.query.first()
    stock.update() #Done
    """
    try:
        q = "select dtyyyymmdd as date from stock_price where code = {}".format(
            (code))
        temp = pd.read_sql(q, db.engine)
        url = "http://www.tsetmc.com/tsev2/data/Export-txt.aspx?t=i&a=1&b=0&i={}"
        df = pd.read_csv(url.format(code))
        df.columns = [i[1:-1].lower() for i in df.columns]
        df["code"] = code
        df = df[~df.dtyyyymmdd.isin(temp.date)]
        df.to_sql("stock_price", db.engine, if_exists="append", index=False)
        return True, code
    except Exception as e:
        return e, code


def update_group(code):
    """
    Update and download data of all stocks in  a group.\n

    `Warning: Stock table should be updated`
    """
    stocks = db.session.query(Stocks.code).filter_by(group_code=code).all()
    if not stocks:
        print("Make sure group has some entity on Stocks")
        return
    for i, stock in enumerate(stocks):
        update_stock_price(stock[0])
        print("group progress: {:.1f}%".format(
            (100*(i+1)/len(stocks))), end="\r")


def get_all_price():
    codes = db.session.query(db.distinct(Stocks.group_code)).all()
    for i, code in enumerate(codes):
        print("                         total progress: {:.2f}%".format(
            (100*(i+1)/len(codes))), end="\r")
        update_group(code[0])

    print("Download Finished.")
