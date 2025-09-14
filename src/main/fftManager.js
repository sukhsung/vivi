const { FFT } = require("fftw-js");
const EventEmitter = require("events");

class FFTManager extends EventEmitter {
  constructor() {
    super();
    this.NUM_FFT = null;
    this.NUM_AVE = null;
    this.NUM_CHANNELS = null;
    this.plan = null;
    this.fft_live = null;
    this.counter_live = null;
    this.fft_sum = null
    this.counter_ave = null;
  }

  initialize(NUM_FFT, NUM_CHANNELS, NUM_AVE) {
    this.NUM_FFT = NUM_FFT;
    if (this.plan !== null) {
      this.plan.dispose();
    }
    this.plan = new FFT(NUM_FFT);

    // TODO: INIT WITH INPUT
    this.NUM_AVE = NUM_AVE;
    this.NUM_CHANNELS = NUM_CHANNELS;

    this.fft_live = this.create2DArray(NUM_CHANNELS, NUM_FFT/2)
    this.fft_sum = this.create2DArray(NUM_CHANNELS, NUM_FFT/2)
    this.fft_ave = this.create2DArray(NUM_CHANNELS, NUM_FFT/2)

    this.counter_live = 0;
  }

  reset_live() {
    for (let ch = 0; ch < this.NUM_CHANNELS; ch++) {
      for (let j = 0; j < this.NUM_FFT/2; j++) {
        this.fft_live[ch][j] = 0.0;
      }
    }
    this.counter_live = 0;
  }

  fft(data) {
    // Output format: [re0, im0, re1, im1, ..., reN, imN]
    if (data.length != this.NUM_FFT) {
      console.log("FFT size is incorrect");
      return null;
    }

    return this.plan.forward(data);
  }

  calculate_mag(data) {
    // Input format: [re0, im0, re1, im1, ..., reN, imN]
    const N = data.length;
    const mag = [];
    for (let j = 0; j < N / 2; j++) {
      const re = data[2 * j];
      const im = data[2 * j + 1];
      mag.push(Math.sqrt(re * re + im * im));
    }
    return mag;
  }

  calc_fft(datas) {
    const datas_t = this.transpose(datas);
    for (let ch = 0; ch < this.NUM_CHANNELS; ch++) {
      // Run FFT
      const output = this.fft(datas_t[ch]);
      // Compute magnitude from real/imag pairs
      const magnitudes = this.calculate_mag(output);

      for (let j = 0; j < this.NUM_FFT/2; j++) {
        this.fft_live[ch][j] += magnitudes[j] / this.NUM_AVE;
        this.fft_sum[ch][j] += magnitudes[j] / this.NUM_AVE;
      }

    }
    this.counter_live += 1;
    this.counter_ave += 1;

    this._print( "Counter "+ this.counter_live )
    if (this.counter_live == this.NUM_AVE) {
      this.emit( 'fft:live-data', {ffts: this.fft_live})
      this.reset_live();
    }
  }

  async calc_ave() {

    for (let ch = 0; ch < this.NUM_CHANNELS; ch++) {
      for (let j = 0; j < this.NUM_FFT/2; j++) {
        this.fft_ave[ch][j] = this.fft_sum[ch][j]/this.counter_ave;
      }

    }

    this.emit( 'fft:live-data', {ffts: this.fft_ave})
  }

  _print(message, header = this.constructor.name, color = "y") {
    let col;
    if (color === "r") {
      col = "\x1b[31m";
    } else if (color === "g") {
      col = "\x1b[32m";
    } else if (color === "y") {
      col = "\x1b[33m";
    }

    if (this.verbose) {
      message = message.split("\n");

      if (message.length <= 1) {
        console.log("\x1b[32m%s:\x1b[0m %s%s\x1b[0m", header, col, message[0]);
      } else {
        console.log("\x1b[32m%s:\x1b[0m", header);
        message.forEach((m) => {
          console.log("    %s%s\x1b[0m", col, m);
        });
      }
    }
  }

  transpose(matrix) {
    return matrix[0].map((_, colIndex) => matrix.map((row) => row[colIndex]));
  }

  // Preallocate a 2D array with given rows and cols
  create2DArray(rows, cols, fill = 0) {
    return Array.from({ length: rows }, () => Array(cols).fill(fill));
  }

}

module.exports = { FFTManager };
