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

  contextBridge.exposeInMainWorld(
    "api_vivi",
    createDevicePreloadApi(ipcRenderer, CH.VIVI),
  );
})();
