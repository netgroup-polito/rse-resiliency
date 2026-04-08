import logging
import pickle
from sys import stdout
import paho.mqtt.client as mqtt
import socket as s

from synchrophasor.pdc import PdcError
from synchrophasor.frame import *
from threading import Thread
from copy import deepcopy
import os.path


class PdcAdapter:

    def __init__(self, pmu_id, pdc_id, adapter_port=4712, mqttbroker_ip="127.0.0.1", mqttbroker_port=1883,
                 mqtt_qos=1, logging_level=logging.WARNING):
        # Set-up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging_level)
        handler = logging.StreamHandler(stdout)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Set-up adapter configurations
        self.pmu_id = pmu_id
        self.pdc_id = pdc_id
        self.adapter_port = adapter_port
        self.data_stream_on = False
        self.cfg2 = None
        self.header = None
        self.client_socket = None
        self.listen_pdc_connection = False
        self.cfg_file_path = os.path.dirname(os.path.dirname(__file__))+"/cfg/cfg2"

        # Try to restore configuration
        self.__restore_config()

        self.mqttbroker_ip = mqttbroker_ip
        self.mqttbroker_port = mqttbroker_port
        self.mqtt_qos = mqtt_qos
        self.mqtt_topic = f"pmu_data/pmu-{self.pmu_id}"
        self.mqtt_client = None

        # Set-up socket
        self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        self.socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
        self.socket.bind(('', adapter_port))

    def __restore_config(self):
        try:
            with open(self.cfg_file_path, 'rb') as cfg_file:
                cfg = pickle.load(cfg_file)
                self.__load_cfg(cfg, False)
                self.logger.info("Configuration file restore")
        except FileNotFoundError:
            self.logger.info("No configuration file to be loaded")

    def __load_cfg(self, message, save=True):
        self.cfg2 = message
        # Set configuration frame 1 by casting the cfg2 since they have the same format
        # but different usage
        self.cfg1 = deepcopy(self.cfg2)
        self.cfg1.__class__ = ConfigFrame1
        # Create the header
        self.header = HeaderFrame(self.pmu_id, f"PMU id. {message.get_id_code()}")

        # Save the cfg in a file in order to restore it later
        try:
            with open(self.cfg_file_path, 'wb') as cfg_file:
                pickle.dump(message, cfg_file)
        except IOError as e:
            self.logger.warning("Unable to write configuration file "+str(e))

    def __on_mqtt_disconnect(self, client, userdata, rc):
        self.logger.warning("Disconnected from the broker")

    def __on_mqtt_connect(self, client, userdata, flags, rc):
        self.logger.info(f"Connected to mqtt broker {self.mqttbroker_ip} on port {self.mqttbroker_port}")

    def __on_mqtt_messages(self, client, userdata, msg):
        payload = msg.payload
        message = None
        try:
            # Decode received message
            message = CommonFrame.convert2frame(payload, self.cfg2)
            self.logger.debug("[%d] - Received %s from PMU", self.pdc_id, type(message).__name__)
        except FrameError:
            self.logger.warning("[%d] - Received unknown message from PMU ", self.pdc_id)

        if type(message) == ConfigFrame2:
            self.logger.info("[%d] - Received new CFG2 frame", self.pdc_id)
            self.__load_cfg(message)
        elif self.client_socket and self.data_stream_on and type(message) == DataFrame:
            self.logger.debug(f"[{self.pdc_id}] - {message.get_measurements()} Received new data frame")
            self.client_socket.sendall(message.convert2bytes())

    def __get_command(self):
        buffer_size = 2048
        connection = self.client_socket
        command = None
        received_data = b""
        """
        Keep receiving until SYNC + FRAMESIZE is received, 4 bytes in total.
        Should get this in first iteration. FRAMESIZE is needed to determine when one complete message
        has been received.
        """
        while len(received_data) < 4:
            received_data += connection.recv(buffer_size)
            if not received_data:
                raise PdcConnectionLost("Connection with PDC lost")

        bytes_received = len(received_data)
        total_frame_size = int.from_bytes(received_data[2:4], byteorder="big", signed=False)

        # Keep receiving until every byte of that message is received
        while bytes_received < total_frame_size:
            message_chunk = connection.recv(min(total_frame_size - bytes_received, buffer_size))
            if not message_chunk:
                raise PdcConnectionLost("Connection with PDC lost")
            received_data += message_chunk
            bytes_received += len(message_chunk)

        # If complete message is received try to decode it
        if len(received_data) == total_frame_size:
            try:
                received_message = CommonFrame.convert2frame(received_data)  # Try to decode received data

                if isinstance(received_message, CommandFrame):
                    command = received_message.get_command()
                    self.logger.info("[%d] - Received command: [%s]", self.pmu_id, command)
                else:
                    self.logger.info("[%d] - Received [%s]", self.pmu_id, type(received_message).__name__)
            except FrameError:
                self.logger.warning("[%d] - Received unknown message", self.pmu_id)
        else:
            self.logger.warning("[%d] - Message not received completely", self.pmu_id)
        return command

    def __handle_command(self, command):
        connection = self.client_socket
        if command:
            if command == "start":
                self.data_stream_on = True
                self.logger.info("[%d] - Start sending data", self.pmu_id)
                if self.cfg2 and (not self.mqtt_client or not self.mqtt_client.is_connected()):
                    self.__mqtt_connect()

            elif command == "stop":
                self.data_stream_on = False
                self.logger.info("[%d] - Stop sending data", self.pmu_id)

            elif command == "header":
                # Wait for header being ready
                while not self.header:
                    pass
                self.logger.info("[%d] - Requested Header frame sent", self.pmu_id)
                connection.sendall(self.header.convert2bytes())

            elif command == "cfg1":
                # Wait for configuration frame 1 being ready
                while not self.cfg1:
                    pass
                self.logger.info("[%d] - Requested Configuration frame 1 sent", self.pmu_id)
                self.cfg1.set_time()
                connection.sendall(self.cfg1.convert2bytes())

            elif command == "cfg2":
                # Wait for configuration frame 2 being ready
                while not self.cfg2:
                    pass
                self.cfg2.set_time()
                connection.sendall(self.cfg2.convert2bytes())
                self.logger.info("[%d] - Requested Configuration frame 2 sent", self.pmu_id)

            elif command == "cfg3":
                self.logger.info("[%d] - Requested Configuration frame 3 but not implemented", self.pmu_id)
                # TODO: not implemented
                pass

    def __commands_handler(self, address):
        self.logger.info(f"Connection accepted with {address}")
        try:
            while True:
                command = self.__get_command()
                self.__handle_command(command)
        except Exception as e:
            self.logger.error(e)
        finally:
            self.data_stream_on = False
            self.client_socket.close()
            self.client_socket = None
            # Interrupt connection with the broker
            self.logger.info("Disconnecting from the broker")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            self.logger.info(f"Connection with {address} closed")

    def __mqtt_connect(self):
        self.logger.info("Connection with the MQTT Broker...")
        # Set-up mqtt client
        self.mqtt_client = mqtt.Client(client_id=f"pdc-{self.pdc_id}", clean_session=False)
        self.mqtt_client.on_connect = self.__on_mqtt_connect
        self.mqtt_client.on_disconnect = self.__on_mqtt_disconnect
        self.mqtt_client.on_message = self.__on_mqtt_messages

        # Connect to the broker
        self.mqtt_client.connect(self.mqttbroker_ip, self.mqttbroker_port)
        self.mqtt_client.loop_start()

        # Subscribe to the topic in order to receive the PMU data
        self.mqtt_client.subscribe(self.mqtt_topic, self.mqtt_qos)

    def listen(self):
        # Listen for PDC requests
        self.socket.listen(1)
        while True:
            self.logger.info(f"Listening for connections in port {self.adapter_port}")
            (self.client_socket, address) = self.socket.accept()
            # Connect to the broker in order to receive data
            # only if we don't have a cfg2, otherwise wait for "start command" from the PDC
            if not self.cfg2:
                self.__mqtt_connect()

            # Start a thread in charge of handling the PDC requests
            handler = Thread(target=self.__commands_handler, args=(address,))
            handler.start()
            handler.join()


class PdcConnectionLost(BaseException):
    pass
