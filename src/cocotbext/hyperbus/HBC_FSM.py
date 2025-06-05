from cocotb.binary import BinaryValue
from cocotb.triggers import Timer
import cocotb
import random
from cocotb.utils import get_sim_time
class HyperBus_FSM:
    # FSM States
    IDLE = 0
    CAs = 1
    WR_LATENCY = 2
    WRITE = 3
    READ = 4
    DONE = 5

    # Write Latency
    WRITE_LATENCY = 6 * 2 + 10 - 1

    def __init__(self):

        self.i_clk = 0
        self.i_rstn = 1
        self.i_cfg_access = 0
        self.i_mem_valid = 0
        self.o_mem_ready = 0
        self.i_mem_wstrb = 0
        self.i_mem_addr = 0
        self.i_mem_wdata = 0
        self.o_mem_rdata = 0
        self.o_csn0 = 1
        self.o_csn1 = 1
        self.o_clk = 0
        self.o_clkn = 1
        self.o_dq = 0
        self.i_dq = 0
        self.o_dq_de = 0
        self.o_rwds = 0
        self.i_rwds = 0
        self.o_rwds_de = 0
        self.o_resetn = 1
        self.io_dq=0
        self.io_rwds=0
        self.dq_z_en=0

        # Internal Variables
        self.state = self.IDLE
        self.ca = 0
        self.wdata = 0
        self.wstrb = 0
        self.counter = 0
        self.mem_ready = 0
        self.mem_rdata = 0
        self.rwds_d = 0
        self.bus_clk = 0

        #High-z values
        self.highimp_8='z'
        for i in range(7):
            self.highimp_8+='z'
        self.highimp_1='z'


    def fsm_reset(self):
        self.ca = 0
        self.state = self.IDLE
        self.mem_ready = 0
        self.mem_rdata = 0
        self.counter = 0

    async def fsm(self,dut):
        await Timer(5,'ns')
        while True:
            if not self.i_rstn:
                self.fsm_reset()
            else:
                if self.state == self.IDLE:
                    self.mem_ready = 0
                    if self.i_mem_valid and not self.mem_ready:
                        self.ca=self.update_ca(self.i_mem_wstrb,self.i_cfg_access,self.i_mem_addr)
                        self.wdata = self.i_mem_wdata
                        self.wstrb = self.i_mem_wstrb
                        self.counter = 5
                        self.state = self.CAs

                elif self.state == self.CAs:
                    if self.counter:
                        self.counter -= 1
                    elif self.ca >> 47:
                        self.counter = 3
                        self.state = self.READ
                    else:
                        if self.ca >> 46 & 1:
                            self.counter = 1
                            self.state = self.WRITE
                        else:
                            self.counter = self.WRITE_LATENCY
                            self.state = self.WR_LATENCY

                elif self.state == self.WR_LATENCY:
                    if self.counter:
                        self.counter -= 1
                    else:
                        self.counter = 3
                        self.state = self.WRITE

                elif self.state == self.WRITE:

                    if self.counter:
                        self.counter -= 1
                    else:
                        self.state = self.DONE

                elif self.state == self.READ:
                    
                    if self.rwds_valid():
                        if self.counter == 3:
                            self.mem_rdata = (self.i_dq << 8) | (self.mem_rdata & 0xFFFF00FF)
                        elif self.counter == 2:
                            self.mem_rdata = (self.i_dq) | (self.mem_rdata & 0xFFFFFF00)
                        elif self.counter == 1:
                            self.mem_rdata = (self.i_dq << 24) | (self.mem_rdata & 0x00FFFFFF)
                        elif self.counter == 0:
                            self.mem_rdata = (self.i_dq << 16) | (self.mem_rdata & 0xFF00FFFF)
                        if self.counter:
                            self.counter -= 1
                        else:
                            self.state = self.DONE
                    

                elif self.state == self.DONE:
                    self.mem_ready = 1
                    self.state = self.IDLE

            self.o_csn0 = self.state in [self.IDLE, self.DONE]
            self.o_resetn = self.i_rstn
            self.o_dq = self.ca_words()[self.counter] if self.state == self.CAs else (self.wdata_words()[self.counter] if self.state == self.WRITE else 0)
            self.o_rwds = not self.wstrb_words()[self.counter] if self.state == self.WRITE else 0
            self.o_dq_de = self.state in [self.CAs, self.WRITE]
            self.o_rwds_de = self.state == self.WRITE and not (self.ca >> 46 & 1)
            self.o_mem_ready = self.mem_ready
            self.o_mem_rdata = self.mem_rdata
            self.io_dq= self.o_dq if self.o_dq_de else self.highimp_8
            self.io_rwds=self.o_rwds if self.o_rwds_de else BinaryValue(self.highimp_1)
            await Timer(10,'ns')


    def rwds_valid(self):
        return self.rwds_d or self.i_rwds

    def ca_words(self):
        return [(self.ca >> (8 * i)) & 0xFF for i in range(6)]

    def wdata_words(self):
        if self.ca >> 46 & 1:
            return [(self.wdata >> 8) & 0xFF, self.wdata & 0xFF, (self.wdata >> 24) & 0xFF, (self.wdata >> 16) & 0xFF]
        else:
            return [(self.wdata >> (8 * i)) & 0xFF for i in range(4)]

    def wstrb_words(self):
        return [(self.wstrb >> 1) & 1, self.wstrb & 1, (self.wstrb >> 3) & 1, (self.wstrb >> 2) & 1]
    
    async def is_rwdsvalid(self):
        while True:
            await Timer(5,'ns')
            self.rwds_d=self.i_rwds

    def get_time(self):
        return get_sim_time("ns")
    
    def log(self,msg):
        print(f'[{self.get_time()}]  {msg}')

    def rx_data(self,num, size):
        binary_str = format(num, '032b')
        shrinked_binary_str = binary_str[-size:]
        shrinked_num = int(shrinked_binary_str, 2)
        hex_str = hex(shrinked_num)
        
        return hex_str
    
    def update_ca(self,i_mem_wstrb, i_cfg_access, i_mem_addr):
        
        or_i_mem_wstrb = int(i_mem_wstrb != 0)
        not_or_i_mem_wstrb = int(not or_i_mem_wstrb)

        _CA = 0
        _CA |= not_or_i_mem_wstrb << 47
        _CA |= int(i_cfg_access) << 46
        _CA |= (or_i_mem_wstrb & int(i_cfg_access)) << 45
        _CA &= ~((1 << 45) - (1 << 16))
        _CA |= (i_mem_addr & 0xFFFFFFF8) << 13 
        _CA &= ~0x7 
        _CA |= (i_mem_addr & 0x7) 
        _CA &= (1 << 48) - 1

        return _CA
    
    def swap_halves(self,hex_num):
        hex_str = f"{hex_num:08x}"

        first_half = hex_str[:4]
        second_half = hex_str[4:]

        swapped_hex_str = second_half + first_half
        swapped_hex_num = int(swapped_hex_str, 16)
        
        return swapped_hex_num
    
    def generate_random_data(self,num):
        int_list = []
        for _ in range(num):
            # Generate a random integer within the specified range
            random_int = random.randint(0, 2**32 - 1)
            int_list.append(random_int)
        return int_list



