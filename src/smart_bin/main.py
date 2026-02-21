import time
from mqtt.smart_bin_mqtt_client import SmartBinMqttClient
from mqtt.mqtt_conf_params import MqttConfigurationParameters
from models.bin_state import BinState
from models.bin_descriptor import BinDescriptor
from models.smart_bin import SmartBin

if __name__ == "__main__":
    bin_id = "bin001"
    bin_descriptor = BinDescriptor(bin_id, 44.6458, 10.9257, 100, 0.9,15, 200, 0.2 )
    bin_state = BinState()
    smart_bin_mqtt_client = SmartBinMqttClient(bin_descriptor.bin_id, MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
    smart_bin = SmartBin(bin_descriptor, bin_state, smart_bin_mqtt_client)
    smart_bin.mqtt_client.connect()
    smart_bin.mqtt_client.loop_start()
    smart_bin.mqtt_client.publish_info()

    for i in range(14):
        smart_bin.update_measurements()
        if i==2:
            smart_bin.simulate_anomaly("fill")
        if i==3:
            smart_bin.simulate_anomaly_res("fill")
        if i==5:
            smart_bin.simulate_anomaly("battery")
        if i==6:
            smart_bin.simulate_anomaly_res("battery")
        if i==8:
            smart_bin.simulate_anomaly("smoke")
        if i==9:
            smart_bin.simulate_anomaly_res("smoke")
        if i==11:
            smart_bin.simulate_anomaly("voc")
        if i==12:
            smart_bin.simulate_anomaly_res("voc")

        smart_bin.perform_checks()
        smart_bin.sync_state_with_cloud()
        time.sleep(6)

    smart_bin.mqtt_client.loop_stop()