import time
import threading
import datetime
from enum import Enum, unique
from typing import List

from config.config import Config
from config.logger_manager import LoggerManager
from controllers.pid import PIDController
from data.dataframes import Frame
from data.units import CycleDataPoint, DataPoint
from hardware.ads7142 import ADS7142
from hardware.cpc1706y import CPC1706Y
from hardware.rel1101 import REL1101
from app.heater_controller import HeaterController


@unique
class HeatingState(Enum):
    COOLING = 0
    HEATING = 1


@unique
class SteadyState(Enum):
    NO = 0
    YES = 1


class Channel:
    def __init__(
        self,
        logger: LoggerManager,
        channel: int,
        heater_controller: HeaterController,
        fan_controller: REL1101,
        fan_channel: int,
        high_setpoint_C: float,
        low_setpoint_C: float,
        update_rate_s: float,
        cycle_frame: Frame,
        channel_frame: Frame,
        cycle_no: int,
        hysteresis: float,
        cool_threshold_C: float,
        time_warm_s: float,
        time_cool_s: float,
        total_cycles: int,
    ) -> None:
        self.logger = logger
        self.channel = channel
        self.heater_controller = heater_controller
        self.fan_controller = fan_controller
        self.fan_channel = fan_channel
        self.high_setpoint_C = high_setpoint_C
        self.low_setpoint_C = low_setpoint_C
        self.update_rate_s = update_rate_s
        self.cycle_no = cycle_no
        self.hysteresis = hysteresis
        self.cool_threshold_C = cool_threshold_C
        self.time_warm_s = time_warm_s
        self.time_cool_s = time_cool_s
        self.total_cycles = total_cycles

        self.last_rate_update = 0.0
        self.steady_state_start = 0.0
        self.steady_state_duration = 0.0
        self.heating_state = HeatingState.HEATING
        self.steady_state = SteadyState.NO

        self.cycle_frame = cycle_frame
        self.channel_frame = channel_frame
        self.cycle_frame.set_filename(f"cycle_{self.cycle_no}")
        self.channel_frame.set_filename("cycles")
        self.channel_frame.load()

        self.ch_thread = threading.Thread(target=self.run)
        self.pid_thread = threading.Thread(target=self.heater_controller.run)

        self.ch_cancel = threading.Event()
        self.ch_pause = threading.Event()
        
        self.fan_controller.register_channel(self.fan_channel)

        self.heater_controller.set_setpoint(self.high_setpoint_C)
        self.pid_thread.start()

    def run(self) -> None:
        while not self.ch_cancel.is_set():
            setpoint = self.heater_controller.get_setpoint()
            temps = self.heater_controller.get_temps()
            temp = max(temps)

            if self.heating_state == HeatingState.HEATING:
                if setpoint == self.low_setpoint_C:
                    self.heater_controller.set_setpoint(self.high_setpoint_C)
                if self.steady_state == SteadyState.NO:
                    if temp >= self.high_setpoint_C*self.hysteresis:
                        self.logger.info(f"Channel {self.channel} achieved steady state heating")
                        self.steady_state = SteadyState.YES
                        self.steady_state_start = time.monotonic()
                elif self.steady_state == SteadyState.YES:
                    self.steady_state_duration = time.monotonic() - self.steady_state_start
                    if self.steady_state_duration >= self.time_warm_s:
                        self.fan_controller.turn_on(self.fan_channel)
                        self.logger.info(f"Channel {self.channel} maintained steady state heating for sufficient time")
                        self.heating_state = HeatingState.COOLING
                        self.steady_state = SteadyState.NO
                        self.steady_state_start = 0.0
                        self.steady_state_duration = 0.0
                        self.cycle_logs()
                        self.heater_controller.set_setpoint(self.low_setpoint_C)
                        self.logger.info(f"Channel {self.channel} beginning cooling cycle")
                else:
                    self.abort()
                    raise RuntimeError("Invalid State - killing thread")
            elif self.heating_state == HeatingState.COOLING:
                if setpoint == self.high_setpoint_C:
                    self.heater_controller.set_setpoint(self.low_setpoint_C)
                if self.steady_state == SteadyState.NO:
                    if temp <= self.cool_threshold_C:
                        self.logger.info(f"Channel {self.channel} achieved steady state cooling")
                        self.steady_state = SteadyState.YES
                        self.steady_state_start = time.monotonic()
                elif self.steady_state == SteadyState.YES:
                    self.steady_state_duration = time.monotonic() - self.steady_state_start
                    if self.steady_state_duration >= self.time_cool_s:
                        self.fan_controller.turn_off(self.fan_channel)
                        self.logger.info(f"Channel {self.channel} maintained steady state cooling for sufficient time")
                        self.heating_state = HeatingState.HEATING
                        self.steady_state = SteadyState.NO
                        self.steady_state_start = 0.0
                        self.steady_state_duration = 0.0
                        self.wait_for_pause()
                        self.heater_controller.set_setpoint(self.high_setpoint_C)
                        self.logger.info(f"Channel {self.channel} beginning heating cycle")
                else:
                    self.abort()
                    raise RuntimeError("Invalid State - killing thread")
            else:
                self.abort()
                raise RuntimeError("Invalid heating state - killing thread")

            self.log_cy_data(temps)
            self.rate_sleep(self.update_rate_s)

        self.logger.info("closing thread")
        self.abort()
    
    def rate_sleep(self, period_s: float) -> None:
        time_since_last_update_s = time.time() - self.last_rate_update

        if time_since_last_update_s < period_s:
            time.sleep(period_s - time_since_last_update_s)

        self.last_rate_update = time.time()

    def start(self) -> None:
        self.ch_thread.start()

    def join(self) -> None:
        self.ch_thread.join()

    def abort(self) -> None:
        self.logger.info(f"Channel {self.channel} aborting")
        self.fan_controller.turn_off(self.fan_channel)
        self.heater_controller.abort()
        self.pid_thread.join()
        self.ch_cancel.set()

    def pause(self) -> None:
        self.logger.info(f"Setting pause flag on channel {self.channel}")
        self.ch_pause.set()

    def unpause(self) -> None:
        self.logger.info(f"Clearing pause flag on channel {self.channel}")
        self.ch_pause.clear()

    def wait_for_pause(self) -> None:
        self.logger.info(f"Channel {self.channel} waiting for pause to clear")
        while self.ch_pause.is_set():
            self.rate_sleep(self.update_rate_s)

    def log_cy_data(self, temps: List[float]) -> None:
        cy_data = DataPoint(
            datetime.datetime.now(),
            temps[0],
            temps[1],
            self.heater_controller.get_dc(),
            self.cycle_no,
        )
        self.cycle_frame.add_row(cy_data)

    def log_ch_data(self) -> None:
        ch_data = CycleDataPoint(
            self.cycle_frame.df[["therm_L_C", "therm_R_C"]].values.max(),
            self.cycle_frame.df[["therm_L_C", "therm_R_C"]].values.min(),
            self.cycle_frame.df["therm_R_C"].tail(150).mean(),
            self.cycle_frame.df["duty_cycle"].tail(150).mean(),
            self.cycle_no
        )
        self.channel_frame.add_row(ch_data)

    def cycle_logs(self) -> None:
        self.logger.info(f"Rotating logs on channel {self.channel}")
        self.log_ch_data()
        self.channel_frame.save()
        self.cycle_frame.save()
        self.cycle_frame.reset()
        self.cycle_no += 1
        self.save_curr_cycle()
        self.cycle_frame.set_filename(f"cycle_{self.cycle_no}")

        if self.cycle_no >= self.total_cycles:
            self.logger.info(f"Channel {self.channel} achieved {self.total_cycles} cycles")
            self.abort()

    def save_curr_cycle(self) -> None:
        config = Config.from_file("/home/pi/heater_cycle_test/config/config.yaml")
        config.merge(config)

        config.app[f"channel_{self.channel}"]["cycle_no"] = self.cycle_no
        config.save("/home/pi/heater_cycle_test/config/config.yaml")
        self.logger.info(f"Updated cycle_no for channel{self.channel} in config.yaml")

    def get_temps(self) -> List[int]:
        return self.heater_controller.get_temps()

    def get_duty_cycle(self) -> int:
        return self.heater_controller.get_dc()

    def get_cycle_number(self) -> int:
        return self.cycle_no


def CreateChannel(
    config: Config,
    logger: LoggerManager,
    channel: int,
) -> Channel:
    ssr=CPC1706Y(
        logger=logger,
        pin=config.ssr.pin,
        freq=config.ssr.freq,
    )
    therms=ADS7142(
        logger=logger,
        bus_number=config.i2c.bus,
        device_address=config.i2c.add,
    )
    pid_controller=PIDController(
        logger=logger,
        kp=config.controller.pid.kp,
        ki=config.controller.pid.ki,
        kd=config.controller.pid.kd,
        output_limits=config.controller.pid.output_limits,
        p_limits=config.controller.pid.p_limits,
        i_limits=config.controller.pid.i_limits,
        d_limits=config.controller.pid.d_limits,
    )
    heater_controller=HeaterController(
        logger=logger,
        pid=pid_controller,
        ssr=ssr,
        therms=therms,
        update_interval_s=config.controller.update_rate_s,
        minimum_plausible_reading_C=config.controller.minimum_plausible_reading_C,
        maximum_overshoot_C=config.controller.maximum_overshoot_C,
        shutoff_temperature_C=config.controller.shutoff_temperature_C,
        safe_output=config.controller.safe_output_C,
    )
    fan_controller = REL1101(
        logger=logger,
        hub_port=config.fan.port,
        timeout=config.fan.timeout,
    )
    cycle_frame=Frame(
        config.csv.name,
        config.csv.loop_headers,
        config.csv.cycle_path,
    )
    channel_frame=Frame(
        config.csv.name,
        config.csv.cycle_headers,
        config.csv.base_path,
    )

    logger.info(f"Created channel {channel}")
    return Channel(
        logger=logger,
        channel=channel,
        heater_controller=heater_controller,
        fan_controller=fan_controller,
        fan_channel=config.fan.channel,
        high_setpoint_C=config.controller.high_setpoint,
        low_setpoint_C=config.controller.low_setpoint,
        update_rate_s=config.update_rate_s,
        cycle_frame=cycle_frame,
        channel_frame=channel_frame,
        cycle_no=config.cycle_no,
        hysteresis=config.hysteresis,
        cool_threshold_C=config.cool_threshold_C,
        time_warm_s=config.time_warm_s,
        time_cool_s=config.time_cool_s,
        total_cycles=config.total_cycles,
    )

