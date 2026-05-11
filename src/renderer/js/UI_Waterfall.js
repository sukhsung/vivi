import { UI_Manager } from "../../../node_modules/instrument-ui/src/renderer/js/UI_Manager.js";
import { colormap } from "./util/colormap.js";

export { UI_WaterfallManager };

const colormaps = ["Viridis", "Inferno", "Plasma", "Magma", "Gray"];

class UI_WaterfallManager extends UI_Manager {
  constructor() {
    super();

    this.idx_cmap = 0;
    this.cmap = new colormap(colormaps[this.idx_cmap]);
  }

  initialize() {
    // Load DOM
    this.cacheDOM({
      div_waterfall: "waterfall",
      canvas: "canvas_waterfall",
      PB_cmap: "PB_cmap",
      div_tabList: "tabList",
    });

    this.PB_cmap.onclick = () => this.onclick_cmap();

    // Canvas
    this.ctx = this.canvas.getContext("2d");

    this.aspect = this.canvas.width / this.canvas.height;
    // Create an offscreen canvas with the ImageData size
    this.offscreen = document.createElement("canvas");
    this.ctx_off = this.offscreen.getContext("2d");

  }

  create_tabs( NUM_CHANNELS ) {
    this.NUM_CHANNELS = NUM_CHANNELS
    this.tabs = [];

    for (let i = 0; i < this.NUM_CHANNELS; i++) {
      this.tabs.push(document.createElement("a"));
      this.div_tabList.appendChild(this.tabs[i]);
      this.tabs[i].innerHTML = `Ch ${i + 1}`;
      this.tabs[i].onclick = () => {
        this.onclick_tab(i);
      };
      this.tabs[i].classList.add("tab");
    }
    this.ch_idx = 0;
    this.tabs[0].classList.add("tab_active");
  }

  received_disconnected() {
    this.tabs = [];
    this.div_tabList.innerHTML=""
  }

  toggle_cmap() {
    this.idx_cmap += 1;
    this.idx_cmap %= colormaps.length;
    this.cmap.set_cmap(colormaps[this.idx_cmap]);
  }

  set_channel(ch) {
    this.ch_idx = ch - 1;
    this.updateCanvas();
  }

  init_plot(NUM_CHANNELS, NUM_FFT) {
    this.NUM_CHANNELS = NUM_CHANNELS;

    this.num_k = NUM_FFT / 2;
    this.num_t = Math.min(Math.round(this.num_k * this.aspect), 256);


    this.offscreen.width = this.num_t;
    this.offscreen.height = this.num_k;
    this.imageData = this.ctx_off.createImageData(this.num_t, this.num_k);

    this.ctx.imageSmoothingEnabled = false;
    this.ctx.patternQuality = "best";

    this.ctx_off.putImageData(this.imageData, 0, 0);
    this.ctx.drawImage(
      this.offscreen,
      0,
      0,
      this.canvas.width,
      this.canvas.height,
    );

    this.data = [];
    for (let idx = 0; idx < this.NUM_CHANNELS; idx++) {
      let cur_data = [];
      for (let t = 0; t < this.num_t; t++) {
        cur_data.push(new Array(this.num_k).fill(null));
      }
      this.data.push(cur_data);
    }

    this.updateCanvas();
  }

  updateCanvas() {
    let minmax = this.getMinMax(this.data[this.ch_idx]);

    for (let k = 0; k < this.num_k; k++) {
      for (let t = 0; t < this.num_t; t++) {
        const idx = (k * this.num_t + t) * 4;

        let val;

        if (this.data[this.ch_idx][t][this.num_k - k - 1] == null) {
          val = 0;
        } else {
          const data_norm =
            (this.data[this.ch_idx][t][this.num_k - k - 1] - minmax.min) /
            (minmax.max - minmax.min);
          val = Math.round(data_norm * 255);
        }

        const rgb = this.cmap.get(val);
        this.imageData.data[idx] = Math.round(255 * rgb[0]); // R
        this.imageData.data[idx + 1] = Math.round(255 * rgb[1]); // G
        this.imageData.data[idx + 2] = Math.round(255 * rgb[2]); // B
        this.imageData.data[idx + 3] = 255; // A
      }
    }

    this.ctx_off.putImageData(this.imageData, 0, 0);
    this.ctx.drawImage(
      this.offscreen,
      0,
      0,
      this.canvas.width,
      this.canvas.height,
    );
  }

  new_spectrum(data_in) {
    for (let idx = 0; idx < this.NUM_CHANNELS; idx++) {
      const data_new = [];
      for (let k = 0; k < this.num_k; k++) {
        data_new.push(Math.log10(data_in[idx][k]));
      }
      // this.data[idx].pop()
      // this.data[idx].unshift( data_new )
      this.data[idx].shift();
      this.data[idx].push(data_new);
    }
    this.updateCanvas();
  }

  getMinMax(matrix) {
    let min = Infinity;
    let max = -Infinity;

    for (const row of matrix) {
      for (const val of row) {
        if (val < min) min = val;
        if (val > max) max = val;
      }
    }

    return { min, max };
  }

  onclick_tab(idx) {
    this.print(`Ch ${idx + 1} Activated`);

    for (let i = 0; i < this.NUM_CHANNELS; i++) {
      if (idx == i) {
        this.tabs[i].classList.add("tab_active");
      } else {
        this.tabs[i].classList.remove("tab_active");
      }
    }

    this.set_channel(idx + 1);
  }

  onclick_cmap() {
    this.toggle_cmap();
    this.PB_cmap.innerHTML = this.cmap.name;
  }

  received_liveData(data) {
    this.new_spectrum(data);
  }
}
