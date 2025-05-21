import { UI_devManager } from "./UI_devManager.js";
import { UI_PathManager } from "./UI_Path.js";
import { UI_ConnectionManager } from "./UI_Connection.js";
import { UI_SettingManager } from "./UI_Settings.js";
import { UI_AcquisitionManager } from "./UI_Acquisition.js";
import { UI_LiveviewManager } from "./UI_LiveView.js";
import { UI_WaterfallManager } from "./UI_Waterfall.js";
import { UI_TerminalManager } from "./UI_Terminal.js";

const dev_manager = new UI_devManager();
const path_manager = new UI_PathManager();
const connection_manager = new UI_ConnectionManager();
const setting_manager = new UI_SettingManager();
const acquisition_manager = new UI_AcquisitionManager();
const liveview_manager = new UI_LiveviewManager();
const waterfall_manager = new UI_WaterfallManager();
const terminal_manager = new UI_TerminalManager();

window.addEventListener("load", () => {
  dev_manager.initialize();
  path_manager.initialize();
  connection_manager.initialize();
  setting_manager.initialize();
  acquisition_manager.initialize();
  liveview_manager.initialize()
  waterfall_manager.initialize();
  terminal_manager.initialize();

  acquisition_manager.addEventListener("start-view", () => {
    const NUM_FFT = acquisition_manager.NUM_FFT;
    const t = 0;
    const labels = setting_manager.labels;
    const NUM_CHANNELS = setting_manager.NUM_CHANNELS;
    const sampling = setting_manager.sampling;

    liveview_manager.init_plot(NUM_CHANNELS, NUM_FFT, sampling, labels);
    waterfall_manager.init_plot( NUM_CHANNELS, NUM_FFT);
    acquisition_manager.start_acquisition(NUM_FFT, t, labels);
  });
  acquisition_manager.addEventListener("start-acquire", () => {
    const NUM_FFT = acquisition_manager.NUM_FFT;
    const t = acquisition_manager.t_acquire;
    const labels = setting_manager.labels;
    const NUM_CHANNELS = setting_manager.NUM_CHANNELS;
    const sampling = setting_manager.sampling;

    liveview_manager.init_plot(NUM_CHANNELS, NUM_FFT, sampling, labels);
    waterfall_manager.init_plot( NUM_CHANNELS, NUM_FFT);
    acquisition_manager.start_acquisition(NUM_FFT, t, labels);
  });
});

window.api.receivedLiveData((data) => {
  liveview_manager.received_liveData(data);
  waterfall_manager.received_liveData(data);
});

window.api.receivedStatus((data) => {
  if (data.status === "connected") {
    dev_manager.received_connected();
    setting_manager.create_ADC_settings(data.NUM_CHANNELS);
    waterfall_manager.create_tabs( data.NUM_CHANNELS)
  } else if (data.status === "disconnected") {
    dev_manager.received_disconnected();
  } else if (data.status === "started") {
    dev_manager.received_started();
    acquisition_manager.received_started(data.file_name);
  } else if (data.status === "progress") {
    acquisition_manager.update_progress(data.value);
  } else if (data.status === "finished") {
    dev_manager.received_finished();
    acquisition_manager.received_finished();
  }
});

window.api.receivedSetting((data) => {
  setting_manager.update_settings(data);
});

window.log_api.receivedStatus((data) => {
  if (data.status === "started") {
    path_manager.received_started(data.fname);
  } else if (data.status === "finished") {
    path_manager.received_finished(data.fname);
  } else {
    path_manager.received_error();
  }
});

window.addEventListener("resize", () => {
  liveview_manager.resize();
});