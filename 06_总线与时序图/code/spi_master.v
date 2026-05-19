// 极简 SPI 主机 (Mode 0: CPOL=0, CPHA=0) 发一个字节，用波形看时序。
// 跑法： make && gtkwave spi_master.vcd

`timescale 1ns/1ps

module spi_master_demo;
    reg          clk = 0;
    always #5 clk = ~clk;     // 100 MHz 系统时钟

    reg          rst_n = 0;
    reg          start = 0;
    reg  [7:0]   data_in = 8'hA5;

    wire         sck;
    wire         ncs;
    wire         mosi;

    // 简化的 SPI 主机：分频 8，发送一字节
    reg  [3:0]   bit_cnt = 0;
    reg  [2:0]   div     = 0;
    reg          busy    = 0;
    reg          sck_r   = 0;
    reg          ncs_r   = 1;
    reg  [7:0]   shift   = 0;

    assign sck  = sck_r;
    assign ncs  = ncs_r;
    assign mosi = shift[7];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            busy <= 0; ncs_r <= 1; sck_r <= 0; bit_cnt <= 0; div <= 0;
        end else if (!busy && start) begin
            busy   <= 1;
            ncs_r  <= 0;
            shift  <= data_in;
            div    <= 0;
            bit_cnt <= 0;
        end else if (busy) begin
            div <= div + 3'd1;
            if (div == 3'd3) begin              // 半周期翻 SCK
                sck_r <= 1;
            end else if (div == 3'd7) begin
                sck_r <= 0;
                shift <= {shift[6:0], 1'b0};    // MSB first
                bit_cnt <= bit_cnt + 4'd1;
                if (bit_cnt == 4'd7) begin
                    busy  <= 0;
                    ncs_r <= 1;
                end
                div <= 0;
            end
        end
    end

    initial begin
        $dumpfile("spi_master.vcd");
        $dumpvars(0, spi_master_demo);
        #20  rst_n = 1;
        #20  start = 1;
        #10  start = 0;
        #2000 $finish;
    end
endmodule
