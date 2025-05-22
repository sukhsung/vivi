import { UI_Manager } from "./UI_Manager.js";
export { UI_SettingManager };

const GAINS = [128, 64, 32, 16, 8, 1];

class UI_SettingManager extends UI_Manager {
  constructor(verbose=false) {
    super(verbose);
    this.scrolled = false;
    this.labels = [];
  }

  initialize() {
    // Load DOM
    this.cacheDOM({
      TB_sampling: "TB_sampling",
      div_scrollbox: "div_scrollbox",
      div_ADCs: "div_ADCs",
      scroll_indicator: "scroll-indicator",
    });
    this.sampling = parseFloat(this.TB_sampling.value);

    this.register_handler_scroll();
    this.register_handler_sampling();
  }

  onchange_label() {
    for (let i = 0; i < this.NUM_CHANNELS; i++) {
      this.labels[i] = this.TB_labels[i].value;
    }
  }

  register_handler_label(TB_label) {
    TB_label.addEventListener("blur", () => {
      this.onchange_label();
    });

    TB_label.addEventListener("keydown", (evt) => {
      if (evt.key === "Enter") {
        this.onchange_label();
      }
    });
  }

  register_handler_sampling() {
    this.TB_sampling.addEventListener("blur", () => {
      this.onchange_sampling();
    });

    this.TB_sampling.addEventListener("keydown", (evt) => {
      if (evt.key === "Enter") {
        this.onchange_sampling();
      }
    });
  }

  register_handler_scroll() {
    // scroll indicator
    this.div_scrollbox.addEventListener("scroll", () => {
      if (this.scrolled) {
        this.scroll_indicator.style.opacity = 0;
      } else if (this.div_scrollbox.scrollTop > 10) {
        this.scroll_indicator.style.opacity = 0;
        this.scrolled = true;
      } else {
        this.scroll_indicator.style.opacity = 1;
      }
    });
  }

  create_ADC_settings(NUM_CHANNELS) {
    this.NUM_CHANNELS = NUM_CHANNELS;
    this.CB_gains = [];
    this.CB_buffers = [];
    this.CB_polarity = [];
    this.TB_labels = [];

    this.labels = [];
    for (let i = 0; i < this.NUM_CHANNELS; i++) {
      const [div_adc, CB_gain, CB_polarity, CB_buffer, TB_label] =
        this._create_ADC_setting(i + 1);
      this.div_ADCs.appendChild(div_adc);
      this.CB_gains.push(CB_gain);
      this.CB_buffers.push(CB_buffer);
      this.CB_polarity.push(CB_polarity);
      this.TB_labels.push(TB_label);

      this.labels.push(TB_label.value);
      this.register_handler_label(TB_label);
    }
    
    this.update_scroll_visibility()
  }

  update_scroll_visibility(){
    if (this.div_scrollbox.scrollHeight > this.div_scrollbox.clientHeight) {
      this.setHidden(this.scroll_indicator, false);
    } else {
      this.setHidden(this.scroll_indicator, true);
    }
  }

  _create_ADC_setting(channel) {
    const template = document.getElementById("adc-setting-template");
    const clone = template.content.cloneNode(true);

    const wrapper = clone.querySelector("div");
    const labelInput = wrapper.querySelector("input");
    labelInput.value = `Ch ${channel}`;

    const selects = wrapper.querySelectorAll("select");
    const [gainSelect, polaritySelect, bufferSelect] = selects;

    gainSelect.selectedIndex = 5
    polaritySelect.selectedIndex =1
    bufferSelect.selectedIndex =0

    this.CB_add_options(gainSelect, GAINS);
    gainSelect.onchange = () => this.onchange_adc(channel);
    polaritySelect.onchange = () => this.onchange_adc(channel);
    bufferSelect.onchange = () => this.onchange_adc(channel);

    return [wrapper, gainSelect, polaritySelect, bufferSelect, labelInput];
  }

  onchange_adc(channel) {
    const idx = channel - 1;
    const gain = parseInt(this.CB_gains[idx].value);
    const polarity = this.CB_polarity[idx].value === "unipolar" ? 1 : 2;
    const buffer = this.CB_buffers[idx].value === "buffered" ? "b" : "u";

    const data = {
      ch: channel,
      gain: gain,
      polarity: polarity,
      buffer: buffer,
    };

    window.api_setting.setADC(data);
    this.print("Setting ADCs")
  }

  onchange_sampling() {
    this.sampling = parseFloat(this.TB_sampling.value);
    if (isNaN(this.sampling)) {
      this.sampling = 400;
    }

    window.api_setting.setSampling(this.sampling);
    this.print("Setting sampling")
  }

  update_settings(data) {
    this.TB_sampling.value = String(data.sampling);

    for (let i = 0; i < this.NUM_CHANNELS; i++) {
      this.CB_gains[i].selectedIndex = GAINS.indexOf(data.adcs[i].gain);
      this.CB_polarity[i].selectedIndex = data.adcs[i].polarity - 1;

      this.CB_buffers[i].selectedIndex = data.adcs[i].buffer === "u" ? 0 : 1;
    }
  }
}
