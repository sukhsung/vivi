const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  listSerialPorts: () => ipcRenderer.invoke("list-serial-ports"),
  isConnected: () => ipcRenderer.invoke("is-connected"),
  connectDevice: (protocol) => ipcRenderer.send("connect-device", protocol),
  disconnectDevice: () => ipcRenderer.send("disconnect-device"),
  setSampling: (sampling) => ipcRenderer.send("set-sampling", sampling),
  setADC: (data) => ipcRenderer.send("set-ADC", data),
  openTerminal: () => ipcRenderer.invoke("terminal-open"),
  terminalCommand: (msg) => ipcRenderer.invoke("terminal-command", msg),
  startAcquire: (data) => ipcRenderer.invoke("start-acquisition", data),
  stopAcquire: () => ipcRenderer.invoke("stop-acquisition"),
  receivedLiveData: (callback) =>
    ipcRenderer.on("live-data", (event, data) => callback(data)),
  receivedStatus: (callback) =>
    ipcRenderer.on("dev:status", (event, data) => callback(data)),
  receivedSetting: (callback) =>
    ipcRenderer.on("settings", (event, data) => callback(data)),
});


contextBridge.exposeInMainWorld("log_api", {
  selectPath: () => ipcRenderer.invoke("log_api", "selectPath"),
  openPath: () => ipcRenderer.invoke("log_api", "openPath"),
  getCurrentPath: () => ipcRenderer.invoke("log_api", "getCurrentPath"),

  receivedStatus: (callback) =>
    ipcRenderer.on("log:status", (event, data) => callback(data)),
});
