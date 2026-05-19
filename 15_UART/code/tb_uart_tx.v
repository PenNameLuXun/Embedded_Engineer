`timescale 1ns/1ps

module tb_uart_tx;
    // 用小一点的时钟和波特率让仿真快些；比例与 50 MHz / 115200 类似
    localparam CLK_HZ = 1_000_000;
    localparam BAUD   = 100_000;

    reg        clk = 0;
    reg        rst_n = 0;
    reg [7:0]  data;
    reg        start;
    wire       busy, tx;

    always #500 clk = ~clk;   // 1 MHz

    uart_tx #(.CLK_HZ(CLK_HZ), .BAUD(BAUD)) dut (
        .clk(clk), .rst_n(rst_n),
        .tx_data(data), .tx_start(start),
        .tx_busy(busy), .tx_pin(tx)
    );

    initial begin
        $dumpfile("wave.vcd");
        $dumpvars(0, tb_uart_tx);
        data  = 8'h41;        // 'A' = 0100_0001
        start = 0;
        rst_n = 0;
        #2000 rst_n = 1;
        #2000 start = 1;
        #1000 start = 0;
        #200000 $finish;       // 跑完一帧足够
    end
endmodule
