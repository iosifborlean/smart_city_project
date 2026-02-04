import random, time, json, os

class SmartBin:
    def __init__(self, descriptor, state, mqtt_client):
        self.descriptor = descriptor
        self.state = state
        self.mqtt_client = mqtt_client
        self.mqtt_client.set_manager(self)

        self.log_filename = os.path.join("..", "logs", "smart_bin_log.txt")
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

    def action_received(self, action):
        if action == "close_lid":
            self.close_lid()
        elif action == "open_lid":
            self.open_lid()

    def url_received(self, url):
        self.log_to_file(f"smart_bin; changed url to: {url}")
        self.change_qr_code(url)

    def config_received(self, config_dictionary):
        self.log_to_file(f"smart_bin; new config received: {config_dictionary}")
        if "fill_threshold" in config_dictionary:
            self.descriptor.fill_threshold = config_dictionary["fill_threshold"]
            self.log_to_file(f"smart_bin; new fill_threshold set: {self.descriptor.fill_threshold}")
        if "smoke_threshold" in config_dictionary:
            self.descriptor.smoke_threshold = config_dictionary["smoke_threshold"]
            self.log_to_file(f"smart_bin; new smoke_threshold set: {self.descriptor.smoke_threshold}")
        if "iaq_threshold" in config_dictionary:
            self.descriptor.iaq_threshold = config_dictionary["iaq_threshold"]
            self.log_to_file(f"smart_bin; new iaq_threshold set: {self.descriptor.iaq_threshold}")

    def sync_state_with_cloud(self):
        self.mqtt_client.publish_telemetry()

    def update_measurements(self):
        if self.state.battery>0:
            self.state.battery = round(max(0, self.state.battery - random.uniform(0.5, 1.5)), 2)
            self.state.fill = round(min(100, self.state.fill + random.uniform(2, 5)), 2)
            self.state.smoke = round(random.uniform(0.1, 2.5), 2)
            self.state.iaq = int(round(random.uniform(0.0, 150.0), 2))

    def perform_checks(self):
        if self.state.get_fill_level() > self.descriptor.fill_threshold:
            self.close_lid()

        if self.state.get_smoke_level() > self.descriptor.smoke_threshold:
            self.close_lid()

    def simulate_anomaly(self, anomaly):
        if anomaly=="smoke":
            self.state.smoke = 100
        if anomaly=="voc":
            self.state.iaq = 250
        if anomaly=="fill":
            self.state.fill = 95.0
        if anomaly=="battery":
            self.state.battery = 5

    def simulate_anomaly_res(self, anomaly):
        if anomaly=="smoke":
            self.state.smoke = 2
        if anomaly=="voc":
            self.state.iaq = 100
        if anomaly=="fill":
            self.state.fill = 0
        if anomaly=="battery":
            self.state.battery = 100

    def change_qr_code(self, url):
        self.state.current_url = url
        self.log_to_file(f"smart_bin; changing qr code to {url}")

    def open_lid(self):
        if not self.state.lid_opened:
            self.state.lid_opened = True
            self.log_to_file(f"smart_bin; lid opened")
        else:
            self.log_to_file(f"smart_bin; lid already open")

    def close_lid(self):
        if self.state.lid_opened:
            self.state.lid_opened = False
            self.log_to_file(f"smart_bin; lid closed")
        else:
            self.log_to_file(f"smart_bin; lid already closed")
