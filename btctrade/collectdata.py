from pprint import pprint
import threading
import sqlite3
import btctrade.config
from btctrade.util import logWrite
from btctrade.config import dbFile
from time import time, sleep
import requests

retentionLength = 60*60*24*30 # 30 days

class Exchange(threading.Thread):
    def __init__(self, name, url, interval, dbWrite):
        super(Exchange, self).__init__(name=name)
        self.url = url
        self.interval = interval
        self._stop = threading.Event()
        self.db = None
        self.dbWrite = dbWrite

    def updateDb(self):
        raise NotImplementedError

    def initDb(self, db=None):
        if not db:
            db = self.db
        t = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (self.__class__.__name__,)).fetchall()
        if not t:
            db.execute("CREATE TABLE %s (id INTEGER UNIQUE, time INTEGER, price REAL, amount REAL, type INTEGER)" %
                self.__class__.__name__)

    def clearDb(self):
        # Clear the expired history
        timeThresh = int(time()) - retentionLength
        try:
            with self.db:
                self.db.execute('DELETE FROM %s WHERE time<?' % self.name, (timeThresh,))
        except Exception as e:
            logWrite("Error cleaning history", 'warning')
            logWrite(repr(e), 'warning')

    def run(self):
        try:
            self.db = sqlite3.connect(dbFile)
            self.initDb()
            btctrade.config.apprun = True
            logWrite("Starting %s collectdata" % self.name)
            while not self._stop.is_set():
                self.updateDb()
                self.clearDb()
                self._stop.wait(timeout=self.interval)
            logWrite("Closing %s collectdata" % self.name)
        finally:
            if self.db:
                self.db.close()
            logWrite("Finished")

    def stop(self):
        self._stop.set()


class BitFinex(Exchange):
    def __init__(self, dbWrite=True):
        url = 'https://api.bitfinex.com/v1/trades/btcusd'
        interval = 10
        name = self.__class__.__name__
        self.bestSeenTime = 0
        self.maxTrades = 2000
        self.tradeTypes = {'buy': 1, 'sell': 0}
        self.prevTrades = []
        super(BitFinex, self).__init__(name, url, interval, dbWrite)

    def updateDb(self):
        try:
            r = requests.get(self.url, params={
                "limit_trades": self.maxTrades, "timestamp": self.bestSeenTime})
            trades = r.json()
        except Exception as e:
            logWrite(str(e))
            return
        
        pastTradesId = [trade['tid'] for trade in self.prevTrades]
        newTrades =  [trade for trade in trades if not trade['tid'] in pastTradesId]       
        numNewTrades = len(newTrades)
        
        if numNewTrades:
            self.bestSeenTime = max([trade['timestamp'] for trade in newTrades])
            self.prevTrades = newTrades

        logWrite("%d new trades" % numNewTrades)

        pprint(newTrades)

        if self.dbWrite:
            try:
                with self.db:
                    self.db.executemany('INSERT INTO %s VALUES (?, ?, ?, ?, ?)' % self.name,
                        [(
                            trade['tid'],
                            trade['timestamp'],
                            trade['price'],
                            trade['amount'],
                            self.tradeTypes[trade['type']]
                        ) for trade in newTrades])
            except sqlite3.IntegrityError:
                numWrites = 0
                for trade in trades:
                    try:
                        with self.db:
                            self.db.execute('INSERT INTO %s VALUES (?, ?, ?, ?, ?)' % self.name,
                                (
                                    trade['tid'],
                                    trade['timestamp'],
                                    trade['price'],
                                    trade['amount'],
                                    self.tradeTypes[trade['type']]
                                ))
                    except sqlite3.IntegrityError:
                        pass
                    except Exception as e:
                        logWrite(repr(e))
                    else:
                        numWrites += 1
            else:
                numWrites = numNewTrades
            if numWrites != numNewTrades:
                logWrite("Warning: only %d writes." % numWrites, 'warning')






        