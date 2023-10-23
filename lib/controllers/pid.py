import time
from typing import cast, Optional

from config.logger_manager import LoggerManager
from controllers.controller import (
    BaseController,
    InputType,
    Limits,
    OutputType,
    TimeType,
)


class PIDController(BaseController[InputType, OutputType, TimeType]):
    def __init__(
        self,
        logger: LoggerManager,
        kp: float,
        ki: float,
        kd: float,
        output_limits: Limits[OutputType],
        p_limits: Optional[Limits[OutputType]]=None,
        i_limits: Optional[Limits[OutputType]]=None,
        d_limits: Optional[Limits[OutputType]]=None,
    ) -> None:
        self.logger = logger
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limits = output_limits
        self.p_limits = p_limits
        self.d_limits = d_limits
        self.i_limits = i_limits
        self.reset()

    def reset(self) -> None:
        self.last_error = None
        self.last_time = None
        self.integrated_error = 0.0
        
    def set_kp(self, kp: float) -> None:
        self.kp = kp

    def set_ki(self, ki: float):
        self.ki = ki

    def set_kd(self, kd: float):
        self.kd = kd

    def __call__(
        self,
        value: InputType,
        setpoint: InputType,
        t: Optional[TimeType] = None,
    ) -> OutputType:
        if t is None:
            t = cast(TimeType, time.monotonic())
        error = cast(InputType, setpoint - value)

        if self.last_error is None or self.last_time is None:
            dt = 0.0
            dedt = 0.0
        else:
            dt = t - self.last_time
            if dt <= 0.0:
                self.logger.warning("Time delta is nonpositive, setting dedt to 0")
                dt = 0.0
                dedt = 0.0
            else:
                dedt = (error - self.last_error) / dt
        self.integrated_error = self.integrated_error + error * dt

        p_term = self.limit(
            cast(OutputType, error * self.kp),
            self.p_limits,
        )
        i_term = self.limit(
            cast(OutputType, self.integrated_error * self.ki),
            self.i_limits,
        )
        d_term = self.limit(
            cast(OutputType, dedt * self.kd),
            self.d_limits,
        )
        output = self.limit(
            cast(OutputType, p_term + i_term + d_term),
            self.output_limits,
        )

        self.last_error = error
        self.last_time = t
        return output

