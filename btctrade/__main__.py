from time import sleep

from btctrade.collectdata import BitFinex
b = BitFinex()
try:
    b = BitFinex()
    b.start()
    while(True):
        sleep(60)
finally:
    b.stop()
    b.join()
    print("main finishsed")
