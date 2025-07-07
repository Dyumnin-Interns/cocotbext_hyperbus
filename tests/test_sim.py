"""Sample test for hyperbus."""
import os
import cocotb
from cocotbext.hyperbus import HyperBusController
import cocotb_test.simulator


@cocotb.test()
async def sample_test(dut):
    """Simple test for reading and writing from a starting address."""
    hbc = HyperBusController(dut)

    # hbc.Init(dut)
    await hbc.Reset(dut)

    await hbc.WriteReg(0x800, (0x8f1f).to_bytes(2, "big"))
    rx = await hbc.ReadReg(0x800)
    cocotb.log.info(rx.hex())
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

def test_cocotb_sim():
    """Needed for pytest to call cocotb-test."""
    verilog_sources = [
        os.path.join("tests","wrapper_ram.v"),
        os.path.join("tests","s27kl0641.v"),
    ]

    cocotb_test.simulator.run(
        toplevel="HyperRAM_wrapper",
        module="tests.test_sim",
        toplevel_lang="verilog",
        verilog_sources=verilog_sources,
        sim="icarus",
        sim_build="sim_build/test",
    )
