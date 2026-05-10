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

  ACQUIRE: Object.freeze({
    START: "acquire:start",
    STOP: "acquire:stop",
    EVT_STATUS: "acquire:status",
    EVT_LIVE_DATA: "acquire:live-data",
  }),

  SETTING: Object.freeze({
    SET_SAMPLING: "setting:setSampling",
    SET_ADC: "setting:setADC",
    SET_ALL_GAIN: "setting:setAllGain",
    EVT_UPDATE: "setting:update",
  }),

  TERMINAL: Object.freeze({
    OPEN: "terminal:open",
    COMMAND: "terminal:command",
  }),
});

export default APP_IPC_CHANNELS;
