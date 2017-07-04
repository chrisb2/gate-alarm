from utime import sleep_ms, sleep
import webrepl
from mqtt import MQTTClient
from machine import Pin, ADC, PWM
import secrets

# Pin constants
LED1 = 16    # GPIO16, D0, Nodemcu led
LED2 = 2     # GPIO2, D4, ESP8266 led
SWITCH = 5   # GPIO5, D1
BATTERY = 0  # ADC0, A0
BUZZER = 14  # GPIO14, D5

# Resistors in voltage divider (ohms)
R1 = 9970
R2 = 994
RESISTOR_RATIO = (R1 + R2) / R2

# ADC Reference voltage in Millivolts
ADC_REF = 3292  # Measured between 3.3V and GND pins
ADC_READS = 30

GATE_STATUS_TOPIC = b"back-gate/status"
GATE_UPDATE_TOPIC = b"back-gate/update"
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
    c.publish(GATE_STATUS_TOPIC, msg_payload())
    c.subscribe(GATE_UPDATE_TOPIC, qos=1)
    c.check_msg()
    c.disconnect()

    flash_led(LED1)

    if not on_for_update:
        switch_off()

    webrepl.start()


def gate_alarm(topic, msg):
    print((topic, msg))
    sound_alarm()


def run_base():
    c = MQTTClient("gate_base_client", secrets.MQTT_BROKER)
    c.set_callback(gate_alarm)
    c.connect(clean_session=False)
    c.subscribe(GATE_STATUS_TOPIC)
    while True:
        c.wait_msg()


def msg_payload():
    return PAYLOAD_FORMAT.format(battery_voltage())


def battery_voltage():
    # ADC read at pin A0
    adc = ADC(BATTERY)
    sum = 0
    for x in range(0, ADC_READS):
        sum += adc.read()
    return ADC_REF * RESISTOR_RATIO * (sum / ADC_READS) / 1024 / 1000


def switch_off():
    # Raise pin high to signal FET switch to turn off
    flash_led(LED2)
    pin = Pin(SWITCH, Pin.OUT)
    pin.on()


def sound_alarm():
    pwm = PWM(Pin(BUZZER), freq=500, duty=512)
    sleep(5)
    pwm.deinit()


def flash_led(pin, count=1):
    pin = Pin(pin, Pin.OUT)
    pin.on()
    for x in range(0, count * 2):
        pin.value(not pin.value())
        sleep_ms(100)
