from .HBC_FSM import HyperBus_FSM
from cocotb.triggers import Timer
from cocotb.binary import BinaryValue
import cocotb
from cocotb.handle import Release, Freeze, Force
from cocotb.utils import get_sim_time


class HyperBusController(HyperBus_FSM):
    def __init__(self,dut):
        super().__init__()
        self.Init(dut)

        

    def Init(self,dut):
        print("Init...")
        cocotb.start_soon(self.clk_cycle(dut))
        cocotb.start_soon(self.Assign(dut))
        cocotb.start_soon(self.fsm(dut))
        cocotb.start_soon(self.is_rwdsvalid())
        # cocotb.start_soon(self.ca_drive(dut))


    async def Reset(self,dut):
        self.i_rstn=0
        await Timer(100,'ns')
        self.i_rstn=1
        self.log("Waiting for device power-up...")
#TODO: Change power-up time in rtl 
        await Timer(160,'ns')
        self.log('RAM IS READY!!!!!!')

    async def ReadReg(self,addr):
        self.i_cfg_access = 1
        self.i_mem_valid  = 1
        self.i_mem_wstrb  = 0
        self.i_mem_addr   = addr
        
        await Timer(10,'ns')

        self.i_mem_valid=0
        
        await self.wait_until_mem_ready()
        await Timer(20,'ns')
        return self.rx_data(self.mem_rdata,16)
    
    async def WriteReg(self,addr,data):
        self.i_cfg_access = 1
        self.i_mem_wdata=self.swap_halves(data)
        self.i_mem_addr   = addr
        self.i_mem_valid  = 1
        self.i_mem_wstrb  = 15
        
        await Timer(10,'ns')

        self.i_mem_valid=0
        
        await self.wait_until_mem_ready()
        await Timer(20,'ns')
        # return self.rx_data(self.mem_rdata,16)
    
    async def WriteMem(self,addr,data):
        w_addr=addr
        for w_data in data:
            print("--------------------------------------------------")
            self.log("Writing into memory...")
            self.i_cfg_access=0
            self.i_mem_wdata=self.swap_halves(w_data)
            self.i_mem_addr=w_addr
            self.i_mem_valid=1
            self.i_mem_wstrb=15
            await Timer(10,'ns')
            self.i_mem_valid=0

            await self.wait_until_mem_ready()
            self.log('Write operation complete.')
            self.log(f'Address: {hex(w_addr)}   Data: {hex(w_data)}')
            print("--------------------------------------------------")
            await Timer(20,'ns')
            w_addr+=2


    async def ReadMem(self,addr,count):
        r_addr=addr
        r_data=[]
        for i in range(count):
            print("--------------------------------------------------")
            self.log("Reading from memory...")
            self.i_cfg_access=0
            self.i_mem_wstrb=0
            self.i_mem_addr=r_addr
            self.i_mem_valid=1
            await Timer(10,'ns')
            self.i_mem_valid=0
            await self.wait_until_mem_ready()
            r_data.append(self.o_mem_rdata)
            self.log('Read operation complete.')
            self.log(f'Address: {hex(r_addr)}   Data: {hex(self.o_mem_rdata)}')
            print("--------------------------------------------------")    
            # self.log(f'$$$$$$$$ o_mem_rdata {self.rx_data(self.o_mem_rdata,32)}')
            await Timer(20,'ns')
            r_addr+=2
        return r_data

    async def clk_cycle(self,dut):
        while True:
            self.i_clk=0
            await Timer(5,'ns')
            self.i_clk=1
            await Timer(5,'ns')
            self.ck_cycle(dut)

    
    def ck_cycle(self,dut):
        if (not self.i_rstn):
            self.bus_clk = 0
        else:
            self.bus_clk = not self.bus_clk if not self.o_csn0 else 0
        self.o_clk=self.bus_clk
        # dut.ck.value=self.o_clk


    def int_to_8bit_array(self,num):
        if (num==self.highimp_1 or num==self.highimp_8):
            return num
        binary_str = bin(num)[2:]
        padded_binary_str = binary_str.zfill(8)

        return [str(bit) for bit in padded_binary_str]
    
    def arr_io_dq(self,index,value):
        _io_dq=self.int_to_8bit_array(value)
        return _io_dq[index]

    
    async def Assign(self,dut):
        # dut.rwds.value=BinaryValue(self.highimp_1)
        self.drive_dq(dut,self.highimp_8)
        while True:
            if(self.o_dq_de):
                self.drive_dq(dut,self.io_dq)

            if(self.o_rwds_de):
                dut.rwds.value=Force(self.o_rwds)
            else:
                dut.rwds.value=Release()

            dut.csneg.value=(self.o_csn0)
            dut.ck.value=(self.o_clk)
            dut.resetneg.value=(self.o_resetn)
            self.monitor_dq(dut)
            self.i_rwds=dut.rwds.value
            dut.i_clk.value=self.o_mem_ready

            
            await Timer(1,'ns')

    async def wait_100ns(self,dut):
        await Timer(100,'ns')

    def drive_dq(self,dut,value):
        dut.dq7.value=BinaryValue(self.arr_io_dq(0,value))
        dut.dq6.value=BinaryValue(self.arr_io_dq(1,value))
        dut.dq5.value=BinaryValue(self.arr_io_dq(2,value))
        dut.dq4.value=BinaryValue(self.arr_io_dq(3,value))
        dut.dq3.value=BinaryValue(self.arr_io_dq(4,value))
        dut.dq2.value=BinaryValue(self.arr_io_dq(5,value))
        dut.dq1.value=BinaryValue(self.arr_io_dq(6,value))
        dut.dq0.value=BinaryValue(self.arr_io_dq(7,value))

    def monitor_dq(self,dut):
        arr=[dut.dq7.value,
            dut.dq6.value,
            dut.dq5.value,
            dut.dq4.value,
            dut.dq3.value,
            dut.dq2.value,
            dut.dq1.value,
            dut.dq0.value]
        
        binary_str = ''.join(map(str, arr))

        if any(char == 'z' for char in binary_str):
            self.i_dq=0
        else:
            self.i_dq = int(binary_str, 2)

    async def wait_until_mem_ready(self):
        while True:
            await Timer(5,'ns')
            if(self.o_mem_ready):
                break


    
    






        
