from utime import ticks_ms, ticks_diff, sleep_ms
import gc
import webrepl
from mqtt import MQTTClient
from machine import Pin, ADC
import secrets

# Pin constants
LED1 = 16    # GPIO16, D0, Nodemcu led
LED2 = 2     # GPIO2, D4, ESP8266 led
SWITCH = 0   # GPIO0, D3
BATTERY = 0  # ADC0, A0

PAYLOAD_FORMAT = "field1=1&field2={:d}&field3={:d}\n"

on_for_update = False


def device_control(topic, msg):
    global on_for_update
    on_for_update = True
    print((topic, msg))


def run():
    global on_for_update
    start = ticks_ms()

    c = MQTTClient("umqtt_client", secrets.MQTT_BROKER)
    c.set_callback(device_control)
    c.connect(clean_session=False)
    c.publish(b"back-gate/status", msg_payload())
    c.subscribe(b"back-gate/update", qos=1)
    c.check_msg()
    c.disconnect()

    print("Message took %d ms" % ticks_diff(ticks_ms(), start))
    flash_led(LED1)

    if not on_for_update:
        switch_off()

    webrepl.start()


def msg_payload():
    return PAYLOAD_FORMAT.format(battery_mv(), gc.mem_free())


def battery_mv():
    # ADC read at pin A0
    adc = ADC(BATTERY)
    return adc.read()


def switch_off():
    # Raise pin high to signal FET switch to turn off
    flash_led(LED2)
    pin = Pin(SWITCH, Pin.OUT)
    pin.on()


def flash_led(pin, count=1):
    pin = Pin(pin, Pin.OUT)
    pin.on()
    for x in range(0, count * 2):
        pin.value(not pin.value())
        sleep_ms(100)
