from utime import sleep_ms
import webrepl
from mqtt import MQTTClient
from machine import Pin, ADC
import topic
import secrets

# Pin constants
LED1 = 16    # GPIO16, D0, Nodemcu led
LED2 = 2     # GPIO2, D4, ESP8266 led
SWITCH = 5   # GPIO5, D1
BATTERY = 0  # ADC0, A0

# Resistors in voltage divider (ohms)
# NodeMcu internal resister divider (from schematic)
NODEMCU_RESISTOR_RATIO = (220 + 100) / 100
# External resister divider
R1 = 9970
R2 = 9990
RESISTOR_RATIO = (R1 + R2) / R2

# ADC Reference voltage in Millivolts
ADC_REF = 1000
# Average value from 100 reads when A0 is grounded
ADC_OFFSET = 3
# Number of ADC reads to take average of
ADC_READS = 30

PAYLOAD_FORMAT = "field1=1&field2={0:.2f}\n"

on_for_update = False


def device_control(topic, msg):
    global on_for_update
    on_for_update = True
    print((topic, msg))


def run_gate():
    global on_for_update

    c = MQTTClient("gate_client", secrets.MQTT_BROKER)
    c.set_callback(device_control)
    c.connect(clean_session=False)
    c.publish(topic.GATE_STATUS, msg_payload())
    c.subscribe(topic.GATE_UPDATE, qos=1)
    c.check_msg()
    c.disconnect()

    flash_led(LED1)

    if not on_for_update:
        switch_off()

    webrepl.start()


def msg_payload():
    return PAYLOAD_FORMAT.format(battery_voltage()).encode('ascii')


def battery_voltage():
    # ADC read at pin A0
    adc = ADC(BATTERY)
    sum = 0
    for x in range(0, ADC_READS):
        sum += adc.read()
    return ADC_REF * NODEMCU_RESISTOR_RATIO * RESISTOR_RATIO * \
        (sum / ADC_READS - ADC_OFFSET) / 1024 / 1000


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
