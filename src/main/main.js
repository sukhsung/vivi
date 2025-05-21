const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require("path");
const { ADC8Manager, list_serial_ports } = require("./ADC8Manager.js");
const { LogManager } = require("./logManager.js");
const { FFTManager } = require("./fftManager.js");

const path_main = __dirname;
const path_preload = path.join(__dirname, "..", "preload");
const path_renderer = path.join(__dirname, "..", "renderer");
const path_terminal = path.join(__dirname, "..", "terminal");

let win;
global.verbose = true;

const fft_manager = new FFTManager();
const dev_manager = new ADC8Manager("vivi", "utf8", "\n");
const log_manager = new LogManager();

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

  log_manager.on("status", (data) => {
    win.webContents.send("log:status", data);
  });
}

function registerDeviceHandlers() {
  // Update serial ports
  ipcMain.handle("list-serial-ports", async () => {
    return await list_serial_ports();
  });

  ipcMain.handle("is-connected", async () => {
    return dev_manager.connected;
  });

  ipcMain.on("connect-device", async (evt, protocol) => {
    await dev_manager.connect(protocol);
  });

  ipcMain.on("disconnect-device", async () => {
    await dev_manager.disconnect();
  });

  ipcMain.on("set-sampling", async (evt, sampling) => {
    dev_manager.set_sampling(sampling);
  });

  ipcMain.on("set-ADC", async (evt, data) => {
    dev_manager.set_ADC(data);
  });

  dev_manager.on("status", (data) => {
    win.webContents.send("dev:status", data);
  });

  dev_manager.on("settings", () => {
    win.webContents.send("settings", dev_manager.settings);
  });
}

function registerAcquisitionHandlers() {
  ipcMain.handle("start-acquisition", (evt, data) => {
    dev_manager.update_labels(data.labels);
    fft_manager.initialize(data.NUM_FFT);
    log_manager.start_log(data.t, dev_manager.settings);

    dev_manager.NUM_FFT = data.NUM_FFT;
    dev_manager.start_acquisition(data.t);
    return { started: true };
  });

  ipcMain.handle("stop-acquisition", () => {
    dev_manager.stop_acquisition();
    log_manager.stop_log();
    return { finished: true };
  });

  dev_manager.on("live-data", (data) => {
    log_manager.write_data(data);
    const ffts = fft_manager.calc_fft(data);
    win.webContents.send("live-data", ffts);
  });
}

function registerTerminalHandlers() {
  ipcMain.handle("terminal-open", () => {
    openTerminal();
  });
  ipcMain.handle("terminal-command", async (evt, msg) => {
    const return_msg = await dev_manager.run_command(msg.value);
    win.webContents.send("setting-updated", dev_manager.settings);
    return return_msg;
  });
}

function openTerminal() {
  const termWin = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(path_preload, "preload.js"),
      // devTools: !app.isPackaged,
    },
  });
  termWin.loadFile(path.join(path_terminal, "terminal.html"));
}

function createWindow() {
  win = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(path_preload, "preload.js"),
      // devTools: !app.isPackaged,
    },
  });

  win.loadFile(path.join(path_renderer, "index.html"));
  log_manager.set_win(win);

  win.on('close', function (e) {
    let response = dialog.showMessageBoxSync(this, {
        type: 'question',
        buttons: ['Yes', 'No'],
        title: 'Confirm',
        message: 'Are you sure you want to quit?'
    });

    if(response == 1) e.preventDefault();
});

  win.on("closed", () => {
    // Closing main window closes everything
    app.quit();
  });
}

app.whenReady().then(() => {
  createWindow();
  registerDeviceHandlers();
  registerAcquisitionHandlers();
  registerTerminalHandlers();
  registerLogHandlers();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
