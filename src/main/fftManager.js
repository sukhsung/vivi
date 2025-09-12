const { FFT } = require("fftw-js");
const EventEmitter = require("events");

class FFTManager extends EventEmitter {
  constructor() {
    super();
    this.NUM_FFT = null;
    this.plan = null;
    this.NUM_AVE = null;
    this.fft_aves = null;
    this.NUM_CHANNELS = null;
    this.ave_counter = null;
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
    this.fft_aves = [];
    let fft_ave;
    for (let ch = 0; ch < this.NUM_CHANNELS; ch++) {
      fft_ave = [];
      for (let j = 0; j < this.NUM_FFT; j++) {
        fft_ave.push(0.0);
      }
      this.fft_aves.push(fft_ave);
    }
    this.ave_counter = 0;
  }

  reset_average() {
    for (let ch = 0; ch < this.NUM_CHANNELS; ch++) {
      for (let j = 0; j < this.NUM_FFT; j++) {
        this.fft_aves[ch][j] = 0.0;
      }
    }
    this.ave_counter = 0;
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

      for (let j = 0; j < this.NUM_FFT; j++) {
        this.fft_aves[ch][j] += magnitudes[j] / this.NUM_AVE;
      }

    }
    this.ave_counter += 1;

    console.log( "Counter "+ this.ave_counter )
    if (this.ave_counter == this.NUM_AVE) {
      this.emit( 'fft:live-data', {ffts: this.fft_aves})
      this.reset_average();
    }
  }

  transpose(matrix) {
    return matrix[0].map((_, colIndex) => matrix.map((row) => row[colIndex]));
  }
}

module.exports = { FFTManager };
