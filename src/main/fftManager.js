import { FFT } from "fftw-js";
import { EventEmitter } from "node:events";
import { make_printer } from "instrument-ui/main/util/printer.js";

export class FFTManager extends EventEmitter {
  constructor(verbose = 0) {
    super();
    this.print = make_printer(verbose, "FFTManager");
    this.NUM_FFT = null;
    this.NUM_AVE = null;
    this.NUM_CHANNELS = null;
    this.plan = null;
    this.fft_live = null;
    this.counter_live = null;
    this.fft_sum = null;
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

    this.fft_live = this.create2DArray(NUM_CHANNELS, NUM_FFT / 2);
    this.fft_sum = this.create2DArray(NUM_CHANNELS, NUM_FFT / 2);
    this.fft_ave = this.create2DArray(NUM_CHANNELS, NUM_FFT / 2);

    this.counter_live = 0;
  }

  reset_live() {
    for (let ch = 0; ch < this.NUM_CHANNELS; ch++) {
      for (let j = 0; j < this.NUM_FFT / 2; j++) {
        this.fft_live[ch][j] = 0.0;
      }
    }
    this.counter_live = 0;
  }

  fft(data) {
    // Output format: [re0, im0, re1, im1, ..., reN, imN]
    if (data.length != this.NUM_FFT) {
      this.print("FFT size is incorrect");
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

      for (let j = 0; j < this.NUM_FFT / 2; j++) {
        this.fft_live[ch][j] += magnitudes[j] / this.NUM_AVE;
        this.fft_sum[ch][j] += magnitudes[j] / this.NUM_AVE;
      }
    }
    this.counter_live += 1;
    this.counter_ave += 1;

    this.print("Counter " + this.counter_live);
    if (this.counter_live == this.NUM_AVE) {
      this.emit("fft:live-data", { ffts: this.fft_live });
      this.reset_live();
    }
  }

  async calc_ave() {
    for (let ch = 0; ch < this.NUM_CHANNELS; ch++) {
      for (let j = 0; j < this.NUM_FFT / 2; j++) {
        this.fft_ave[ch][j] = this.fft_sum[ch][j] / this.counter_ave;
      }
    }

    this.emit("fft:live-data", { ffts: this.fft_ave });
  }

  transpose(matrix) {
    return matrix[0].map((_, colIndex) => matrix.map((row) => row[colIndex]));
  }

  // Preallocate a 2D array with given rows and cols
  create2DArray(rows, cols, fill = 0) {
    return Array.from({ length: rows }, () => Array(cols).fill(fill));
  }
}
