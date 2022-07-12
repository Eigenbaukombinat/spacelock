from ebk_status import is_open
import logging
import paho.mqtt.client as mqtt
import time
import telnetlib

logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s '
                        '%(levelname)s %(message)s')
log = logging.getLogger(__name__)


mqtt_client = mqtt.Client()
mqtt_client.enable_logger(logger=log)
mqtt_client.connect('localhost')
mqtt_client.subscribe('space/status/door')

LAST_LOCK_ERROR = False


def telnet(txt):
    try:
        telnet = telnetlib.Telnet('vfddisplay.lan')
    except:
        logging.error('Cannot connect to display, make sure it is on the network with vfddisplay.lan')
        return
    telnet.write('\n\n'.encode('latin1'))
    telnet.write(chr(0x0D).encode('latin1')) #0x0D clear; 0x0F All Display; 0x0B scroll; 
    telnet.write(chr(0x10).encode('latin1'))  ##Displayposition   0x10  
    telnet.write(chr(0).encode('latin1'))    ##Position
    telnet.write(txt.encode('latin1'))


def display_text(client, text):
    telnet(text)
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

