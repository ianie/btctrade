from time import ctime
import btctrade.config
from btctrade.config import logFile, warningFile

def logWrite(entry, logType=None):
    s = ctime() + ': ' + entry
    print(s)
    if btctrade.config.apprun:
        with open(logFile, 'a') as f:
            f.write(s + '\n')
        if logType == 'warning':
            with open(warningFile, 'a') as f:
                f.write(s + '\n')