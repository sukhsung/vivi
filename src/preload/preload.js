const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  openTerminal: () => ipcRenderer.invoke("terminal-open"),
  terminalCommand: (msg) => ipcRenderer.invoke("terminal-command", msg),
  startAcquire: (data) => ipcRenderer.invoke("start-acquisition", data),
  stopAcquire: () => ipcRenderer.invoke("stop-acquisition"),
  receivedLiveData: (callback) =>
    ipcRenderer.on("live-data", (event, data) => callback(data)),
  receivedSetting: (callback) =>
    ipcRenderer.on("settings", (event, data) => callback(data)),
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
});

contextBridge.exposeInMainWorld("log_api", {
  selectPath: () => ipcRenderer.invoke("log_api", "selectPath"),
  openPath: () => ipcRenderer.invoke("log_api", "openPath"),
  getCurrentPath: () => ipcRenderer.invoke("log_api", "getCurrentPath"),

  receivedStatus: (callback) =>
    ipcRenderer.on("log:status", (event, data) => callback(data)),
});
