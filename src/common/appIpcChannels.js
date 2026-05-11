const APP_IPC_CHANNELS = Object.freeze({
  VIVI: Object.freeze({
    CONNECT: "vivi:connect",
    DISCONNECT: "vivi:disconnect",
    IS_CONNECTED: "vivi:is_connected",
    EVT_CONNECTION: "vivi:connection",
    START_COMM: "vivi:start_comm",
    EVT_STATUS: "vivi:status",
    EVT_SETTINGS: "vivi:settings",
    ADD_REQUEST: "vivi:add_request",
  }),

  TERMINAL: Object.freeze({
    OPEN: "terminal:open",
    COMMAND: "terminal:command",
  }),
});

export default APP_IPC_CHANNELS;
