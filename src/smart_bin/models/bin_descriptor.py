import json
class BinDescriptor:
    def __init__(self, bin_id, latitude, longitude, capacity_liters=50, fill_threshold=0.9, smoke_threshold=15.0, iaq_threshold=200, battery_threshold=0.2):
        self.bin_id = bin_id
        self.capacity_liters = capacity_liters
        self.latitude = latitude
        self.longitude = longitude
        self.fill_threshold = fill_threshold
        self.smoke_threshold = smoke_threshold
        self.iaq_threshold = iaq_threshold
        self.battery_threshold = battery_threshold

    def to_json(self):
        return json.dumps(self.__dict__)