# Multithreaded Heater Cycler
This tool controls up to 8 channels of closed loop heating systems.

## Hardware

- **Raspberry Pi**
  - **8x GPIO** Connected to **8x SSRs**
    - [IXYS Integrated Circuits Division CPC1706Y](https://www.digikey.com/en/products/detail/ixys-integrated-circuits-division/CPC1706Y/3077519)
    - Each SSR switches a 48v line to drive heaters.
    - PWM enabled on these GPIO connectors. Can be low-ish frequency software PWM.
    - Approximately 1ms total on+off time, giving 95% efficiency at 50Hz.
    - Check if SSRs get hot at 50Hz with 3.5A load; adjust PWM frequency if necessary or increase to 5mA drive.
  - **1x GPIO** Connected to **Fan Enable Pin**.
  - **1 I2C Line** connected to **8x I2C multiplexer**.
    - [I2C Multiplexer pHAT for Raspberry Pi](https://thepihut.com/products/i2c-multiplexer-phat-for-raspberry-pi)
    - Each multiplexed line connected to one heater board (to read thermistors from onboard ADC).

