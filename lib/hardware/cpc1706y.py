import RPi.GPIO as gpio
from config.logger_manager import LoggerManager


class CPC1706Y:
    def __init__(
        self,
        logger: LoggerManager,
        pin: int,
        freq: int,
    ) -> None:
        self.logger = logger

        self.pin = pin
        self.freq = freq
        self.pwm = None

        self.setup()

    def setup(self) -> None:
        self.logger.info(f"Configuring PWM on GPIO {self.pin} at {self.freq} Hz")
        gpio.setup(self.pin, gpio.OUT)
        self.pwm = gpio.PWM(self.pin, self.freq)
        self.pwm.start(0)

    def set_duty_cycle(self, duty_cycle: int) -> None:
        self.pwm.ChangeDutyCycle(duty_cycle)

    def disable(self) -> None:
        self.pwm.stop()

