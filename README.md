# cocotb extension for HyperBus

[![PyPI version](https://badge.fury.io/py/cocotbext-hyperbus.svg)](https://badge.fury.io/py/cocotbext-hyperbus)

GitHub repository: https://github.com/meeeeet/cocotbext_hyperbus

## Installation

Installation from pip (release version, stable):

    pip install cocotbext-uart

Installation for active development:

    git clone https://github.com/meeeeet/cocotbext_hyperbus
    pip install -e cocotbext_hyperbus

## Documentation and usage examples

See the `tests` directory for complete testbenches using these modules.

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
* `WriteMem(addr,data)`: Write _data_ into memory at _addr_
* `ReadReg(count)`: Read from memory at _addr_
