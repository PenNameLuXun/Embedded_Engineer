`timescale 1ns/1ps

module tb_counter4;
    reg clk = 0, rst_n = 0, en = 0;
    wire [3:0] cnt;

    always #5 clk = ~clk;

    counter4 dut(.clk(clk), .rst_n(rst_n), .en(en), .cnt(cnt));

    initial begin
        $dumpfile("wave.vcd");
        $dumpvars(0, tb_counter4);
        #20 rst_n = 1;
        #10 en = 1;
        #200 en = 0;
        #50 $finish;
    end

    always @(posedge clk)
        $display("%4t  cnt = %d", $time, cnt);
endmodule
