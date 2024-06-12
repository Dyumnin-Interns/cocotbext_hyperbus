import cocotb
from cocotbext_hyperbus import HyperBusController

@cocotb.test()
async def sample_test(dut):
    hbc=HyperBusController(dut)

    # hbc.Init(dut)
    await hbc.Reset(dut)
    Rx = await hbc.ReadReg(0)
    print(Rx)
    Rx = await hbc.ReadReg(2)
    print(Rx)
    # await hbc.WriteReg(2048,0xcf8f)
    Rx = await hbc.ReadReg(2048)
    print(Rx)
    Rx = await hbc.ReadReg(2049)
    print(Rx)

    await hbc.WriteMem(16,0xDEADBEEF)
    await hbc.WriteMem(0x13,0x1A2B3C4D)
    Rx = await hbc.ReadMem(16)
    print(Rx)

    Rx = await hbc.ReadMem(0x13)
    print(Rx)
    # await hbc.wait_100ns(dut)
    
