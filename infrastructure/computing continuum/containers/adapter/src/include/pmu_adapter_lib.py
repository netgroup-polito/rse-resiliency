import logging
from sys import stdout
import paho.mqtt.client as mqtt

from synchrophasor.pdc import Pdc
from synchrophasor.pdc import PdcError
from synchrophasor.frame import *
from threading import Thread


class PmuAdapter:

    def __init__(self, pdc_id=1, pmu_ip="127.0.0.1", pmu_port=4712,
                 mqttbroker_ip="127.0.0.1", mqttbroker_port=1883, mqtt_qos=1, logging_level=logging.WARNING):
        # Set-up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging_level)
        handler = logging.StreamHandler(stdout)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.pdc = Pdc(pdc_id, pmu_ip, pmu_port)
        self.pdc.logger.setLevel(logging_level)
        self.mqttbroker_ip = mqttbroker_ip
        self.mqttbroker_port = mqttbroker_port
        self.mqtt_qos = mqtt_qos

        # Set-up mqtt client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.__on_mqtt_connect
        self.mqtt_client.on_disconnect = self.__on_mqtt_disconnect
        self.mqtt_loop = None

    def __pmu_connect(self):
        if not self.pdc.run():
            raise PdcError("Unable to connect to the PMU")

    def __on_mqtt_disconnect(self, client, userdata, rc):
        self.logger.warning("Connection with mqtt broker lost, retrying connection...")

    def __on_mqtt_connect(self, client, userdata, flags, rc):
        self.logger.info(f"Connected to mqtt broker {self.mqttbroker_ip} on port {self.mqttbroker_port}")

    def __publish_config(self, config):
        self.mqtt_topic = f"pmu_data/pmu-{config.get_id_code()}"
        self.mqtt_client.publish(self.mqtt_topic, config.convert2bytes(), self.mqtt_qos, retain=True)

    def connect(self):
        # Connect to PMU
        self.__pmu_connect()

        # Connect to the mqtt server
        self.mqtt_client.connect(self.mqttbroker_ip, self.mqttbroker_port)
        # Handle mqtt netwoork loop in a separate thread in order to avoid a blocking loop
        self.mqtt_loop = Thread(target=self.mqtt_client.loop_forever)
        # Stop thread on main program exit
        self.mqtt_loop.daemon = True
        self.mqtt_loop.start()

        # Request the pmu config and send it to the broker with retain mode
        # so that PDCs can receive it as soon as they connect to the PMU topic
        config = self.pdc.get_config()
        self.__publish_config(config)

    def start(self):
        if not self.mqtt_loop:
            self.connect()

        self.pdc.start()
        while True:
            # Receive data
            data = self.pdc.get()

            if type(data) == DataFrame:
                self.mqtt_client.publish(self.mqtt_topic, data.convert2bytes(), self.mqtt_qos)
                self.logger.debug(data.get_measurements())
            elif type(data) == ConfigFrame2:
                self.__publish_config(data)

