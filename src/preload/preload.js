const { contextBridge, ipcRenderer } = require("electron");

(async () => {
  // Loading ESM Module in CommonJS
  const { default: CH } = await import(process.env.IPC_CHANNEL);

  contextBridge.exposeInMainWorld("api_device_manager", {
    open: () => ipcRenderer.send(CH.DEVICE_MANAGER.OPEN),
    listSerialPorts: () =>
      ipcRenderer.invoke(CH.DEVICE_MANAGER.LIST_SERIAL_PORTS),
  });

  contextBridge.exposeInMainWorld("api", {
    openTerminal: () => ipcRenderer.invoke("terminal-open"),
    terminalCommand: (msg) => ipcRenderer.invoke("terminal-command", msg),
  });

  contextBridge.exposeInMainWorld("api_acquire", {
    startAcquire: (data) => ipcRenderer.send("acquire:start", data),
    stopAcquire: () => ipcRenderer.send("acquire:stop"),
    receivedStatus: (callback) =>
      ipcRenderer.on("acquire:status", (event, data) => callback(data)),
    receivedLiveData: (callback) =>
      ipcRenderer.on("acquire:live-data", (event, data) => callback(data)),
  });

  contextBridge.exposeInMainWorld("api_setting", {
    setSampling: (sampling) =>
      ipcRenderer.send("setting:setSampling", sampling),
    setADC: (data) => ipcRenderer.send("setting:setADC", data),
    setAllGain: (data) => ipcRenderer.send("setting:setAllGain", data),
    receivedSetting: (callback) =>
      ipcRenderer.on("setting:update", (event, data) => callback(data)),
  });

  contextBridge.exposeInMainWorld("log_api", {
    selectPath: () => ipcRenderer.invoke("log_api", "selectPath"),
    openPath: () => ipcRenderer.invoke("log_api", "openPath"),
    getCurrentPath: () => ipcRenderer.invoke("log_api", "getCurrentPath"),

    receivedStatus: (callback) =>
      ipcRenderer.on("log:status", (event, data) => callback(data)),
  });

  contextBridge.exposeInMainWorld("api_vivi", {
    is_connected: () => ipcRenderer.invoke(CH.VIVI.IS_CONNECTED),
    connect: (data) => ipcRenderer.send(CH.VIVI.CONNECT, data),
    disconnect: () => ipcRenderer.send(CH.VIVI.DISCONNECT),
    add_request: (data) => ipcRenderer.send(CH.VIVI.ADD_REQUEST, data),

    start_comm: () => ipcRenderer.send(CH.VIVI.START_COMM),

    evt_connection: (callback) =>
      ipcRenderer.on(CH.VIVI.EVT_CONNECTION, (_evt, data) => callback(data)),
    evt_status: (callback) =>
      ipcRenderer.on(CH.VIVI.EVT_STATUS, (_evt, data) => callback(data)),
    evt_settings: (callback) =>
      ipcRenderer.on(CH.VIVI.EVT_SETTINGS, (_evt, data) => callback(data)),
  });

  contextBridge.exposeInMainWorld("api_flags", {
    get_flags: () => ipcRenderer.invoke(CH.APP.GET_FLAGS),
  });

  contextBridge.exposeInMainWorld("api_app", {
    get_version: () => ipcRenderer.invoke(CH.APP.GET_VERSION),
    get_config: () => ipcRenderer.invoke(CH.APP.GET_CONFIG),
  });

  contextBridge.exposeInMainWorld("api_window", {
    minimize: () => ipcRenderer.send(CH.WINDOW.MINIMIZE),
    maximize: () => ipcRenderer.send(CH.WINDOW.MAXIMIZE),
    close: () => ipcRenderer.send(CH.WINDOW.CLOSE),
  });
})();
