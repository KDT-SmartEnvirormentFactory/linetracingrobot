# TCRT_5000.py
import lgpio

def TCRT5000(h, gpio):
    lgpio.gpio_claim_input(h, gpio, lgpio.SET_PULL_UP)
    return gpio

def read(h, gpio):
    return int(lgpio.gpio_read(h, gpio))
