from time import sleep

from btctrade.collectdata import Bitfinex
b = Bitfinex()
try:
    b = Bitfinex()
    b.start()
    while(True):
        sleep(60)
finally:
    b.stop()
    b.join()
    print("main finishsed")
