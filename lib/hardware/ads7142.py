from typing import Iterable
from smbus2 import SMBus, i2c_msg
from config.logger_manager import LoggerManager


NTC_table = [
    -578, -470, -362, -292, -239, -196, -160, 
    -128, -99,  -73,  -49,  -27,  -6,   14,
    32,   50,   67,   83,   98,   113,  128,
    142,  156,  169,  182,  195,  207,  219,
    231,  243,  255,  266,  277,  289,  299,
    310,  321,  332,  342,  352,  363,  373,
    383,  393,  404,  414,  424,  434,  443,
    453,  463,  473,  483,  493,  503,  513,
    523,  533,  543,  553,  563,  573,  583,
    593,  603,  614,  624,  635,  645,  656,
    667,  677,  688,  699,  711,  722,  733,
    745,  757,  768,  781,  793,  805,  818,
    831,  844,  857,  871,  885,  899,  914,
    929,  944,  959,  976,  992,  1009, 1027, 
    1045, 1063, 1083, 1103, 1124, 1145, 1168,
    1192, 1216, 1242, 1270, 1299, 1329, 1362,
    1397, 1434, 1474, 1518, 1566, 1619, 1678,
    1745, 1821, 1911, 2017, 2148, 2318, 2553,
    2924, 3695, 4466
]


class ADS7142_Reg:
    OPMODE_SEL = 0x1C
    START_SEQUENCE = 0x1E
    nCLK_SEL = 0x19
    DATA_BUFFER_OPMODE = 0x2c
    DOUT_FORMAT_CFG = 0x28
    ABORT_SEQUENCE = 0x1F
    READ_ADDRESS = 0b00010000
    WRITE_ADDRESS = 0b00001000


class ADS7142:
    def __init__(
        self,
        logger: LoggerManager,
        bus_number: int,
        device_address: int,
    ):
        self.logger = logger
        self.bus = SMBus(bus_number)
        self.device_address = device_address

        self.configure_device()
        # Read once to get through first "bad" reading
        self.read_thermistor_values()

    @staticmethod
    def bytes_to_int16(data) -> Iterable[int]:
        return [(data[i] << 8) | data[i+1] for i in range(0, len(data), 2)]

    @staticmethod
    def calculate_temp(val: int) -> int:
        p1 = NTC_table[(val >> 5)]
        p2 = NTC_table[(val >> 5) + 1]
        return p1 + ((p2 - p1) * (val & 0x001F)) / 32

    def read_register(self, register_address: int) -> int:
        write1 = i2c_msg.write(self.device_address, [ADS7142_Reg.READ_ADDRESS, register_address])
        read1 = i2c_msg.read(self.device_address, 1)
        self.bus.i2c_rdwr(write1, read1)
        return list(read1)

    def write_register(
        self,
        register_address: int,
        value: int
    ) -> None:
        write1 = i2c_msg.write(self.device_address, [ADS7142_Reg.WRITE_ADDRESS, register_address, value])
        self.bus.i2c_rdwr(write1)

    def configure_device(self) -> None:
        self.write_register(ADS7142_Reg.OPMODE_SEL, 0b110)
        self.write_register(ADS7142_Reg.nCLK_SEL, 0x0)
        self.write_register(ADS7142_Reg.DATA_BUFFER_OPMODE, 0b000)
        self.write_register(ADS7142_Reg.DOUT_FORMAT_CFG, 0b010)

    def read_thermistor_values(self) -> Iterable[float]:
        self.write_register(ADS7142_Reg.ABORT_SEQUENCE, 1);
        read_data = self.bus.read_i2c_block_data(self.device_address, 0x00, 16*2)
        data = self.bytes_to_int16(read_data)
        data_mC = [0, 0]
        counter = [0, 0]
        accumulate_mC = [0, 0]

        for val in data:
            if val & 0x0001:
                idx = 1 if val & 0b1110 else 0
                counter[idx] += 1
                accumulate_mC[idx] += self.calculate_temp((val & 0xFFF0) >> 4)

        for idx in range(2):
            if counter[idx] != 0:
                accumulate_mC[idx] /= counter[idx]
                data_mC[idx] = accumulate_mC[idx]
            else:
                self.logger.warning(f"ADS7142 channel {idx+1} has no valid readings")
                data_mC[idx] = -1234

        self.write_register(ADS7142_Reg.START_SEQUENCE, 1)
        return [each/10 for each in data_mC]


if __name__ == "__main__":
    from config.config import Config
    import time

    config = Config.from_file("/home/pi/heater_cycle_test/config/config.yaml")
    config.merge(config)
    logger = LoggerManager.get_logger(config.log)  

    device = ADS7142(logger=logger, bus_number=22, device_address=0x1f)
    device.configure_device()
    for _ in range(5):
        time.sleep(0.1)
        print(device.read_thermistor_values())

