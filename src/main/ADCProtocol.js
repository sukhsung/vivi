import { Parser } from "binary-parser";

export class ADCProtocol {
  constructor(board_type, num_channels) {
    this.board_type = board_type;
    this.NUM_CHANNELS = num_channels;
    this.SCALE_24 = 1.0 / (1 << 24);
    this.VREF = 2.5 * 1.02;

    if (this.board_type == "ADC-8") {
      this.HDR_LEN = 16;
      this.i_function = false;
    } else if (this.board_type == "ADC-8x") {
      this.HDR_LEN = 10 + this.NUM_CHANNELS * 2;
      // self.check_i_function()
    }
  }

  getHeaderParser() {
    if (this.board_type === "ADC-8") {
      return new Parser()
        .endianess("little")
        .string("signature", { length: 4 })
        .uint16("rate_div")
        .uint16("sinc_order")
        .array("data", { type: "uint8", length: 2 * this.NUM_CHANNELS });
    } else if (this.board_type === "ADC-8x") {
      return new Parser()
        .endianess("little")
        .string("signature", { length: 8 })
        .uint16("rate_div")
        .array("data", { type: "uint8", length: 2 * this.NUM_CHANNELS });
    } else {
      throw new Error("Unknown board type");
    }
  }

  convert_values(block, gains, bipolar, num) {
    let j = 0;
    let v = 0;
    const volts = Array(num).fill(0.0);

    for (let i = 0; i < gains.length; i++) {
      const g = gains[i];
      if (g === 0) continue;

      // Read 24-bit unsigned int from 3 bytes (little-endian)
      const x = block[j] + (block[j + 1] << 8) + (block[j + 2] << 16);
      let value = x * this.SCALE_24;

      if (bipolar[i]) {
        value = 2.0 * value - 1.0;
      }

      volts[v] = Number(((value * this.VREF) / g).toFixed(9)); // Rounded to 9 digits
      j += 3;
      v += 1;
    }

    return volts;
  }
}
