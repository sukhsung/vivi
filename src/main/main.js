const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require("path");
const { ADC8Manager, list_serial_ports } = require("./ADC8Manager.js");
const { LogManager } = require("./logManager.js");
const { FFTManager } = require("./fftManager.js");

if (process.platform === "linux") {
  app.commandLine.appendSwitch("gtk-version", "3");
}
if (require("electron-squirrel-startup")) app.quit();

const path_main = __dirname;
const path_preload = path.join(path_main, "..", "preload");
const path_renderer = path.join(path_main, "..", "renderer");
const path_terminal = path.join(path_main, "..", "terminal");

const verbose = true;

let win;
const fft_manager = new FFTManager();
const dev_manager = new ADC8Manager(verbose);
const log_manager = new LogManager(verbose);

function print(message, header = "main.js") {
  if (verbose) {
    console.log("\x1b[32m%s:\x1b[0m \x1b[33m%s\x1b[0m", header, message);
  }
}

function send_to_renderer(channel, data) {
  if (win && !win.isDestroyed()) {
    // console.log("Window is still alive");
    win.webContents.send(channel, data);
  } else {
    print("Window is already destroyed");
  }
}

function registerLogHandlers() {
  ipcMain.handle("log_api", async (evt, data) => {
    if (data == "selectPath") {
      return await log_manager.select_dir();
    } else if (data == "openPath") {
      await log_manager.open_path();
    } else if (data == "getCurrentPath") {
      return log_manager.path;
    }
  });

  log_manager.on("log:status", (data) => {
    send_to_renderer("log:status", data);
  });
}

function registerConnectionHandlers() {
  // Update serial ports
  ipcMain.handle("list-serial-ports", async () => {
    return await list_serial_ports();
  });

  ipcMain.handle("device:isConnected", async () => {
    return dev_manager.connected;
  });

  ipcMain.on("device:connect", async (evt, protocol) => {
    await dev_manager.connect(protocol);
  });

  ipcMain.on("device:disconnect", async () => {
    await dev_manager.disconnect();
  });

  dev_manager.on("connection", async (status) => {
    const data = {};
    if (status.connected) {
      print("Sending connected to renderer");
      data.connected = true;
      data.NUM_CHANNELS = dev_manager.NUM_CHANNELS;
    } else {
      print("Sending disconnected to renderer");
      data.connected = false;
    }

    send_to_renderer("device:connection", data);
  });
}

function registerSettingHandlers() {
  ipcMain.on("setting:setSampling", async (evt, sampling) => {
    dev_manager.setSampling(sampling);
  });

  ipcMain.on("setting:setADC", async (evt, data) => {
    dev_manager.setADC(data);
  });

  ipcMain.on("setting:setAllGain", async (evt, data) => {
    dev_manager.setAllGain(data);
  });

  dev_manager.on("setting:update", () => {
    send_to_renderer("setting:update", dev_manager.settings);
  });
}

function registerAcquisitionHandlers() {
  ipcMain.on("acquire:start", (evt, data) => {
    print("Requested to start");
    dev_manager.update_labels(data.labels);
    log_manager.start_log(data.t, dev_manager.settings);
    fft_manager.initialize(data.NUM_FFT);

    dev_manager.NUM_FFT = data.NUM_FFT;
    dev_manager.start_acquisition(data.t_acquire, data.t_delay);
  });

  ipcMain.on("acquire:stop", () => {
    dev_manager.stop_acquisition();
    log_manager.stop_log();
  });

  dev_manager.on("acquire:status", (data) => {
    send_to_renderer("acquire:status", data);
  });

  dev_manager.on("acquire:live-data", (data) => {
    log_manager.write_data(data);
    const ffts = fft_manager.calc_fft(data);
    send_to_renderer("acquire:live-data", ffts);
  });
}

function registerTerminalHandlers() {
  ipcMain.handle("terminal-open", () => {
    openTerminal();
  });
  ipcMain.handle("terminal-command", async (evt, msg) => {
    const return_msg = await dev_manager.run_command(msg.value);
    send_to_renderer("setting-updated", dev_manager.settings);
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
      preload: path.join(path_preload, "preload.js"),
      devTools: !app.isPackaged,
      autoHideMenuBar: app.isPackaged,
    },
  });

  termWin.setMenu(null)

  termWin.loadFile(path.join(path_terminal, "terminal.html"));
}

function createWindow() {
  win = new BrowserWindow({
    width: 1400,
    height: 900,
    autoHideMenuBar: true,  
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(path_preload, "preload.js"),
      autoHideMenuBar: app.isPackaged,
      devTools: !app.isPackaged,
    },
  });
  win.setMenu(null)

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
      print("Closing");
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
  registerSettingHandlers();
  registerConnectionHandlers();
  registerAcquisitionHandlers();
  registerTerminalHandlers();
  registerLogHandlers();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
