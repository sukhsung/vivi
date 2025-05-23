const { contextBridge, ipcRenderer } = require("electron");

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

contextBridge.exposeInMainWorld("api_connection", {
  receivedConnection: (callback) =>
    ipcRenderer.on("device:connection", (event, data) => callback(data)),
  isConnected: () => ipcRenderer.invoke("device:isConnected"),
  connectDevice: (protocol) => ipcRenderer.send("device:connect", protocol),
  disconnectDevice: () => ipcRenderer.send("device:disconnect"),
  listSerialPorts: () => ipcRenderer.invoke("list-serial-ports"),
});

contextBridge.exposeInMainWorld("api_setting", {
  setSampling: (sampling) => ipcRenderer.send("setting:setSampling", sampling),
  setADC: (data) => ipcRenderer.send("setting:setADC", data),
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
