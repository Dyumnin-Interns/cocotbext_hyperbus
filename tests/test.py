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

    # Writing random data into memory
    data_count=16
    w_data=hbc.generate_random_data(data_count)
    w_addr=0x4
    await hbc.WriteMem(w_addr,w_data)
    
    # Reading from the memory
    r_addr=w_addr
    r_data = await hbc.ReadMem(r_addr,data_count)

    assert w_data==r_data, f'Read-write test failed'
    
