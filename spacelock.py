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
mqtt_client.connect('putin')
mqtt_client.subscribe('space/status/door')

LAST_LOCK_ERROR = False


def telnet(txt):
    try:
        telnet = telnetlib.Telnet('192.168.21.148')
    except:
        logging.error('Cannot connect to display, make sure it is on the network with IP 192.168.21.148')
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
    if msg.topic == opentopic:
        payload = msg.payload.decode('utf8')
        if payload == 'lock':
            if is_open():
                display_text(client, 'WARNUNG - Tuer abgeschlossen, Space war offen.')
                client.publish('space/status/error', 'Tuer wurde abgeschlossen, doch der Space war offen!')
                LAST_LOCK_ERROR = True
            else:
                display_text(client, 'Door locked. Wer das liest ist eingeschlossen.')
        elif payload == 'unlock':
            if LAST_LOCK_ERROR:
                display_text(client, 'WARNUNG: Door unlocked! Space war beim abschliessen noch offen!')
                LAST_LOCK_ERROR = False
            else:
                display_text(client, 'Door unlocked! Ggf. Spaceschalter bedienen und Zeit einstellen!')

mqtt_client.on_message = mqtt_received
mqtt_client.loop_start()


while True:
    time.sleep(5)

