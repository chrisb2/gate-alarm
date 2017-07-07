from mqtt import MQTTClient
from machine import Pin, PWM
from utime import sleep
import urequests
import topic
import secrets

# Pin constants
BUZZER = 14  # GPIO14, D5

REQUEST_FORMAT = "https://api.thingspeak.com/update?api_key={}&{}"


def gate_alarm(topic, msg):
    print((topic, msg))
    send_to_thingspeak(msg.decode('ascii'))
    sound_alarm()


def run_base():
    c = MQTTClient("gate_base_client", secrets.MQTT_BROKER)
    c.set_callback(gate_alarm)
    c.connect(clean_session=False)
    c.subscribe(topic.GATE_STATUS)
    while True:
        c.wait_msg()


def send_to_thingspeak(msg):
    request = REQUEST_FORMAT.format(secrets.THINGSPEAK_API_KEY, msg)
    urequests.get(request)


def sound_alarm():
    pwm = PWM(Pin(BUZZER), freq=500, duty=512)
    sleep(5)
    pwm.deinit()
