import paho.mqtt.client as mqtt
from .mqtt_conf_params import MqttConfigurationParameters
from src.data_manager.data_manager_config import DataManagerConfigParameters
import json, time, os

class DataManagerMqttClient:
    def __init__(self, client_id, broker_address, broker_port):
        self.manager = None
        self.mqtt_client_id = client_id
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, self.mqtt_client_id, clean_session=False)
        self.mqtt_client.username_pw_set(MqttConfigurationParameters.MQTT_USERNAME,
                                         MqttConfigurationParameters.MQTT_PASSWORD)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.topic_telemetry = "{0}/{1}/+/{2}".format(
            MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.BIN_TOPIC,
            MqttConfigurationParameters.TELEMETRY_TOPIC)
        self.topic_alert = "{0}/{1}/+/+/{2}".format(MqttConfigurationParameters.MQTT_BASIC_TOPIC, MqttConfigurationParameters.ALERT_TOPIC, MqttConfigurationParameters.RESOLUTION_TOPIC)
        self.topic_info = "{0}/{1}/+/{2}".format(
            MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.BIN_TOPIC,
            MqttConfigurationParameters.INFO_TOPIC)

        self.log_filename = os.path.join("..", "logs", "data_manager_mqtt_client_log.txt")
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
        self.mqtt_client.subscribe(self.topic_telemetry, qos=1)
        self.mqtt_client.subscribe(self.topic_alert, qos=1)
        self.mqtt_client.subscribe(self.topic_info, qos=1)

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with id: {self.mqtt_client_id}, with result code: " + str(rc))
        self.subscribe_routine()

    def on_message(self, client, userdata, message):
        if self.manager:
            topic = message.topic
            parts = topic.split('/')

            if MqttConfigurationParameters.TELEMETRY_TOPIC in topic:
                senml_payload = json.loads(message.payload.decode())
                self.log_to_file(f"data_manager_mqtt_client: received message {senml_payload} on topic {topic}")
                bin_id = parts[-2]
                data_dict = self.process_senml_to_dict(senml_payload)
                self.manager.process_telemetry(bin_id, data_dict)

            if MqttConfigurationParameters.RESOLUTION_TOPIC in topic:
                self.log_to_file(f"data_manager_mqtt_client: received message {message.payload.decode()} on topic {topic}")
                bin_id = parts[-2]
                alert_type = parts[-3]
                employee_id = json.loads(message.payload.decode()).get("employee_id")
                self.manager.process_alert_resolution_message(bin_id, alert_type, employee_id)

            if MqttConfigurationParameters.INFO_TOPIC in topic:
                self.log_to_file(f"data_manager_mqtt_client: received info message {message.payload.decode()} on topic {topic}")
                bin_id = parts[-2]
                self.manager.process_information_message(bin_id, json.loads(message.payload.decode()))

    def publish_alert(self, bin_id, alert_type, alert_id=None, lat=None, lon=None, is_resolved=False):
        topic = "{0}/{1}/{2}/{3}".format(MqttConfigurationParameters.MQTT_BASIC_TOPIC, MqttConfigurationParameters.ALERT_TOPIC, alert_type, bin_id)

        if is_resolved:
            self.log_to_file(f"data_manager_mqtt_client: publshing to {topic} empty message")
            self.mqtt_client.publish(topic, payload=None, qos=1, retain=True)
        else:
            payload = json.dumps({
                "bin_id": bin_id,
                "alert_id" : alert_id,
                "location": {
                    "lat": lat,
                    "lon": lon
                },
                "timestamp": time.time()
            })
            self.log_to_file(f"data_manager_mqtt_client: publshing to {topic}: {payload}")
            self.mqtt_client.publish(topic, payload, 1, retain=True)

    def publish_config(self, bin_id, config=None):
        topic = "{0}/{1}/{2}/{3}".format(MqttConfigurationParameters.MQTT_BASIC_TOPIC, MqttConfigurationParameters.BIN_TOPIC, bin_id, MqttConfigurationParameters.CONFIG_TOPIC)
        payload = json.dumps({
            "bin_id": bin_id,
            "config" : config
        })
        self.mqtt_client.publish(topic, payload, 1)
        self.log_to_file(f"data_manager_mqtt_client: publishing new bin {bin_id} config message: {payload}")

    def publish_url(self, bin_id, url):
        topic = "{0}/{1}/{2}/{3}".format(MqttConfigurationParameters.MQTT_BASIC_TOPIC, MqttConfigurationParameters.BIN_TOPIC, bin_id, MqttConfigurationParameters.DISPLAY_TOPIC)
        payload = json.dumps({
            "bin_id": bin_id,
            "url" : url
        })
        self.mqtt_client.publish(topic, payload, 1)
        self.log_to_file(f"data_manager_mqtt_client; sent new url {url} for {bin_id}")

    def process_senml_to_dict(self, senml_payload):
        data_dict = {}

        timestamp = senml_payload[0].get("bt", time.time())
        data_dict["timestamp"] = timestamp

        for entry in senml_payload:
            if "n" not in entry:
                continue

            name = entry["n"]

            if "v" in entry:
                value = entry["v"]
            elif "vb" in entry:
                value = entry["vb"]
            elif "vs" in entry:
                value = entry["vs"]
            else:
                value = None

            data_dict[name] = value

        return data_dict

    def loop(self, timeout=2.0):
        self.mqtt_client.loop(timeout=timeout)

    def loop_start(self):
        self.mqtt_client.loop_start()

    def loop_stop(self):
        self.mqtt_client.loop_stop()

    def connect(self):
        self.mqtt_client.connect(self.broker_address, self.broker_port)

    def disconnect(self):
        self.mqtt_client.disconnect()