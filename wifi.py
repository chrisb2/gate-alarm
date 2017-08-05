import network
from utime import ticks_ms, ticks_diff, sleep
import secrets

WIFI_DELAY = 5


def connect():
    start = ticks_ms()

    print('Connecting to network...')

    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)

    sta_if = network.WLAN(network.STA_IF)
    secs = WIFI_DELAY
    while secs >= 0 and not sta_if.isconnected():
        sleep(1)
        secs -= 1
    if not sta_if.isconnected():
        print('Re-connecting %s ...' % secrets.WIFI_SSID)
        sta_if.connect(secrets.WIFI_SSID, secrets.WIFI_PASSPHRASE)

    if sta_if.isconnected():
        print('Network, address: %s in %d ms' %
              (sta_if.ifconfig()[0], ticks_diff(ticks_ms(), start)))
