from mqtt_as import MQTTClient
import uasyncio as asyncio
import ubinascii
from machine import Pin, PWM, unique_id
import urequests
import secrets
import topic

CLIENT_ID = ubinascii.hexlify(unique_id())
MQTTClient.DEBUG = True  # Optional: print diagnostic messages

# Pin constants
_BUZZER = 14  # GPIO14, D5
_LED1 = 16    # GPIO16, D0, Nodemcu led
_LED2 = 2     # GPIO2, D4, ESP8266 led

THINGSPEAK_URL = "https://api.thingspeak.com/update?api_key={}&{}"
IFTTT_URL = "https://maker.ifttt.com/trigger/gate/with/key/{}"

loop = asyncio.get_event_loop()
blue_led = Pin(_LED2, Pin.OUT, value=1)
live_led = Pin(_LED1, Pin.OUT, value=1)


def run_base():
    client = MQTTClient(mqtt_config, CLIENT_ID, secrets.MQTT_BROKER)
    try:
        loop.create_task(alive_signal())
        loop.run_until_complete(main(client))
    finally:
        client.close()  # Prevent LmacRxBlk:1 errors


async def alive_signal():
    while True:
        live_led(False)
        await asyncio.sleep_ms(50)
        live_led(True)
        await asyncio.sleep(5)


async def signal_alarm():
    blue_led(False)
    await asyncio.sleep(1)
    blue_led(True)


async def raise_alarm(msg):
    send_to_ifttt()
    await asyncio.sleep_ms(100)
    send_to_thingspeak(msg)


def callback(topic, msg):
    msg_str = msg.decode('ascii').strip()
    loop.create_task(signal_alarm())
    loop.create_task(raise_alarm(msg_str))
    loop.create_task(sound_alarm())


async def conn_han(client):
    await client.subscribe(topic.GATE_STATUS)


async def main(client):
    await client.connect()
    while True:
        await asyncio.sleep(5)


def send_to_thingspeak(msg):
    url = THINGSPEAK_URL.format(secrets.THINGSPEAK_API_KEY, msg)
    http_get(url)


def send_to_ifttt():
    url = IFTTT_URL.format(secrets.IFTTT_API_KEY)
    http_get(url)


def http_get(url):
    try:
        req = urequests.get(url)
        req.close()
    except Exception as e:
        # Ignore so that program continues running
        print('HTTP get failed', e)


async def sound_alarm():
    pwm = PWM(Pin(_BUZZER), freq=500, duty=512)
    await asyncio.sleep(5)
    pwm.deinit()


mqtt_config = {
    'subs_cb': callback,
    'connect_coro': conn_han,
}
