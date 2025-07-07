"""HyperBusController class."""
from .hbc_fsm import HyperBus_FSM
from cocotb.triggers import Timer
from cocotb.binary import BinaryValue
import cocotb
from cocotb.handle import Release, Force, SimHandleBase
from typing import Union, List


class HyperBusController(HyperBus_FSM):
    """HyperBus Controller class with methods.

    Reset, ReadReg, WriteReg, ReadMem, WriteMem, clk_cycle, ck_cycle, int_to_8bit_array, arr_io_dq, Assign, wait_100ns, drive_dq, monitor_dq, wait_until_mem_ready.
    """

    def __init__(self, dut: SimHandleBase) -> None:
        """Initialization."""
        super().__init__()
        self.Init(dut)

    def Init(self, dut: SimHandleBase) -> None:
        """Initialize clock, Controller FSM and connects dut with controllor."""
        self.log("Init...")
        cocotb.start_soon(self.clk_cycle(dut))
        cocotb.start_soon(self.Assign(dut))
        cocotb.start_soon(self.fsm(dut))
        cocotb.start_soon(self.is_rwdsvalid())
        # cocotb.start_soon(self.ca_drive(dut))

    async def Reset(self, dut: SimHandleBase) -> None:
        """Reset based on timing requirement of the rtl model."""
        self.i_rstn = 0
        await Timer(100, "ns")
        self.i_rstn = 1
        self.log("Waiting for device power-up...")
        # TODO: Change power-up time in rtl
        await Timer(160, "ns")
        self.log("RAM IS READY!!!!!!")

    async def ReadReg(self, addr: int) -> bytes:
            """Reads from a register based on the address, returns 2 bytes."""
            self.i_cfg_access = 1
            self.i_mem_valid = 1
            self.i_mem_wstrb = 0
            self.i_mem_addr = addr
            await Timer(10, "ns")
            self.i_mem_valid = 0
            await self.wait_until_mem_ready()
            await Timer(20, "ns")

            reg_value = self.mem_rdata & 0xFFFF  # Directly use as int
            return reg_value.to_bytes(2, byteorder="big")  # or 'little' if system is little-endian

    async def WriteReg(self, addr: int, data: bytes) -> None:
        """Writes 2 bytes to a register based on the address."""
        expected_bytes = 2
        if len(data) != expected_bytes:
            raise ValueError("WriteReg expects exactly 2 bytes.")

        int_data = int.from_bytes(data, byteorder="big")  # or 'little' if required
        self.i_cfg_access = 1
        self.i_mem_wdata = self.swap_halves(int_data)
        self.i_mem_addr = addr
        self.i_mem_valid = 1
        self.i_mem_wstrb = 0xF
        await Timer(10, "ns")
        self.i_mem_valid = 0
        await self.wait_until_mem_ready()
        await Timer(20, "ns")


    async def WriteMem(self, addr: int, data: bytes) -> None:
        """Writes the memory content form the starting address for specified bytes of data.

        Each transaction is 4 bytes.
        """
        w_addr = addr

        # Convert byte stream into list of 32-bit packets (little-endian)
        padded_data = data
        if (len(data) % 4) != 0:
            padding = 4 - (len(data) % 4)
            padded_data = data + b"\x00" * padding

        b32_list = []
        for i in range(0, len(padded_data), 4):
            val = (
                (padded_data[i + 0])
                | (padded_data[i + 1] << 8)
                | (padded_data[i + 2] << 16)
                | (padded_data[i + 3] << 24)
            )
            b32_list.append(val)

        for w_data in b32_list:
            self.log("--------------------------------------------------")
            self.log("Writing into memory...")
            self.i_cfg_access = 0
            self.i_mem_wdata = self.swap_halves(w_data)
            self.i_mem_addr = w_addr
            self.i_mem_valid = 1
            self.i_mem_wstrb = 15
            await Timer(10, "ns")
            self.i_mem_valid = 0

            await self.wait_until_mem_ready()
            self.log("Write operation complete.")
            self.log(f"Address: {hex(w_addr)}   Data: {hex(w_data)}")
            self.log("--------------------------------------------------")
            await Timer(20, "ns")
            w_addr += 2

    async def ReadMem(self, addr: int, count: int) -> bytes:
        """Reads the memory content form the starting address for a specified number of bytes.

        Each transaction is 4 bytes.
        """
        r_addr = addr
        r_data = []

        count_32b = count // 4
        count_rem = count % 4
        if count_rem > 0:
            count_32b += 1

        for _i in range(count_32b):
            self.log("--------------------------------------------------")
            self.log("Reading from memory...")
            self.i_cfg_access = 0
            self.i_mem_wstrb = 0
            self.i_mem_addr = r_addr
            self.i_mem_valid = 1
            await Timer(10, "ns")
            self.i_mem_valid = 0
            await self.wait_until_mem_ready()
            r_data.append(self.o_mem_rdata)
            self.log("Read operation complete.")
            self.log(f"Address: {hex(r_addr)}   Data: {hex(self.o_mem_rdata)}")
            self.log("--------------------------------------------------")
            # self.log(f"$$$$$$$$ o_mem_rdata {self.rx_data(self.o_mem_rdata,32)}")
            await Timer(20, "ns")
            r_addr += 2

        # Convert list of 32-bit packets back into bytes (little-endian)
        byte_data = []
        for val in r_data:
            byte_data.append((val >> 0) & 0xFF)
            byte_data.append((val >> 8) & 0xFF)
            byte_data.append((val >> 16) & 0xFF)
            byte_data.append((val >> 24) & 0xFF)

        return bytes(byte_data[:count])

    async def clk_cycle(self, dut: SimHandleBase) -> None:
        """Generate the clock for the test."""
        while True:
            self.i_clk = 0
            await Timer(5, "ns")
            self.i_clk = 1
            await Timer(5, "ns")
            self.ck_cycle(dut)

    def ck_cycle(self, dut: SimHandleBase) -> None:
        """Updates the derived clock based on reset and chip select lines."""
        if not self.i_rstn:
            self.bus_clk = 0
        else:
            self.bus_clk = not self.bus_clk if not self.o_csn0 else 0
        self.o_clk = self.bus_clk
        # dut.ck.value=self.o_clk

    def int_to_8bit_array(self, num: Union[int, str]) -> Union[str, List[str]]:
        """Converts Integer into a 8 bit binary string array."""
        if num in (self.highimp_1, self.highimp_8):
            return str(num)
        binary_str = bin(int(num))[2:]
        padded_binary_str = binary_str.zfill(8)
        return [str(bit) for bit in padded_binary_str]

    def arr_io_dq(self, index: int, value: Union[int, str]) -> str:
        """Returns the bit at an index for the 8 bit array."""
        _io_dq = self.int_to_8bit_array(value)
        return _io_dq[index]

    async def Assign(self, dut: SimHandleBase) -> None:
        """Drives and Monitors signals between controllor and dut."""
        # dut.rwds.value=BinaryValue(self.highimp_1)
        self.drive_dq(dut, self.highimp_8)
        while True:
            if self.o_dq_de:
                self.drive_dq(dut, self.io_dq)

            if self.o_rwds_de:
                dut.rwds.value = Force(self.o_rwds)
            else:
                dut.rwds.value = Release()

            dut.csneg.value = self.o_csn0
            dut.ck.value = self.o_clk
            dut.resetneg.value = self.o_resetn
            self.monitor_dq(dut)
            self.i_rwds = dut.rwds.value
            await Timer(1, "ns")

    async def wait_100ns(self, dut: SimHandleBase) -> None:
        """Waits for 100ns."""
        await Timer(100, "ns")

    def drive_dq(self, dut: SimHandleBase, value: Union[int, str]) -> None:
        """Drives the data bus."""
        dut.dq7.value = BinaryValue(self.arr_io_dq(0, value))
        dut.dq6.value = BinaryValue(self.arr_io_dq(1, value))
        dut.dq5.value = BinaryValue(self.arr_io_dq(2, value))
        dut.dq4.value = BinaryValue(self.arr_io_dq(3, value))
        dut.dq3.value = BinaryValue(self.arr_io_dq(4, value))
        dut.dq2.value = BinaryValue(self.arr_io_dq(5, value))
        dut.dq1.value = BinaryValue(self.arr_io_dq(6, value))
        dut.dq0.value = BinaryValue(self.arr_io_dq(7, value))

    def monitor_dq(self, dut: SimHandleBase) -> None:
        """Moniters the data bus."""
        arr = [
            dut.dq7.value,
            dut.dq6.value,
            dut.dq5.value,
            dut.dq4.value,
            dut.dq3.value,
            dut.dq2.value,
            dut.dq1.value,
            dut.dq0.value,
        ]
        binary_str = "".join(map(str, arr))

        if any(char == "z" for char in binary_str):
            self.i_dq = 0
        else:
            self.i_dq = int(binary_str, 2)

    async def wait_until_mem_ready(self) -> None:
        """Continously polls for every half clock cycle to check if the memory is ready."""
        while True:
            await Timer(5, "ns")
            if self.o_mem_ready:
                break
