import { app, BrowserWindow, ipcMain } from "electron";

import { FFTManager } from "./fftManager.js";
import { ADC8Manager, EVT_RAW_DATA, EVT_ACQUIRE_START } from "./ADC8Manager.js";
import { LogManager } from "./logManager.js";
import {
  load_config,
  list_serial_ports,
  guardEPIPE,
  registerOSSwitches,
  registerApplicationMenu,
  resolvePaths,
  registerAppHandlers,
  registerAppLifecycleHandlers,
  registerWindowHandlers,
  send_to_renderer,
  make_printer,
  createAbout,
  createMainWindow,
  registerMainWindowEvents,
} from "instrument-ui";
import CH from "../common/ipcChannels.js";

const APP_VERSION = app.getVersion();
const verbose = app.isPackaged ? 0 : 2;
const APP_INFO_URL = "hbarinstruments.com";
const APP_INFO_COPYRIGHT = "© 2026 h-Bar Instruments";

// Process-level setup must run before windows or IPC handlers are registered.
guardEPIPE();
registerOSSwitches();
registerApplicationMenu();

// App-local paths follow the standard src/main, src/preload, src/renderer layout.
const {
  path_preload,
  path_renderer_index,
  path_terminal_index,
  path_icon,
  path_default_config,
  url_app_ipc_channels,
} = resolvePaths(import.meta.url);

const appConfig = load_config(path_default_config);
const DEV_MODE = process.argv.includes("dev");

process.env.APP_IPC_CHANNELS = url_app_ipc_channels;
process.env.INSTRUMENT_UI_PRELOAD_COMMON = import.meta.resolve(
  "instrument-ui/preload/common.js",
);

let win;

// Device and service managers own hardware, acquisition, and app-side state.
const fft_manager = new FFTManager(verbose);
const dev_manager = new ADC8Manager(verbose);
const log_manager = new LogManager(verbose);

const print = make_printer(verbose, "main");

// App-specific IPC and device events.
function registerLogHandlers() {
  log_manager.set_win(win);

  ipcMain.handle(CH.LOG.PATH_SELECT, async () => {
    return await log_manager.select_dir();
  });
  ipcMain.handle(CH.LOG.PATH_OPEN, async () => {
    return await log_manager.open_path();
  });
  ipcMain.handle(CH.LOG.PATH_GET_CURRENT, async () => {
    return log_manager.path;
  });
  ipcMain.on(CH.LOG.START, async () => {
    log_manager.start_log(0, dev_manager.settings);
  });
  ipcMain.on(CH.LOG.STOP, async () => {
    log_manager.stop_log();
  });
  ipcMain.on(CH.LOG.SET_TAG, async (_evt, data) => {
    log_manager.set_tag(data.tag);
  });

  log_manager.on(CH.LOG.EVT_STATUS, (data) => {
    send_to_renderer(win, CH.LOG.EVT_STATUS, data);
  });
}

function registerConnectionHandlers() {
  // Update serial ports
  ipcMain.handle(CH.DEVICE_MANAGER.LIST_SERIAL_PORTS, async () => {
    return await list_serial_ports();
  });

  ipcMain.handle(CH.VIVI.IS_CONNECTED, async () => {
    return dev_manager.is_connected();
  });

  ipcMain.on(CH.VIVI.CONNECT, async (_evt, data) => {
    await dev_manager.connect(data.protocol);
  });

  ipcMain.on(CH.VIVI.DISCONNECT, async () => {
    await dev_manager.disconnect();
  });

  ipcMain.on(CH.VIVI.START_COMM, async () => {
    await dev_manager.start_comm();
  });

  ipcMain.on(CH.VIVI.ADD_REQUEST, async (_evt, request) => {
    await dev_manager._process_request(request);
  });

  dev_manager.on(CH.VIVI.EVT_CONNECTION, async (data) => {
    if (data.connected) {
      print("Sending connected to renderer");
    } else {
      print("Sending disconnected to renderer");
    }
    send_to_renderer(win, CH.VIVI.EVT_CONNECTION, data);
  });
}

function registerDeviceEventHandlers() {
  dev_manager.on(EVT_ACQUIRE_START, (data) => {
    log_manager.start_log(data.t, dev_manager.settings);
    fft_manager.initialize(
      data.NUM_FFT,
      dev_manager.device_info.NUM_CHANNELS,
      data.NUM_AVE,
    );
  });

  dev_manager.on(CH.VIVI.EVT_SETTINGS, (data) => {
    send_to_renderer(win, CH.VIVI.EVT_SETTINGS, data);
  });

  dev_manager.on(CH.VIVI.EVT_STATUS, async (data) => {
    send_to_renderer(win, CH.VIVI.EVT_STATUS, data);
    if (data["status"] === "finished") {
      await fft_manager.calc_ave();
      await log_manager.write_data_fft(fft_manager.fft_ave);
      log_manager.stop_log();
    }
  });

  dev_manager.on(EVT_RAW_DATA, (data) => {
    log_manager.write_data_raw(data);
    fft_manager.calc_fft(data);
  });

  fft_manager.on("fft:live-data", (data) => {
    send_to_renderer(win, CH.VIVI.EVT_STATUS, {
      kind: "live-data",
      data: data.ffts,
    });
  });
}

function registerTerminalHandlers() {
  ipcMain.handle(CH.TERMINAL.OPEN, () => {
    openTerminal();
  });
  ipcMain.handle(CH.TERMINAL.COMMAND, async (evt, msg) => {
    const return_msg = await dev_manager.run_command(msg.value);
    return return_msg;
  });
}

function openTerminal() {
  const termWin = new BrowserWindow({
    width: 800,
    height: 600,
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path_preload,
      devTools: !app.isPackaged,
      autoHideMenuBar: app.isPackaged,
    },
  });

  termWin.setMenu(null);
  termWin.loadFile(path_terminal_index);
}

// App startup wires the shared Electron shell to app-specific managers.
app.whenReady().then(() => {
  win = createMainWindow({
    preload: path_preload,
    renderer: path_renderer_index,
    icon: path_icon,
    devMode: DEV_MODE,
    fillWorkArea: true,
  });
  registerMainWindowEvents({
    win,
    icon: path_icon,
    onClosed: async () => {
      await dev_manager.close();
      await log_manager.close();
    },
  });
  createAbout({
    applicationName: "vivi",
    copyright: APP_INFO_COPYRIGHT,
  });
  registerAppHandlers({
    version: APP_VERSION,
    config: appConfig,
    info: { url: APP_INFO_URL, copyright: APP_INFO_COPYRIGHT },
  });
  registerConnectionHandlers();
  registerLogHandlers();
  registerDeviceEventHandlers();
  registerTerminalHandlers();
  registerWindowHandlers();
  registerAppLifecycleHandlers();
});
