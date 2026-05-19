// 第 01 章 · 半加器 (Half Adder) + testbench
//
// 半加器：S = A ^ B, C = A & B
//
// 跑法：
//     make run-hdl
// 会生成 wave.vcd，可选 gtkwave wave.vcd 看波形。

`timescale 1ns / 1ps

// --------- 被测电路 (Device Under Test) ---------
module half_adder (
    input  wire A,
    input  wire B,
    output wire S,   // sum
    output wire C    // carry
);
    assign S = A ^ B;
    assign C = A & B;
endmodule


// --------- testbench ---------
module tb_half_adder;
    reg  a, b;
    wire s, c;

    half_adder dut (.A(a), .B(b), .S(s), .C(c));

    initial begin
        // 让仿真器把波形写出来
        $dumpfile("wave.vcd");
        $dumpvars(0, tb_half_adder);

        $display("time  a b | s c");
        $display("----  --- | ---");

        a = 0; b = 0; #10 $display("%4t  %b %b | %b %b", $time, a, b, s, c);
        a = 0; b = 1; #10 $display("%4t  %b %b | %b %b", $time, a, b, s, c);
        a = 1; b = 0; #10 $display("%4t  %b %b | %b %b", $time, a, b, s, c);
        a = 1; b = 1; #10 $display("%4t  %b %b | %b %b", $time, a, b, s, c);

        $finish;
    end
endmodule
