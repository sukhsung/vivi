import { UI_DeviceManager } from "./splash/UI_DeviceManager.js";
import { UI_TerminalManager } from "./splash/UI_Terminal.js";
import { UI_InfoManager } from "../../../node_modules/instrument-ui/src/renderer/js/splash/UI_InfoManager.js";

import { UI_PanelManager } from "./UI_PanelManager.js";
import { UI_LogManager } from "./UI_LogManager.js";

import { UI_SettingManager } from "./adc/UI_Settings.js";
import { UI_AcquisitionManager } from "./adc/UI_Acquisition.js";
import { UI_LiveviewManager } from "./adc/UI_LiveView.js";
import { UI_WaterfallManager } from "./adc/UI_Waterfall.js";

import { UI_KeyboardManager } from "../../../node_modules/instrument-ui/src/renderer/js/UI_Keyboard.js";
import { make_printer } from "../../../node_modules/instrument-ui/src/common/printer.js";

const verbose = true;

let CONFIG = {};

// UI managers own renderer state and DOM updates.
const device_manager = new UI_DeviceManager();
const vivi_manager = new UI_PanelManager(verbose);
const log_manager = new UI_LogManager();
const setting_manager = new UI_SettingManager(verbose);
const acquisition_manager = new UI_AcquisitionManager();
const liveview_manager = new UI_LiveviewManager();
const waterfall_manager = new UI_WaterfallManager();
const terminal_manager = new UI_TerminalManager();

let info_manager;
const keyboard_manager = new UI_KeyboardManager();

const print = make_printer(verbose, "renderer", false);

// Initial renderer setup.
async function initialize() {
  CONFIG = await window.api_app.get_config();
  const APP_INFO = await window.api_app.get_info();
  info_manager = new UI_InfoManager(APP_INFO.url, APP_INFO.copyright);
  await device_manager.initialize(CONFIG);
  await vivi_manager.initialize();
  log_manager.initialize();
  setting_manager.initialize();
  acquisition_manager.initialize();
  liveview_manager.initialize();
  waterfall_manager.initialize();
  terminal_manager.initialize();
  await info_manager.initialize();
  await keyboard_manager.initialize();
}

// Renderer-local UI events.
function attachUIListeners() {
  acquisition_manager.addEventListener("start-view", () => {
    const NUM_FFT = acquisition_manager.NUM_FFT;
    const NUM_AVE = acquisition_manager.NUM_AVE;
    const t_acquire = 0;
    const t_delay = acquisition_manager.t_delay;
    const labels = setting_manager.labels;
    const NUM_CHANNELS = setting_manager.NUM_CHANNELS;
    const sampling = setting_manager.sampling;
    liveview_manager.init_plot(NUM_CHANNELS, NUM_FFT, sampling, labels);
    waterfall_manager.init_plot(NUM_CHANNELS, NUM_FFT);
    acquisition_manager.start_acquisition(
      NUM_FFT,
      NUM_AVE,
      t_acquire,
      t_delay,
      labels,
    );
  });

  acquisition_manager.addEventListener("start-acquire", () => {
    const NUM_FFT = acquisition_manager.NUM_FFT;
    const NUM_AVE = acquisition_manager.NUM_AVE;
    const t_acquire = acquisition_manager.t_acquire;
    const t_delay = acquisition_manager.t_delay;
    const labels = setting_manager.labels;
    const NUM_CHANNELS = setting_manager.NUM_CHANNELS;
    const sampling = setting_manager.sampling;

    liveview_manager.init_plot(NUM_CHANNELS, NUM_FFT, sampling, labels);
    waterfall_manager.init_plot(NUM_CHANNELS, NUM_FFT);
    acquisition_manager.start_acquisition(
      NUM_FFT,
      NUM_AVE,
      t_acquire,
      t_delay,
      labels,
    );
  });
}

function attachWindowControls() {
  document
    .getElementById("PB_win_min")
    .addEventListener("click", () => window.api_window.minimize());
  document
    .getElementById("PB_win_max")
    .addEventListener("click", () => window.api_window.maximize());
  document
    .getElementById("PB_win_close")
    .addEventListener("click", () => window.api_window.close());
}

// App startup wires DOM controls after the document is available.
window.addEventListener("load", async () => {
  attachWindowControls();
  await initialize();
  attachUIListeners();
});

// Main-process events.
window.api_vivi.evt_connection(async (data) => {
  if (data.connected) {
    print("received connected");
    vivi_manager.received_connected();
    print(data);
    await setting_manager.create_ADC_settings(data.device_info.NUM_CHANNELS);
    waterfall_manager.create_tabs(data.device_info.NUM_CHANNELS);
  } else {
    print("received disconnected");
    vivi_manager.received_disconnected();
    setting_manager.received_disconnected();
    waterfall_manager.received_disconnected();
  }
});

window.api_vivi.evt_status((data) => {
  if (data.kind === "live-data") {
    liveview_manager.received_liveData(data.data);
    waterfall_manager.received_liveData(data.data);
    return;
  }

  if (data.kind !== "acquire") return;

  if (data.status === "started") {
    acquisition_manager.received_started(data.mode);
    vivi_manager.received_started(data.mode);
  } else if (data.status === "finished") {
    acquisition_manager.received_finished();
    vivi_manager.received_finished();
  } else if (data.status === "progress") {
    acquisition_manager.update_progress(data.value);
  } else if (data.status === "delay") {
    acquisition_manager.received_delay();
    vivi_manager.received_delay();
  }
});

window.api_vivi.evt_settings((data) => {
  setting_manager.update_settings(data);
});

window.api_log.evt_status((data) => {
  if (data.status === "started") {
    log_manager.received_started(data.fname);
  } else if (data.status === "finished") {
    log_manager.received_finished(data.fname);
  } else {
    log_manager.received_error();
  }
});

window.addEventListener("resize", () => {
  liveview_manager.resize();
});
