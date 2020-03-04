from tehran_stocks.config import *
from sqlalchemy.orm import relationship
import pandas as pd


class Stocks(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    title = Column(String)
    group_name = Column(String)
    group_code = Column(Integer)
    instId = Column(String)
    insCode = Column(String)
    code = Column(String, unique=True)
    sectorPe = Column(Float)
    shareCount = Column(Float)
    estimatedEps = Column(Float)
    baseVol = Column(Float)
    prices = relationship("StockPrice", backref="stock")
    _cached = False
    _dfcounter = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def df(self):
        self._dfcounter += 1
        if self._cached:
            return self._df
        query = "select * from stock_price where code = {}".format((self.code))
        df = pd.read_sql(query, engine)
        if df.empty:
            self._cached = True
            self._df = df
            return self._df
        df["date"] = pd.to_datetime(df["dtyyyymmdd"], format="%Y%m%d")
        df = df.sort_values("date")
        df.reset_index(drop=True, inplace=True)
        df.set_index("date", inplace=True)
        self._cached = True
        self._df = df
        return self._df

    @property
    def mpl(self):
        self._mpl = self.df.rename(columns={
                                   "close": "Close", "open": "Open", "high": "High", "low": "Low", "vol": "Volume"})
        return self._mpl

    def update(self):
        from tehran_stocks.download import update_stock_price

        try:
            res = update_stock_price(self.code)
            return res
        except:
            return False

    def summary(self):
        df = self.df
        sdate = df.date.min().strftime("%Y%m%d")
        edate = df.date.max().strftime("%Y%m%d")

        print("Start date: {}".format((sdate)))
        print("End date: {}".format((edate)))
        print("Total days: {}".format((len(df))))

    def __repr__(self):
        return "{}-{}-{}".format((self.title), (self.name), (self.group_name))

    def __str__(self):
        return self.name

    @staticmethod
    def get_group():
        codes = (
            session.query(Stocks.group_code, Stocks.group_name)
            .group_by(Stocks.group_code)
            .all()
        )
        return codes


class StockPrice(Base):
    __tablename__ = "stock_price"

    id = Column(Integer, primary_key=True)
    code = Column(String, ForeignKey("stocks.code"), index=True)
    ticker = Column(String)
    date = Column("dtyyyymmdd", Integer, index=True)
    first = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    value = Column(Integer)
    vol = Column(Integer)
    openint = Column(Integer)
    per = Column(String)
    open = Column(Float)
    last = Column(Float)

    def __repr__(self):
        return "{}, {}, {:.0f}".format((self.stock.name), (self.date), (self.close))


def get_asset(name):
    asset = Stocks.query.filter_by(name=name).first()
    return asset
