# main.py
import time
import lgpio
from TCRT_5000 import TCRT5000, read

h = lgpio.gpiochip_open(0)

L = TCRT5000(h, 6)
R = TCRT5000(h, 5)

try:
    while True:
        print(read(h, L), read(h, R))
        time.sleep(0.05)
finally:
    lgpio.gpiochip_close(h)
