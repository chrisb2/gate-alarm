# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
import gc
import network
from utime import ticks_ms, ticks_diff
import secrets

start = ticks_ms()

print('Connecting to network...')

ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

sta_if = network.WLAN(network.STA_IF)
sta_if.connect(secrets.WIFI_SSID, secrets.WIFI_PASSPHRASE)
while not sta_if.isconnected():
    pass

print('Network, address: %s in %d ms' %
      (sta_if.ifconfig()[0], ticks_diff(ticks_ms(), start)))

gc.collect()
