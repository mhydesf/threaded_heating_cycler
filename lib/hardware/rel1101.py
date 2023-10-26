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
        self.channels[channel].setDutyCycle(0)

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

