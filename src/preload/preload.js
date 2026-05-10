const { contextBridge, ipcRenderer } = require("electron");

(async () => {
  // Loading ESM modules in CommonJS
  const { default: APP_IPC_CHANNELS } = await import(
    process.env.APP_IPC_CHANNELS
  );
  const { createIpcChannels } = await import(
    process.env.INSTRUMENT_UI_IPC_CHANNELS
  );
  const { createDevicePreloadApi, registerCommonPreloadApis } = await import(
    process.env.INSTRUMENT_UI_PRELOAD_COMMON
  );
  const CH = createIpcChannels(APP_IPC_CHANNELS);

  registerCommonPreloadApis({ contextBridge, ipcRenderer, CH });

  contextBridge.exposeInMainWorld("api_terminal", {
    openTerminal: () => ipcRenderer.invoke(CH.TERMINAL.OPEN),
    terminalCommand: (msg) => ipcRenderer.invoke(CH.TERMINAL.COMMAND, msg),
  });

  contextBridge.exposeInMainWorld("api_acquire", {
    startAcquire: (data) => ipcRenderer.send(CH.ACQUIRE.START, data),
    stopAcquire: () => ipcRenderer.send(CH.ACQUIRE.STOP),
    receivedStatus: (callback) =>
      ipcRenderer.on(CH.ACQUIRE.EVT_STATUS, (_evt, data) => callback(data)),
    receivedLiveData: (callback) =>
      ipcRenderer.on(CH.ACQUIRE.EVT_LIVE_DATA, (_evt, data) => callback(data)),
  });

  contextBridge.exposeInMainWorld("api_setting", {
    setSampling: (sampling) =>
      ipcRenderer.send(CH.SETTING.SET_SAMPLING, sampling),
    setADC: (data) => ipcRenderer.send(CH.SETTING.SET_ADC, data),
    setAllGain: (data) => ipcRenderer.send(CH.SETTING.SET_ALL_GAIN, data),
    receivedSetting: (callback) =>
      ipcRenderer.on(CH.SETTING.EVT_UPDATE, (_evt, data) => callback(data)),
  });

  contextBridge.exposeInMainWorld(
    "api_vivi",
    createDevicePreloadApi(ipcRenderer, CH.VIVI),
  );
})();
