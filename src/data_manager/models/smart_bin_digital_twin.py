import time

class SmartBinDigitalTwin:
    def __init__(self, bin_id, descriptor_dict):
        self.bin_id = bin_id
        self.descriptor = {"latitude":descriptor_dict["latitude"],
                           "longitude":descriptor_dict["longitude"],
                           "fill_threshold":descriptor_dict["fill_threshold"],
                           "smoke_threshold":descriptor_dict["smoke_threshold"],
                           "iaq_threshold":descriptor_dict["iaq_threshold"],
                           "battery_threshold":descriptor_dict["battery_threshold"],
                           "capacity_liters":descriptor_dict["capacity_liters"]
                           }
        self.last_sync = None
        self.nearest_free_bin_id = None
        self.state = {
            "battery": None,
            "fill": None,
            "smoke": None,
            "iaq": None,
            "lid_opened": None
        }

    def update_state(self, data_dict):  
        self.state.update(data_dict)

    def update_info(self, data_dict):
        self.descriptor.update(data_dict)

    def is_air_quality_bad(self):
        if self.state["iaq"] is None:
            return False
        return self.state["iaq"] > self.descriptor["iaq_threshold"]

    def fire_alarm(self):
        if self.state["smoke"] is None:
            return False
        return self.state["smoke"] > self.descriptor["smoke_threshold"]

    def is_nearly_full(self):
        if self.state["fill"] is None:
            return False
        return self.state["fill"] > self.descriptor["fill_threshold"]

    def is_lid_opened(self):
        return self.state["lid_opened"]

    def is_battery_low(self):
        return self.state["battery"] < self.descriptor["battery_threshold"]
