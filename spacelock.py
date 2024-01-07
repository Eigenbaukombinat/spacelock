from ebk_status import is_open
import logging
import paho.mqtt.client as mqtt
import time

import argparse
parser = argparse.ArgumentParser(description='EBK space api status')
parser.add_argument('--mqtt_broker', dest='mqtt_broker', default='localhost', help='Hostname/IP of the mqtt server (default:localhost).')
config = parser.parse_args()

logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s '
                        '%(levelname)s %(message)s')
log = logging.getLogger(__name__)


mqtt_client = mqtt.Client()
mqtt_client.enable_logger(logger=log)
mqtt_client.connect(config.mqtt_broker)
mqtt_client.subscribe('space/status/door')

LAST_LOCK_ERROR = False


def display_text(client, text):
    client.publish('display/ledlaufschrift/text', text)

def mqtt_received(client, data, msg):
    global LAST_LOCK_ERROR
    doortopic = 'space/status/door'
    if msg.topic == doortopic:
        payload = msg.payload.decode('utf8')
        if payload == 'lock':
            if is_open():
                display_text(client, 'Tuer abgeschlossen, Space war offen.') # max 40 Zeichen
                client.publish('space/status/error', 'Tuer wurde abgeschlossen, doch der Space war offen!')
                LAST_LOCK_ERROR = True
            else:
                display_text(client, 'Tuer zu.Wer das liest ist eingeschlossen') #max 40 Zeichen
                client.publish('space/bernd/speak/msg', 'Tür abgeschlossen, späis ist zu.')
        elif payload == 'unlock':
            if LAST_LOCK_ERROR:
                display_text(client, 'Tuer auf!Space b abschliessen offen') # max 40 Zeichen
                LAST_LOCK_ERROR = False
            else:
                display_text(client, 'Tuer auf!Spaceschalter u Zeit bedienen!') # max 40 Zeichen
                client.publish('space/bernd/speak/msg', 'Tür aufgeschlossen, gegebenenfalls den Schalter bedienen und die Zeit einstellen.')

mqtt_client.on_message = mqtt_received
mqtt_client.loop_start()


while True:
    time.sleep(5)

