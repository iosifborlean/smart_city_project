import paho.mqtt.client as mqtt
from .mqtt_conf_params import MqttConfigurationParameters
import json, time, os

class SmartBinMqttClient():
    def __init__(self, bin_id, broker_address, broker_port):
        self.manager = None
        self.bin_id = bin_id
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.mqtt_client_id = bin_id
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, self.mqtt_client_id, clean_session=False)
        self.mqtt_client.username_pw_set(MqttConfigurationParameters.MQTT_USERNAME,
                                         MqttConfigurationParameters.MQTT_PASSWORD)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.topic_telemetry = "{0}/{1}/{2}/{3}".format(
            MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.BIN_TOPIC,
            self.bin_id,
            MqttConfigurationParameters.TELEMETRY_TOPIC)
        self.topic_action = "{0}/{1}/{2}/{3}".format(MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.BIN_TOPIC,
            self.bin_id,
            MqttConfigurationParameters.ACTION_TOPIC)
        self.topic_config = "{0}/{1}/{2}/{3}".format(MqttConfigurationParameters.MQTT_BASIC_TOPIC,
                                         MqttConfigurationParameters.BIN_TOPIC,
                                         self.bin_id,
                                         MqttConfigurationParameters.CONFIG_TOPIC)
        self.topic_display = "{0}/{1}/{2}/{3}".format(MqttConfigurationParameters.MQTT_BASIC_TOPIC,
                                         MqttConfigurationParameters.BIN_TOPIC,
                                         self.bin_id,
                                         MqttConfigurationParameters.DISPLAY_TOPIC)
        self.topic_info = "{0}/{1}/{2}/{3}".format(
            MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.BIN_TOPIC,
            self.bin_id,
            MqttConfigurationParameters.INFO_TOPIC)

        self.log_filename = os.path.join("..", "logs", "smart_bin_mqtt_client_log.txt")
        open(self.log_filename, "w").close()
        self.log_to_file("Log pulito.")

    def log_to_file(self, message):
        timestamp = time.time()
        log_entry = f"timestamp {timestamp}: {message}"

        print(log_entry)

        try:
            with open(self.log_filename, "a") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Errore durante la scrittura del log: {e}")

    def set_manager(self, manager):
        self.manager = manager

    def subscribe_routine(self):
        self.mqtt_client.subscribe(self.topic_action, qos=1)
        self.mqtt_client.subscribe(self.topic_config, qos=1)
        self.mqtt_client.subscribe(self.topic_display, qos=1)

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with id: {self.mqtt_client_id}, result code: " + str(rc))
        self.subscribe_routine()

    def on_message(self, client, userdata, message):
        if self.manager:
            topic = message.topic
            parts = topic.split('/')
            message_payload = json.loads(message.payload.decode())
            if MqttConfigurationParameters.ACTION_TOPIC in topic:
                if message.payload:
                    self.manager.action_received(message_payload.get("action"))

            if MqttConfigurationParameters.CONFIG_TOPIC in topic:
                if message.payload:
                    self.log_to_file(f"smart_bin_mqtt_client; new config message received: {message_payload}")
                    self.manager.config_received(message_payload.get("config"))

            if MqttConfigurationParameters.DISPLAY_TOPIC in topic:
                if message.payload:
                    self.log_to_file(f"smart_bin_mqtt_client; new display message received: {message_payload}")
                    self.manager.url_received(message_payload.get("url"))

    def publish_telemetry(self):
        if self.manager:
            payload = self.format_senml_telemetry_payload()
            self.mqtt_client.publish(self.topic_telemetry, payload, qos=1)
            self.log_to_file(f"smart_bin_mqtt_client; published to {self.topic_telemetry}: {payload}")

    def format_senml_telemetry_payload(self):
        bin_id = self.manager.descriptor.bin_id
        bin_state = self.manager.state

        senml_payload = [
            {"bn": f"{bin_id}/", "bt": round(time.time(), 2)},
            {"n": "battery", "u": "/", "v": bin_state.get_battery_level()},
            {"n": "fill", "u": "/", "v": bin_state.get_fill_level()},
            {"n": "smoke", "u": "ppm", "v": bin_state.get_smoke_level()},
            {"n": "iaq", "v": bin_state.get_iaq_level()},
            {"n": "lid_opened", "vb": bin_state.lid_opened}
        ]
        return json.dumps(senml_payload)

    def publish_info(self):
        if self.manager:
            bin_descriptor = self.manager.descriptor
            payload = bin_descriptor.to_json()
            self.mqtt_client.publish(self.topic_info, payload, qos=1, retain=True)
            self.log_to_file(f"smart_bin_mqtt_client; published info to {self.topic_info}: {payload}")

    def connect(self):
        self.mqtt_client.connect(self.broker_address, self.broker_port)

    def disconnect(self):
        self.mqtt_client.disconnect()

    def loop(self, timeout=1.0):
        self.mqtt_client.loop(timeout=timeout)

    def loop_start(self):
        self.mqtt_client.loop_start()

    def loop_stop(self):
        self.mqtt_client.loop_stop()