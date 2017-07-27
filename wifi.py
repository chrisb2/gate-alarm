import network
from utime import ticks_ms, ticks_diff, sleep
import secrets

MAX_RETRIES = 10


def connect():
    retries = 0
    start = ticks_ms()

    print('Connecting to network...')

    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)

    sta_if = network.WLAN(network.STA_IF)
    sta_if.connect(secrets.WIFI_SSID, secrets.WIFI_PASSPHRASE)
    while not sta_if.isconnected() and retries < MAX_RETRIES:
        # Limit network access retries
        retries += 1
        sleep(1)

    if sta_if.isconnected():
        print('Network, address: %s in %d ms' %
              (sta_if.ifconfig()[0], ticks_diff(ticks_ms(), start)))
