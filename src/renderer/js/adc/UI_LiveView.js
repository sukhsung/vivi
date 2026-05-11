import { UI_Manager } from "../../../../node_modules/instrument-ui/src/renderer/js/UI_Manager.js";

export { UI_LiveviewManager };

class UI_LiveviewManager extends UI_Manager {
  constructor() {
    super();
  }

  initialize() {
    // Load DOM
    this.cacheDOM({
      div_livefft: "livefft",
      canvas: "canvas_live",
    });

    this.data = {};
    this.options = {
      responsive: true,
      maintainAspectRatio: false, // important!
      scales: {
        x: {
          display: true,
        },
        y: {
          display: false,
          type: "logarithmic",
        },
      },
    };

    this.chart = new Chart(this.canvas, {
      type: "scatter",
      data: this.data,
      options: this.options,
    });

    this.chart.zooming = false;
  }

  init_plot(NUM_CHANNELS, NUM_FFT, sampling, labels) {
    this.sampling = sampling;
    this.dk = sampling / NUM_FFT;
    this.NUM_CHANNELS = NUM_CHANNELS;
    this.NUM_FFT = NUM_FFT;
    this.chart.data.datasets = [];
    this.freq = Array.from({ length: NUM_FFT / 2 }, (_, j) => j * this.dk);

    for (let i = 0; i < NUM_CHANNELS; i++) {
      let data = [];
      for (let j = 0; j < NUM_FFT / 2; j++) {
        data.push({ x: this.freq[j], y: 0 });
      }

      let dataset = {
        showLine: true,
        label: labels[i],
        data: data,
        fill: false,
        borderWidth: 1,
        pointRadius: 0,
        animation: false,
      };

      this.chart.data.datasets.push(dataset);
    }
    this.chart.options.scales.x.max = this.sampling / 2;

    this.chart.update();
  }

  received_liveData(data) {
    this.set_data(data);
  }

  set_data(specs) {
    var maxX = Number.NEGATIVE_INFINITY;
    for (let i = 0; i < this.NUM_CHANNELS; i++) {
      const dataset = this.chart.data.datasets[i].data;
      for (let j = 0; j < this.NUM_FFT / 2; j++) {
        if (specs[i][j] > maxX) {
          maxX = specs[i][j];
        }
        dataset[j].y = specs[i][j];
      }
    }

    this.chart.update();
  }

  resize() {
    this.chart.resize();
  }
}
