from src.data_manager.models.smart_bin_digital_twin import SmartBinDigitalTwin
from src.data_manager.data_manager_config import DataManagerConfigParameters
from src.data_manager.mqtt.mqtt_conf_params import MqttConfigurationParameters
from .alert import Alert
import time, os

class DataManager:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.active_bins={}
        self.mqtt_client.set_manager(self)
        self.active_alerts = {
            MqttConfigurationParameters.COLLECTION_TOPIC: {},
            MqttConfigurationParameters.MAINTENANCE_TOPIC: {},
            MqttConfigurationParameters.SAFETY_CHECK_TOPIC: {}
        }
        self.alert_id = 0

        self.log_filename = os.path.join("..", "logs", "data_manager_log.txt")
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

    def process_alert_resolution_message(self, bin_id, alert_type, employee_id):
        if bin_id in self.active_alerts[alert_type]:
            alert = self.active_alerts[alert_type][bin_id]
            alert.resolved = True
            alert.resolver_employee_id = employee_id
            self.mqtt_client.publish_alert(bin_id, alert_type, is_resolved=True)
            self.log_to_file(f"data_manager; employee {employee_id} marked {alert_type} with id {alert.alert_id} for {bin_id} as resolved")

    def process_telemetry(self, bin_id, data_dict):
        if bin_id not in self.active_bins:
            return

        timestamp = data_dict.pop("timestamp", time.time())
        target_bin = self.active_bins[bin_id]
        target_bin.update_state(data_dict)
        self.perform_checks(bin_id)

    def process_information_message(self, bin_id, info_dict):
        if bin_id not in self.active_bins:
            if bin_id == info_dict.pop("bin_id", None):
                self.active_bins[bin_id] = SmartBinDigitalTwin(bin_id=bin_id, descriptor_dict=info_dict)
                self.log_to_file(f"data_manager; new bin registered: {bin_id}")
        else:
            if bin_id == info_dict.pop("bin_id"):
                target_bin = self.active_bins[bin_id]
                target_bin.update_info(info_dict)

    def generate_alert(self, target_bin, alert_type):
        alert = Alert(target_bin.bin_id, self.alert_id, alert_type)
        self.alert_id += 1
        self.active_alerts[alert_type][target_bin.bin_id] = alert
        self.mqtt_client.publish_alert(target_bin.bin_id, alert_type, alert.alert_id, target_bin.descriptor["latitude"], target_bin.descriptor["longitude"])

    def resolve_alert(self, target_bin, alert_type):
        self.active_alerts[alert_type].pop(target_bin.bin_id, None)
        self.log_to_file(f"data_manager; {alert_type} alert for {target_bin.bin_id} resolved")

    def check_nearest_free_bin(self, target_bin):
        nearest_free_bin_id = "bin003"
        if nearest_free_bin_id != target_bin.nearest_free_bin_id:
            target_bin.nearest_free_bin_id = nearest_free_bin_id
            url = self.generate_new_url(nearest_free_bin_id)
            self.mqtt_client.publish_url(target_bin.bin_id, url)

    def generate_new_url(self, nearest_free_bin_id):
        return (f"https://smartbin.it/map/{nearest_free_bin_id}")

    def new_bin_config(self, new_fill_threshold, new_smoke_threshold, new_iaq_threshold, new_battery_threshold):
        DataManagerConfigParameters.FILL_THRESHOLD = new_fill_threshold
        DataManagerConfigParameters.SMOKE_THRESHOLD = new_smoke_threshold
        DataManagerConfigParameters.IAQ_THRESHOLD = new_iaq_threshold
        DataManagerConfigParameters.BATTERY_THRESHOLD = new_battery_threshold

    def perform_checks(self, bin_id):
        if bin_id in self.active_bins:
            target_bin = self.active_bins[bin_id]

            alert_type = MqttConfigurationParameters.COLLECTION_TOPIC
            if target_bin.is_nearly_full() or target_bin.is_air_quality_bad():
                self.check_nearest_free_bin(target_bin)
                if not target_bin.bin_id in list(self.active_alerts[alert_type].keys()):
                    self.generate_alert(target_bin, alert_type)
                elif self.active_alerts[alert_type][target_bin.bin_id].resolved:
                    self.resolve_alert(target_bin, alert_type)
                    self.generate_alert(target_bin, alert_type)
            else:
                if bin_id in self.active_alerts[alert_type].keys():
                    self.resolve_alert(target_bin, alert_type)

            alert_type = MqttConfigurationParameters.MAINTENANCE_TOPIC
            if target_bin.is_battery_low():
                if not target_bin.bin_id in list(self.active_alerts[alert_type].keys()):
                    self.generate_alert(target_bin, alert_type)
                elif self.active_alerts[alert_type][target_bin.bin_id].resolved:
                    self.resolve_alert(target_bin, alert_type)
                    self.generate_alert(target_bin, alert_type)
            else:
                if bin_id in self.active_alerts[alert_type].keys():
                    self.resolve_alert(target_bin, alert_type)

            alert_type = MqttConfigurationParameters.SAFETY_CHECK_TOPIC
            if target_bin.fire_alarm():
                if not target_bin.bin_id in list(self.active_alerts[alert_type].keys()):
                    self.generate_alert(target_bin, alert_type)
                elif self.active_alerts[alert_type][target_bin.bin_id].resolved:
                    self.resolve_alert(target_bin, alert_type)
                    self.generate_alert(target_bin, alert_type)
            else:
                if bin_id in self.active_alerts[alert_type].keys():
                    self.resolve_alert(target_bin, alert_type)