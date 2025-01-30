from ntcore import NetworkTableInstance


class ReefSelector:
    __INSTANCE__: 'ReefSelector' = None

    def __init__(self, init_value: int = None, nt_instance: NetworkTableInstance = None):
        ReefSelector.__INSTANCE__ = self

        self.__nt_inst = NetworkTableInstance.getDefault() if nt_instance is None else nt_instance
        self.__entry = self.__nt_inst.getEntry('/selected_reef')

        if init_value is not None:
            self.__entry.setValue(init_value)

    def __get_value__(self) -> int:
        return self.__entry.getInteger(0)
    @staticmethod
    def get_value() -> int:
        return ReefSelector.instance().__get_value__()

    def __set_value__(self, value: int):
        self.__entry.setInteger(value)
    @staticmethod
    def set_value(value: int):
        ReefSelector.instance().__set_value__(value)

    @staticmethod
    def instance():
        if ReefSelector.__INSTANCE__ is None:
            ReefSelector()

        return ReefSelector.__INSTANCE__