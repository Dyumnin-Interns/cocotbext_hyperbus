`timescale 1ns/1ns
module HyperRAM_wrapper(
    dq7      ,
    dq6      ,
    dq5      ,
    dq4      ,
    dq3      ,
    dq2      ,
    dq1      ,
    dq0      ,
    rwds     ,
    csneg    ,
    ck       ,
    resetneg ,
);

inout  dq7;
inout  dq6;
inout  dq5;
inout  dq4;
inout  dq3;
inout  dq2;
inout  dq1;
inout  dq0;
inout  rwds;
input  csneg;
input  ck;
input  resetneg;


wire [7:0] dq;
assign dq={dq7,dq6,dq5,dq4,dq3,dq2,dq1,dq0};


s27kl0641
	#(
	.TimingModel("S27KL0641DABHI000"))
RAM
(
    dq7      ,
    dq6      ,
    dq5      ,
    dq4      ,
    dq3      ,
    dq2      ,
    dq1      ,
    dq0      ,
    rwds     ,

    csneg    ,
    ck       ,
    resetneg
    );


	initial begin
		// #160e6;
		$dumpfile("dump.vcd");
		$dumpvars;
	end


endmodule
