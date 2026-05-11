import { app, BrowserWindow, ipcMain, dialog, Menu, screen } from "electron";
import { createRequire } from "module";
const _require = createRequire(import.meta.url);
const { version: APP_VERSION } = _require("../../package.json");

import path from "node:path";
import fs from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";

import { list_serial_ports } from "instrument-ui/main/util/list_serial_ports.js";
import { FFTManager } from "./fftManager.js";
import { ADC8Manager, EVT_RAW_DATA } from "./ADC8Manager.js";
import { LogManager } from "./logManager.js";
import CH from "../common/ipcChannels.js";
import { config as appConfig } from "./configManager.js";

const verbose = app.isPackaged ? 0 : 3;
const APP_INFO_URL = "hbarinstruments.com";
const APP_INFO_COPYRIGHT = "© 2026 h-Bar Instruments";

if (process.platform === "linux") {
  // app.commandLine.appendSwitch("gtk-version", "3");
  app.commandLine.appendSwitch("--no-zygote");
}

app.commandLine.appendSwitch("--password-store", "basic");

const DEV_MODE = process.argv.includes("dev");

// Pre-resolve filenames
function resolve_path(path) {
  return pathToFileURL(path).href;
}
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const path_main = __dirname;

const path_preload = path.join(path_main, "..", "preload", "preload.js");
const path_renderer = path.join(path_main, "..", "renderer");
const path_ipcchannel = path.join(path_main, "..", "common", "ipcChannels.js");
const path_app_ipcchannels = path.join(
  path_main,
  "..",
  "common",
  "appIpcChannels.js",
);
const path_terminal = path.join(path_main, "..", "terminal");
const path_icon = path.join(path_main, "..", "assets", "app-icon.png");
process.env.IPC_CHANNEL = resolve_path(path_ipcchannel);
process.env.APP_IPC_CHANNELS = resolve_path(path_app_ipcchannels);
process.env.INSTRUMENT_UI_IPC_CHANNELS = resolve_path(
  _require.resolve("instrument-ui/common/ipcChannels.js"),
);
process.env.INSTRUMENT_UI_PRELOAD_COMMON = resolve_path(
  _require.resolve("instrument-ui/preload/common.js"),
);

let win;
const fft_manager = new FFTManager();
const dev_manager = new ADC8Manager(verbose);
const log_manager = new LogManager(verbose);

function log(message, header = "main.js") {
  if (verbose) {
    console.log("\x1b[32m%s:\x1b[0m \x1b[33m%s\x1b[0m", header, message);
  }
}

function send_to_renderer(channel, data) {
  if (win && !win.isDestroyed()) {
    // console.log("Window is still alive");
    win.webContents.send(channel, data);
  } else {
    log("Window is already destroyed");
  }
}

function registerAppHandlers() {
  ipcMain.handle(CH.APP.GET_VERSION, () => APP_VERSION);
  ipcMain.handle(CH.APP.GET_CONFIG, () => appConfig);
  ipcMain.handle(CH.APP.GET_INFO, () => ({
    url: APP_INFO_URL,
    copyright: APP_INFO_COPYRIGHT,
  }));
}

function registerWindowHandlers() {
  ipcMain.on(CH.WINDOW.MINIMIZE, (event) => {
    BrowserWindow.fromWebContents(event.sender)?.minimize();
  });
  ipcMain.on(CH.WINDOW.MAXIMIZE, (event) => {
    const w = BrowserWindow.fromWebContents(event.sender);
    if (w?.isMaximized()) w.unmaximize();
    else w?.maximize();
  });
  ipcMain.on(CH.WINDOW.CLOSE, (event) => {
    BrowserWindow.fromWebContents(event.sender)?.close();
  });
}
function registerLogHandlers() {
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
    send_to_renderer(CH.LOG.EVT_STATUS, data);
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
    console.log("Received connect request with data:", data);
    await dev_manager.connect(data.protocol);
  });

  ipcMain.on(CH.VIVI.DISCONNECT, async () => {
    await dev_manager.disconnect();
  });

  ipcMain.on(CH.VIVI.START_COMM, async () => {
    await dev_manager.start_comm();
  });

  ipcMain.on(CH.VIVI.ADD_REQUEST, async (_evt, request) => {
    await handleDeviceRequest(request);
  });

  dev_manager.on(CH.VIVI.EVT_CONNECTION, async (data) => {
    if (data.connected) {
      log("Sending connected to renderer");
    } else {
      log("Sending disconnected to renderer");
    }
    send_to_renderer(CH.VIVI.EVT_CONNECTION, data);
  });
}

async function handleDeviceRequest(request) {
  if (!request?.type) return;

  if (request.type === "set_sampling") {
    await dev_manager.setSampling(request.value);
  } else if (request.type === "set_adc") {
    await dev_manager.setADC(request.data);
  } else if (request.type === "set_all_gain") {
    await dev_manager.setAllGain(request.data);
  } else if (request.type === "start_acquisition") {
    startAcquisition(request);
  } else if (request.type === "stop_acquisition") {
    await dev_manager.stop_acquisition();
  } else {
    log(`Unknown device request type: ${request.type}`);
  }
}

function startAcquisition(data) {
  log("Requested to start");
  dev_manager.update_labels(data.labels);
  dev_manager.settings.NUM_FFT = data.NUM_FFT;
  log_manager.start_log(data.t, dev_manager.settings);
  fft_manager.initialize(
    data.NUM_FFT,
    dev_manager.device_info.NUM_CHANNELS,
    data.NUM_AVE,
  );

  dev_manager.start_acquisition(data.t_acquire, data.t_delay);
}

function registerDeviceEventHandlers() {
  dev_manager.on(CH.VIVI.EVT_SETTINGS, (data) => {
    send_to_renderer(CH.VIVI.EVT_SETTINGS, data);
  });

  dev_manager.on(CH.VIVI.EVT_STATUS, async (data) => {
    send_to_renderer(CH.VIVI.EVT_STATUS, data);
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
    send_to_renderer(CH.VIVI.EVT_STATUS, {
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

  termWin.loadFile(path.join(path_terminal, "terminal.html"));
}

function createWindow() {
  const { width, height } = screen.getDisplayNearestPoint(
    screen.getCursorScreenPoint(),
  ).workAreaSize;

  win = new BrowserWindow({
    width,
    height,
    // icon: path_icon,
    frame: false,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path_preload,
      devTools: DEV_MODE || !app.isPackaged,
      sandbox: true, // extra isolation
      webSecurity: true, // enforce same-origin/CORS
      disableBlinkFeatures: "Auxclick", // minor footgun
    },
  });
  if (!DEV_MODE) win.setMenu(null);
  win.maximize();

  win.loadFile(path.join(path_renderer, "index.html"));
  log_manager.set_win(win);

  win.on("close", (e) => {
    let response = dialog.showMessageBoxSync(win, {
      type: "question",
      buttons: ["No", "Yes"],
      title: "Confirm",
      message: "Are you sure you want to quit?",
    });

    if (response == 0) {
      e.preventDefault();
    } else {
      log("Closing");
    }
  });

  win.on("closed", async () => {
    await dev_manager.close();
    await log_manager.close();
    // Closing main window closes everything
    app.quit();
  });
}

app.whenReady().then(() => {
  createWindow();
  registerAppHandlers();
  registerConnectionHandlers();
  registerDeviceEventHandlers();
  registerTerminalHandlers();
  registerLogHandlers();
  registerWindowHandlers();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
