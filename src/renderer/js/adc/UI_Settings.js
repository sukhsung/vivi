import { UI_Manager } from "../../../../node_modules/instrument-ui/src/renderer/js/UI_Manager.js";
export { UI_SettingManager };

const GAINS = [128, 64, 32, 16, 8, 1];

class UI_SettingManager extends UI_Manager {
  constructor(verbose = false) {
    super(verbose);
    this.scrolled = false;
    this.labels = [];
  }

  initialize() {
    // Load DOM
    this.cacheDOM({
      TB_sampling: "TB_sampling",
      CB_allGains: "CB_allGains",
      div_scrollbox: "div_scrollbox",
      div_ADCs: "div_ADCs",
      scroll_indicator: "scroll-indicator",
      gradient_t: "adc-gradient-t",
      gradient_b: "adc-gradient-b",
    });
    this.sampling = parseFloat(this.TB_sampling.value);
    this.CB_allGains.selectedIndex = 5;
    this.CB_add_options(this.CB_allGains, GAINS);

    this.register_handler_scroll();
    this.register_handler_sampling();
    this.CB_allGains.onchange = () => this.onchange_allGains();
  }

  received_disconnected() {
    this.remove_ADC_settings();
  }

  async onclick_disconnect() {
    // this.PB_connect.innerHTML = 'Disonnecting...'
    window.api_connection.disconnectDevice();
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

  onchange_allGains() {
    const idx_option = this.CB_allGains.selectedIndex;

    for (let i = 0; i < this.NUM_CHANNELS; i++) {
      this.CB_gains[i].selectedIndex = idx_option;
    }

    const gain = parseInt(this.CB_allGains.value);

    const data = {
      gain: gain,
    };

    window.api_vivi.add_request({
      type: "set_all_gain",
      data: data,
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
      this.update_scroll_visibility();
    });
  }

  remove_ADC_settings() {
    this.NUM_CHANNELS = null;
    this.CB_gains = [];
    this.CB_buffers = [];
    this.CB_polarity = [];
    this.TB_labels = [];
    this.labels = [];
    this.div_ADCs.innerHTML = "";
  }

  async create_ADC_settings(NUM_CHANNELS) {
    this.NUM_CHANNELS = NUM_CHANNELS;
    this.CB_gains = [];
    this.CB_buffers = [];
    this.CB_polarity = [];
    this.TB_labels = [];

    this.labels = [];
    for (let i = 0; i < this.NUM_CHANNELS; i++) {
      const [div_adc, CB_gain, CB_polarity, CB_buffer, TB_label] =
        await this._create_ADC_setting(i + 1);
      this.div_ADCs.appendChild(div_adc);
      this.CB_gains.push(CB_gain);
      this.CB_buffers.push(CB_buffer);
      this.CB_polarity.push(CB_polarity);
      this.TB_labels.push(TB_label);

      this.labels.push(TB_label.value);
      this.register_handler_label(TB_label);
    }

    this.update_scroll_visibility();
  }

  update_scroll_visibility() {
    const scrollHeight = this.div_scrollbox.scrollHeight;
    const clientHeight = this.div_scrollbox.clientHeight;

    const scroll_available = scrollHeight > clientHeight;

    this.setHidden(this.scroll_indicator, !scroll_available);

    if (scroll_available) {
      const atTop = this.div_scrollbox.scrollTop <= 10;
      const atBot =
        this.div_scrollbox.scrollTop + clientHeight >= scrollHeight - 10;

      if (atTop) {
        this.setHidden(this.gradient_t, true);
      } else {
        this.setHidden(this.gradient_t, false);
      }

      if (atBot) {
        this.setHidden(this.gradient_b, true);
      } else {
        this.setHidden(this.gradient_b, false);
      }
    } else {
      this.setHidden(this.gradient_t, true);
      this.setHidden(this.gradient_b, true);
    }
  }

  onclick_collapse(channel) {
    const wrapper = this.div_ADCs.childNodes[channel - 1];
    const body = wrapper.querySelector(".adc-settings-body");
    const icon = wrapper.querySelector("svg");

    body.classList.toggle("hidden");
    icon.classList.toggle("rotate-180"); // Optional: rotate arrow

    this.update_scroll_visibility();
  }

  async _create_ADC_setting(channel) {
    const template = await this.import_template(
      "./templates/template_adc_setting.html",
    );
    const clone = template.content.cloneNode(true);

    const wrapper = clone.querySelector("div");
    const div_label = wrapper.querySelector("div").querySelector("div");
    div_label.innerHTML = `ADC ${channel}`;
    const labelInput = wrapper.querySelector("input");
    labelInput.value = `Ch ${channel}`;

    const collapse = wrapper.querySelector("button");

    const selects = wrapper.querySelectorAll("select");
    const [gainSelect, polaritySelect, bufferSelect] = selects;

    gainSelect.selectedIndex = 5;
    polaritySelect.selectedIndex = 1;
    bufferSelect.selectedIndex = 0;

    this.CB_add_options(gainSelect, GAINS);
    gainSelect.onchange = () => this.onchange_adc(channel);
    polaritySelect.onchange = () => this.onchange_adc(channel);
    bufferSelect.onchange = () => this.onchange_adc(channel);
    collapse.onclick = () => this.onclick_collapse(channel);

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

    window.api_vivi.add_request({
      type: "set_adc",
      data: data,
    });
    this.print("Setting ADCs");
  }

  onchange_sampling() {
    this.sampling = parseFloat(this.TB_sampling.value);
    if (isNaN(this.sampling)) {
      this.sampling = 400;
    }

    window.api_vivi.add_request({
      type: "set_sampling",
      value: this.sampling,
    });
    this.print("Setting sampling");
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
