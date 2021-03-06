from mqtt_as import MQTTClient
import uasyncio as asyncio
import ubinascii
from machine import Pin, PWM, unique_id
import urequests
import secrets
import topic

_CLIENT_ID = ubinascii.hexlify(unique_id())

# Pin constants
_BUZZER = 14  # GPIO14, D5
_LED1 = 16    # GPIO16, D0, Nodemcu led
_LED2 = 2     # GPIO2, D4, ESP8266 led

_THINGSPEAK_URL = "https://api.thingspeak.com/update?api_key={}&{}"
_IFTTT_URL = "https://maker.ifttt.com/trigger/gate/with/key/{}"

MQTTClient.DEBUG = False  # Optional: print diagnostic messages

loop = asyncio.get_event_loop()
msg_led = Pin(_LED2, Pin.OUT, value=1)
live_led = Pin(_LED1, Pin.OUT, value=1)


def run_base():
    client = MQTTClient(mqtt_config, _CLIENT_ID, secrets.MQTT_BROKER)
    try:
        loop.create_task(signal_alive())
        loop.run_until_complete(main(client))
    finally:
        client.close()  # Prevent LmacRxBlk:1 errors


async def signal_alive():
    while True:
        live_led(False)
        await asyncio.sleep_ms(30)
        live_led(True)
        await asyncio.sleep(5)


async def signal_alarm():
    msg_led(False)
    await asyncio.sleep(1)
    msg_led(True)


async def sound_alarm():
    pwm = PWM(Pin(_BUZZER), freq=500, duty=512)
    await asyncio.sleep(5)
    pwm.deinit()


def callback(topic, msg):
    msg_str = msg.decode('ascii').strip()
    loop.create_task(signal_alarm())
    loop.create_task(send_to_ifttt())
    loop.create_task(send_to_thingspeak(msg_str))
    loop.create_task(sound_alarm())


async def conn_han(client):
    await client.subscribe(topic.GATE_STATUS)


async def main(client):
    await client.connect()
    while True:
        await asyncio.sleep(5)


async def send_to_thingspeak(msg):
    url = _THINGSPEAK_URL.format(secrets.THINGSPEAK_API_KEY, msg)
    await asyncio.sleep(0)
    http_get(url)


async def send_to_ifttt():
    url = _IFTTT_URL.format(secrets.IFTTT_API_KEY)
    await asyncio.sleep(0)
    http_get(url)


def http_get(url):
    try:
        req = urequests.get(url)
        req.close()
    except Exception as e:
        # Ignore so that program continues running
        print('HTTP get failed', e)


mqtt_config = {
    'subs_cb': callback,
    'connect_coro': conn_han,
}
