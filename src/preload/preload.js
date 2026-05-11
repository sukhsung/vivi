const { contextBridge, ipcRenderer } = require("electron");

(async () => {
  const { default: APP_IPC_CHANNELS } = await import(process.env.APP_IPC_CHANNELS);
  const { createPreload } = await import(process.env.INSTRUMENT_UI_PRELOAD_COMMON);

  createPreload({
    contextBridge,
    ipcRenderer,
    appIpcChannels: APP_IPC_CHANNELS,
    setup: ({ contextBridge, ipcRenderer, CH, createDevicePreloadApi }) => {
      contextBridge.exposeInMainWorld("api_terminal", {
        openTerminal: () => ipcRenderer.invoke(CH.TERMINAL.OPEN),
        terminalCommand: (msg) => ipcRenderer.invoke(CH.TERMINAL.COMMAND, msg),
      });
      contextBridge.exposeInMainWorld("api_vivi", createDevicePreloadApi(ipcRenderer, CH.VIVI));
    },
  });
})();
