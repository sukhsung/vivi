import { UI_devManager } from "./UI_devManager.js";
import { UI_PathManager } from "./UI_Path.js";
import { UI_ConnectionManager } from "./UI_Connection.js";
import { UI_SettingManager } from "./UI_Settings.js";
import { UI_AcquisitionManager } from "./UI_Acquisition.js";
import { UI_LiveviewManager } from "./UI_LiveView.js";
import { UI_WaterfallManager } from "./UI_Waterfall.js";
import { UI_TerminalManager } from "./UI_Terminal.js";

const verbose = true
const dev_manager = new UI_devManager();
const path_manager = new UI_PathManager();
const connection_manager = new UI_ConnectionManager(verbose);
const setting_manager = new UI_SettingManager(verbose);
const acquisition_manager = new UI_AcquisitionManager();
const liveview_manager = new UI_LiveviewManager();
const waterfall_manager = new UI_WaterfallManager();
const terminal_manager = new UI_TerminalManager();


function print( message, header='renderer.js') {
  if (verbose) {
    console.log( `${header}`, message)
  }
}

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

window.api_connection.receivedConnection((data) => {
  if (data.connected) {
    print('received connected')
    dev_manager.received_connected();
    connection_manager.received_connected();
    setting_manager.create_ADC_settings(data.NUM_CHANNELS);
    waterfall_manager.create_tabs( data.NUM_CHANNELS)
  } else {
    print('received disconnected')
    dev_manager.received_disconnected();
    connection_manager.received_disconnected();
  }
})

window.api_acquire.receivedStatus((data) =>{
  print( 'received' + data)
  if (data.status==="started") {
    acquisition_manager.received_started()
  } else if (data.status ==="finished"){
    acquisition_manager.received_finished()
  } else if (data.status ==="progress"){
    acquisition_manager.update_progress( data.value)
  }

})

window.api_acquire.receivedLiveData((data) => {
  liveview_manager.received_liveData(data);
  waterfall_manager.received_liveData(data);
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