from threading import Lock
from config.logger_manager import LoggerManager
from Phidget22.Phidget import PhidgetException
from Phidget22.Devices.DigitalOutput import DigitalOutput


class REL1101:
    _instance = None
    _lock: Lock = Lock()

    def __new__(
        cls,
        logger: LoggerManager,
        hub_port: int,
        timeout: int,
    ):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(REL1101, cls).__new__(cls)
                cls._instance.initialize(logger, hub_port, timeout)
            return cls._instance

    def initialize(
        self,
        logger: LoggerManager,
        hub_port: int,
        timeout: int,
    ) -> None:
        self.logger = logger
        self.hub_port = hub_port
        self.timeout = timeout
        self.channels = {}

    def register_channel(self, channel: int) -> None:
        ch = DigitalOutput()
        ch.setHubPort(self.hub_port)
        ch.setChannel(channel)
        ch.openWaitForAttachment(self.timeout)
        self.channels[channel] = ch

    def turn_on(self, fan_channel: int) -> None:
        try:
            with self._lock:
                self.channels[fan_channel].setDutyCycle(1)
                self.logger.info(f"Turned on relay channel {fan_channel}")
        except PhidgetException as e:
            self.logger.error(f"Error turning on relay channel {fan_channel}: {e.details}")

    def turn_off(self, fan_channel: int) -> None:
        try:
            with self._lock:
                self.channels[fan_channel].setDutyCycle(0)
                self.logger.info(f"Turned off relay channel {fan_channel}")
        except PhidgetException as e:
            self.logger.error(f"Error turning off relay channel {fan_channel}: {e.details}")


if __name__ == "__main__":
    import time
    from config.config import Config

    config = Config.from_file("/home/pi/heater_cycle_test/config/config.yaml")
    config.merge(config)
    logger = LoggerManager.get_logger(config.log)  

    sing = REL1101(logger, 0, 1000)
    sing.register_channel(0)
    sing.register_channel(1)
    sing.register_channel(2)
    sing.register_channel(3)
    sing.register_channel(4)
    sing.register_channel(5)
    sing.register_channel(6)
    sing.register_channel(7)
    sing.register_channel(8)
    sing.register_channel(9)
    sing.register_channel(10)
    sing.register_channel(11)
    sing.register_channel(12)
    sing.register_channel(13)
    sing.register_channel(14)
    sing.register_channel(15)
    
    for i in range(16):
        sing.turn_on(i)

    while True:
        time.sleep(1)

