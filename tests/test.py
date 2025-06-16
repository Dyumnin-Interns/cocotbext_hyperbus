"""Sample test for hyperbus."""
import cocotb
from cocotbext_hyperbus import HyperBusController

@cocotb.test()
async def sample_test(dut):
    """Simple test for reading and writing from a starting address."""
    hbc=HyperBusController(dut)

    # hbc.Init(dut)
    await hbc.Reset(dut)
    rx = await hbc.ReadReg(0)
    cocotb.log.info(rx)
    rx = await hbc.ReadReg(2)
    cocotb.log.info(rx)
    # await hbc.WriteReg(2048,0xcf8f)
    rx = await hbc.ReadReg(2048)
    cocotb.log.info(rx)
    rx = await hbc.ReadReg(2049)
    cocotb.log.info(rx)

    # Writing random data into memory
    data_count=16
    w_data=hbc.generate_random_data(data_count)
    w_addr=0x4
    await hbc.WriteMem(w_addr,w_data)

    # Reading from the memory
    r_addr=w_addr
    r_data = await hbc.ReadMem(r_addr,data_count)

    if w_data == r_data:
        cocotb.log.info("Written and read data match exactly.")
    else:
        cocotb.log.error("Data mismatch!")
