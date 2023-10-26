import time
from typing import List, TypeVar, Generic, Optional
from threading import Lock, Event

from config.logger_manager import LoggerManager
from controllers.pid import PIDController
from hardware.ads7142 import ADS7142
from hardware.cpc1706y import CPC1706Y


OutputType = TypeVar("OutputType", bound=float)


class HeaterController(Generic[OutputType]):
    def __init__(
        self,
        logger: LoggerManager,
        pid: PIDController,
        ssr: CPC1706Y,
        therms: ADS7142,
        update_interval_s: float,
        minimum_plausible_reading_C: float,
        maximum_overshoot_C: float,
        shutoff_temperature_C: float,
        safe_output: Optional[OutputType] = None
    ) -> None:
        self.logger = logger
        self.pid = pid
        self.ssr = ssr
        self.therms = therms
        self.update_interval_s = update_interval_s
        self.minimum_plausible_reading_C = minimum_plausible_reading_C
        self.maximum_overshoot_C = maximum_overshoot_C
        self.shutoff_temperature_C = shutoff_temperature_C
        if safe_output is None:
            safe_output = min(self.pid.output_limits)
        self.safe_output = safe_output
        self.time_of_last_update = time.monotonic()
        self.time_of_last_sleep = time.monotonic()
        self.reading_timeout_s = 20

        self.setpoint_C = None
        self.temps_C = [0, 0]
        self.dc = 0

        self.setpoint_mtx = Lock()
        self.temp_mtx = Lock()
        self.dc_mtx = Lock()
        
        self.pid_cancel = Event()
    
    def run(self) -> None:
        while not self.pid_cancel.is_set():
            temps_C = self.therms.read_thermistor_values()
            input_C = max(temps_C)
            dc = self.update(input_C)
            if dc is not None:
                self.ssr.set_duty_cycle(dc)
                self.set_dc(dc)
            self.set_temps(temps_C)

            self.rate_sleep(self.update_interval_s)

        self.logger.info("closing heater controller")

    def update(self, temperature_C: float) -> float:
        if self.setpoint_C is None:
            return None
        now = time.monotonic()
        time_since_update_s = now - self.time_of_last_update
        if time_since_update_s < self.update_interval_s:
            return None

        if temperature_C < self.minimum_plausible_reading_C:
            if time_since_update_s < self.reading_timeout_s:
                self.logger.debug("Ignoring temperature of {:.1f} C".format(temperature_C))
                return None
            else:
                if (
                    time_since_update_s
                    < self.reading_timeout_s + 2 * self.update_interval_s
                ):
                    self.logger.warning(
                        (
                            "No valid temperature readings for {:.3f} s."
                            "Switching to safe output of {:.3f}."
                        ).format(time_since_update_s, self.safe_output)
                    )
                return self.safe_output

        self.time_of_last_update = now
        if temperature_C > self.shutoff_temperature_C:
            self.logger.warning(
                (
                    "Temperature exceeds upper limit: {:.1f} > {:.1f}. "
                    "Switching to safe output of {:.3f}."
                ).format(
                    temperature_C,
                    self.shutoff_temperature_C,
                    self.safe_output,
                )
            )
            return self.safe_output
        if temperature_C - self.setpoint_C > self.maximum_overshoot_C:
            return self.safe_output
        return self.pid(temperature_C, self.setpoint_C)

    def rate_sleep(self, period_s: float) -> None:
        time_since_last_update_s = time.monotonic() - self.time_of_last_sleep

        if time_since_last_update_s < period_s:
            time.sleep(period_s - time_since_last_update_s)

        self.time_of_last_sleep = time.monotonic()

    def abort(self) -> None:
        self.pid_cancel.set()

    def set_setpoint(self, setpoint_C: float) -> None:
        with self.setpoint_mtx:
            if setpoint_C is None:
                self.logger.info("Changing set point to None")
            else:
                self.logger.info("Changing set point to {:.1f} C".format(setpoint_C))
            self.setpoint_C = setpoint_C

    def set_temps(self, temps: List[float]) -> None:
        with self.temp_mtx:
            self.temps_C = temps

    def set_dc(self, dc: int) -> None:
        with self.dc_mtx:
            self.dc = dc

    def get_setpoint(self) -> float:
        with self.setpoint_mtx:
            return self.setpoint_C

    def get_temps(self) -> List[float]:
        with self.temp_mtx:
            return self.temps_C

    def get_dc(self) -> int:
        with self.dc_mtx:
            return self.dc

