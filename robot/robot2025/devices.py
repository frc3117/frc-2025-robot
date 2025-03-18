from frctools.devices import DevicesManager


class Devices2025:
    __INSTANCE__: 'Devices2025' = None

    def __init__(self):
        DevicesManager.instance().load_devices_json(json_path='config.json')


    @classmethod
    def instance(cls):
        if cls.__INSTANCE__ is None:
            cls.__INSTANCE__ = cls()

        return cls.__INSTANCE__
