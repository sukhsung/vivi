const { FFT } = require("fftw-js");

class FFTManager {
  constructor() {
    this.NUM_FFT = null;
    this.plan = null;
  }

  initialize(NUM_FFT) {
    this.NUM_FFT = NUM_FFT;
    if (this.plan !== null) {
      this.plan.dispose();
    }
    this.plan = new FFT(NUM_FFT);
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

    const ffts = [];
    for (let i = 0; i < datas_t.length; i++) {
      // Run FFT
      const output = this.fft(datas_t[i]);
      // Compute magnitude from real/imag pairs
      const magnitudes = this.calculate_mag(output);

      ffts.push(magnitudes);
    }
    return ffts;
  }

  transpose(matrix) {
    return matrix[0].map((_, colIndex) => matrix.map((row) => row[colIndex]));
  }
}

module.exports = { FFTManager };
