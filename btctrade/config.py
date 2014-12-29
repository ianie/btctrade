import os

apprun = False


dbFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/trades.db")
logFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/debug.log")
warningFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/warnings.log")