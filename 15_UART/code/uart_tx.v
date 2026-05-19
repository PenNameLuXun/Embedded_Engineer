// 最小可综合 UART TX
`timescale 1ns/1ps

module uart_tx #(
    parameter CLK_HZ = 50_000_000,
    parameter BAUD   = 115200
)(
    input  wire        clk,
    input  wire        rst_n,
    input  wire [7:0]  tx_data,
    input  wire        tx_start,
    output reg         tx_busy,
    output reg         tx_pin
);
    localparam DIV = CLK_HZ / BAUD;

    reg [15:0] bit_cnt;
    reg [3:0]  bit_idx;
    reg [9:0]  shift;
    reg        busy;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            busy    <= 1'b0;
            tx_pin  <= 1'b1;
            bit_cnt <= 16'd0;
            bit_idx <= 4'd0;
            shift   <= 10'h3FF;
            tx_busy <= 1'b0;
        end else begin
            if (!busy) begin
                tx_pin <= 1'b1;
                if (tx_start) begin
                    busy    <= 1'b1;
                    shift   <= {1'b1, tx_data, 1'b0};  // stop | D7..D0 | start (LSB out first)
                    bit_cnt <= 16'd0;
                    bit_idx <= 4'd0;
                end
            end else begin
                tx_pin <= shift[0];
                if (bit_cnt == DIV - 1) begin
                    bit_cnt <= 16'd0;
                    shift   <= {1'b1, shift[9:1]};
                    if (bit_idx == 4'd9) begin
                        busy <= 1'b0;
                    end else begin
                        bit_idx <= bit_idx + 4'd1;
                    end
                end else begin
                    bit_cnt <= bit_cnt + 16'd1;
                end
            end
            tx_busy <= busy;
        end
    end
endmodule
