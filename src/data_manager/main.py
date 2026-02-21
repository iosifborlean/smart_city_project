import time
from mqtt.data_manager_mqtt_client import DataManagerMqttClient
from mqtt.mqtt_conf_params import MqttConfigurationParameters
from models.data_manager import DataManager
from src.data_manager.data_manager_config import DataManagerConfigParameters

if __name__ == "__main__":
    data_manager_id = MqttConfigurationParameters.DATA_MANAGER_CLIENT_ID
    data_manager_mqtt_client = DataManagerMqttClient(data_manager_id, MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
    data_manager = DataManager(data_manager_mqtt_client)
    data_manager.mqtt_client.connect()
    data_manager.mqtt_client.loop_start()
    #data_manager.mqtt_client.publish_alert("bin001", MqttConfigurationParameters.COLLECTION_TOPIC, is_resolved=True)
    #data_manager.mqtt_client.publish_alert("telemetry", MqttConfigurationParameters.COLLECTION_TOPIC, is_resolved=True)
    #data_manager.mqtt_client.publish_alert("bin001", MqttConfigurationParameters.SAFETY_CHECK_TOPIC, is_resolved=True)
    #data_manager.mqtt_client.publish_alert("bin001", MqttConfigurationParameters.MAINTENANCE_TOPIC, is_resolved=True)
    data_manager.new_bin_config(new_fill_threshold = 0.8, new_smoke_threshold = 14.0, new_iaq_threshold = 190, new_battery_threshold=0.1)
    new_config = {"fill_threshold": DataManagerConfigParameters.FILL_THRESHOLD,
            "smoke_threshold": DataManagerConfigParameters.SMOKE_THRESHOLD,
            "iaq_threshold": DataManagerConfigParameters.IAQ_THRESHOLD,
            "battery_threshold": DataManagerConfigParameters.BATTERY_THRESHOLD}
    for i in range(300):
        if i==20:
            data_manager.mqtt_client.publish_config("bin001", new_config)
        time.sleep(0.5)

    data_manager.mqtt_client.loop_stop()