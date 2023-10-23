import time
import threading
import RPi.GPIO as gpio
from typing import List

from config.config import Config
from config.logger_manager import LoggerManager
from app.channel import Channel, CreateChannel


class Application:
    def __init__(
        self,
        config: Config,
        logger: LoggerManager,
    ) -> None:
        self.config = config
        self.logger = logger
        self.channels: List[Channel] = []

        self.configure()
        self.setup()

    def configure(self) -> None:
        gpio.setmode(gpio.BCM)

    def setup(self) -> None:
        channel_1 = CreateChannel(
            self.config.channel_1,
            self.logger,
            1,
        ) if self.config.channel_1.enabled else None
        channel_2 = CreateChannel(
            self.config.channel_2,
            self.logger,
            2,
        ) if self.config.channel_2.enabled else None
        channel_3 = CreateChannel(
            self.config.channel_3,
            self.logger,
            3,
        ) if self.config.channel_3.enabled else None
        channel_4 = CreateChannel(
            self.config.channel_4,
            self.logger,
            4,
        ) if self.config.channel_4.enabled else None
        channel_5 = CreateChannel(
            self.config.channel_5,
            self.logger,
            5,
        ) if self.config.channel_5.enabled else None
        channel_6 = CreateChannel(
            self.config.channel_6,
            self.logger,
            6,
        ) if self.config.channel_6.enabled else None
        channel_7 = CreateChannel(
            self.config.channel_7,
            self.logger,
            7,
        ) if self.config.channel_7.enabled else None
        channel_8 = CreateChannel(
            self.config.channel_8,
            self.logger,
            8,
        ) if self.config.channel_8.enabled else None

        self.channels = [channel_1, channel_2, channel_3, channel_4,
                         channel_5, channel_6, channel_7, channel_8]
        self.channels = [ch for ch in self.channels if ch is not None]

    def run(self) -> None:
        self.logger.info("Starting channel threads")
        threads: List[threading.Thread] = [ch.ch_thread for ch in self.channels]
        for th in threads:
            th.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            for channel in self.channels:
                channel.abort()

            for th in threads:
                th.join()

        gpio.cleanup()

