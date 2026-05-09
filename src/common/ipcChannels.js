// 1) Channel registry (single source of truth)
const CH = Object.freeze({
  DEVICE_MANAGER: {
    LIST_SERIAL_PORTS: "device_manager:list_serial_ports",
  },

  VIVI: {
    CONNECT: "vivi:connect",
    DISCONNECT: "vivi:disconnect",
    IS_CONNECTED: "vivi:is_connected",
    EVT_CONNECTION: "vivi:connection",
    START_COMM: "vivi:start_comm",
    EVT_STATUS: "vivi:status",
    EVT_SETTINGS: "vivi:settings",
    ADD_REQUEST: "vivi:add_request",
  },

  LOG: {
    PATH_SELECT: "log:path_select",
    PATH_OPEN: "log:path_open",
    PATH_GET_CURRENT: "log:path_current",
    EVT_STATUS: "log:status",
    START: "log:start",
    STOP: "log:stop",
    SET_TAG: "log:tag",
  },

  APP: {
    GET_FLAGS: "app:get_flags",
    GET_VERSION: "app:get_version",
    GET_CONFIG: "app:get_config",
  },

  WINDOW: {
    MINIMIZE: "window:minimize",
    MAXIMIZE: "window:maximize",
    CLOSE: "window:close",
  },

  TERMINAL: {
    OPEN: "terminal:open",
    COMMAND: "terminal:command",
  },
});

export default CH;
