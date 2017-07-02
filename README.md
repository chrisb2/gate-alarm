# Gate alarm based on Nodemcu (ESP8266)

This project uses two Nodemcu clones which communicate via MQTT. One is battery
powered and attached to the gate and the other is a mains powered base station
which has an audible and visual alarm.

The base station uses MQTT to publish the gate status to ThingSpeak, so gate
alarms can also be picked up on a Mobile phone.
