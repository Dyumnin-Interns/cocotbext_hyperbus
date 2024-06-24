# cocotb extension for HyperBus

[![PyPI version](https://badge.fury.io/py/cocotbext-hyperbus.svg)](https://badge.fury.io/py/cocotbext-hyperbus)

## Installation

Installation from pip (release version, stable):

    pip install cocotbext-hyperbus

Installation for active development:

    git clone https://github.com/meeeeet/cocotbext_hyperbus
    pip install -e cocotbext_hyperbus

## Documentation and usage examples

See the `tests` directory for complete testbenches using these modules.

### Configuration

1. Alter the following parameter in the Infineon HyperRAM RTL code to avoid the cocotb having to wait a long time and the simulation crashing.

    ```
    // tdevice values: values for internal delays
    // power-on reset
    specparam tdevice_VCS    = 150;
    // Deep Power Down to Idle wake up time
    specparam tdevice_DPD    = 150;
    // Exit Event from Deep Power Down
    specparam tdevice_DPDCSL = 20;
    // Warm HW reset
    specparam tdevice_RPH    = 40;
    // Refresh time
    specparam tdevice_REF100 = 40;
    // Page Open Time
    specparam tdevice_PO100 = 40;
    ```

2. Make a wrapper module for better experience and make sure to use signal names in lowercase in wrapper module as shown in [`test/wrapper_ram.v`](https://github.com/meeeeet/cocotbext_hyperbus/blob/main/tests/wrapper_ram.v).

### HyperBus

The `HyperBusController` class can be used to drive and receive data from HyperRAM.

To use these modules, import the one you need and connect it to the DUT:

    from cocotbext_hyperbus import HyperBusController
    @cocotb.test()
    async def sample_test(dut):
        hbc=HyperBusController(dut)

#### Methods

* `Reset(dut)`: Reset the _dut_
* `WriteReg(addr,data)`: Write _data_ into register at _addr_
* `ReadReg(addr)`: Read from register at _addr_
* `generate_random_data(len)`: Generate random 32-bit data of _len_ length
* `WriteMem(addr,data)`: Write _data_ into memory at _addr_
* `ReadMem(addr,len)`: Read _len_ 32-bit data from memory starting from _addr_
