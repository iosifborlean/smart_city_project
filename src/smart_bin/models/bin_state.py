class BinState:
    def __init__(self, battery=100, smoke=0, iaq=0, fill=0):
        self.battery = battery
        self.smoke = smoke
        self.iaq = iaq
        self.fill = fill
        self.current_url = None
        self.lid_opened = True

    def get_battery_level(self):
        return round(self.battery/100, 2)
    def get_fill_level(self):
        return round(self.fill/100, 2)
    def get_smoke_level(self):
        return round(self.smoke, 2)
    def get_iaq_level(self):
        return round(self.iaq, 2)