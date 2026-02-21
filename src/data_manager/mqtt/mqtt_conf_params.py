class MqttConfigurationParameters(object):

    BROKER_ADDRESS = "155.185.4.4"
    BROKER_PORT = 7883
    MQTT_USERNAME = "341689@studenti.unimore.it"
    MQTT_PASSWORD = "euyahyhjttftyuxy"
    DATA_MANAGER_CLIENT_ID = "central_data_manager"
    MQTT_BASIC_TOPIC = "/iot/user/{0}".format(MQTT_USERNAME)
    BIN_TOPIC = "bin"
    TELEMETRY_TOPIC = "telemetry"
    ALERT_TOPIC = "alert"
    MAINTENANCE_TOPIC = "maintenance"
    COLLECTION_TOPIC = "collection"
    SAFETY_CHECK_TOPIC = "safety_check"
    RESOLUTION_TOPIC = "res"
    BIN_INFO_TOPIC = "info"
    ACTION_TOPIC = "action"
    CONFIG_TOPIC = "config"
    DISPLAY_TOPIC = "display"
    INFO_TOPIC = "info"