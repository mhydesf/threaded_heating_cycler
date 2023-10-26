import RPi.GPIO as gpio
from typing import Dict

from config.config import Config
from config.logger_manager import LoggerManager
from app.channel import Channel, CreateChannel
from app_ipc.payloads import RepPayload


class Application:
    def __init__(
        self,
        config: Config,
        logger: LoggerManager,
    ) -> None:
        self.config = config
        self.logger = logger
        self.channels: Dict[str, Channel] = {}

        self.configure()
        self.setup()

    def configure(self) -> None:
        gpio.setmode(gpio.BCM)

    def setup(self) -> None:
        if self.config.channel_1.enabled:
            self.channels["channel_1"] = CreateChannel(
                self.config.channel_1,
                self.logger,
                1,
            ) 
        if self.config.channel_2.enabled:
            self.channels["channel_2"] = CreateChannel(
                self.config.channel_2,
                self.logger,
                2,
            )
        if self.config.channel_3.enabled:
            self.channels["channel_3"] = CreateChannel(
                self.config.channel_3,
                self.logger,
                3,
            ) 
        if self.config.channel_4.enabled:
            self.channels["channel_4"] = CreateChannel(
                self.config.channel_4,
                self.logger,
                4,
            )
        if self.config.channel_5.enabled:
            self.channels["channel_5"] = CreateChannel(
                self.config.channel_5,
                self.logger,
                5,
            ) 
        if self.config.channel_6.enabled:
            self.channels["channel_6"] = CreateChannel(
                self.config.channel_6,
                self.logger,
                6,
            )
        if self.config.channel_7.enabled:
            self.channels["channel_7"] = CreateChannel(
                self.config.channel_7,
                self.logger,
                7,
            ) 
        if self.config.channel_8.enabled:
            self.channels["channel_8"] = CreateChannel(
                self.config.channel_8,
                self.logger,
                8,
            )

    def launch(self) -> None:
        self.logger.info("Starting channel threads")
        for ch in self.channels.values():
            ch.start()

    def shutdown(self) -> None:
        self.logger.info("Shutting down all channels")
        for channel in self.channels.values():
            channel.abort()
            channel.join()

        gpio.cleanup()

    def get_temps(self, channel: str) -> RepPayload:
        if not isinstance(channel, str):
            return RepPayload(status="error", payload="Channel is of invalid type")
        if channel == "all":
            response = RepPayload(
                status="ok",
                payload={key: val.get_temps() for key,val in self.channels.items()}
            )
            return response
        if channel not in self.channels.keys():
            return RepPayload(status="error", payload="Invalid channel")

        return RepPayload(status="ok", payload=self.channels[channel].get_temps())

    def get_duty_cycle(self, channel: str) -> RepPayload:
        if not isinstance(channel, str):
            return RepPayload(status="error", payload="Channel is of invalid type")
        if channel == "all":
            response = RepPayload(
                status="ok",
                payload={key: val.get_duty_cycle() for key,val in self.channels.items()}
            )
            return response
        if channel not in self.channels.keys():
            return RepPayload(status="error", payload="Invalid channel")

        return RepPayload(status="ok", payload=self.channels[channel].get_duty_cycle())
    
    def get_cycle_number(self, channel: str) -> RepPayload:
        if not isinstance(channel, str):
            return RepPayload(status="error", payload="Channel is of invalid type")
        if channel == "all":
            response = RepPayload(
                status="ok",
                payload={key: val.get_cycle_number() for key,val in self.channels.items()}
            )
            return response
        if channel not in self.channels.keys():
            return RepPayload(status="error", payload="Invalid channel")

        return RepPayload(status="ok", payload=self.channels[channel].get_cycle_number())

    def shutdown_channel(self, channel: str) -> RepPayload:
        if not isinstance(channel, str):
            return RepPayload(status="error", payload="Channel is of invalid type")
        if channel == "all":
            response = RepPayload(
                status="ok",
                payload={key: val.abort() for key,val in self.channels.items()}
            )
            return response
        if channel not in self.channels.keys():
            return RepPayload(status="error", payload="Invalid channel")

        return RepPayload(status="ok", payload=self.channels[channel].abort())

    def pause_channel(self, channel: str) -> RepPayload:
        if not isinstance(channel, str):
            return RepPayload(status="error", payload="Channel is of invalid type")
        if channel == "all":
            response = RepPayload(
                status="ok",
                payload={key: val.pause() for key,val in self.channels.items()}
            )
            return response
        if channel not in self.channels.keys():
            return RepPayload(status="error", payload="Invalid channel")

        return RepPayload(status="ok", payload=self.channels[channel].pause())

    def unpause_channel(self, channel: str) -> RepPayload:
        if not isinstance(channel, str):
            return RepPayload(status="error", payload="Channel is of invalid type")
        if channel == "all":
            response = RepPayload(
                status="ok",
                payload={key: val.unpause() for key,val in self.channels.items()}
            )
            return response
        if channel not in self.channels.keys():
            return RepPayload(status="error", payload="Invalid channel")

        return RepPayload(status="ok", payload=self.channels[channel].unpause())

