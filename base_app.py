from mqtt import MQTTClient
from machine import Pin, PWM
from utime import sleep, sleep_ms
import urequests
import topic
import secrets

# Pin constants
BUZZER = 14  # GPIO14, D5
LED2 = 2     # GPIO2, D4, ESP8266 led

REQUEST_FORMAT = "https://api.thingspeak.com/update?api_key={}&{}"


def gate_alarm(topic, msg):
    flash_led(LED2)
    send_to_thingspeak(msg.decode('ascii').strip())
    sound_alarm()


def run_base():
    mqtt_client = MQTTClient("gate_base_client", secrets.MQTT_BROKER)
    mqtt_client.set_callback(gate_alarm)
    _connect_mqtt_session(mqtt_client)
    mqtt_client.subscribe(topic.GATE_STATUS)
    while True:
        try:
            mqtt_client.wait_msg()
        except OSError as e:
            sleep(5)
            _connect_mqtt_session(mqtt_client)


def _connect_mqtt_session(client):
    client.connect(clean_session=False)


def send_to_thingspeak(msg):
    request = REQUEST_FORMAT.format(secrets.THINGSPEAK_API_KEY, msg)
    try:
        urequests.get(request)
    except Exception:
        # Ignore so that program continues running
        pass


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
