import { import_template } from "../util/import_template.js";
import { UI_SplashManager } from "./UI_SplashManager.js";
import { UI_ConnectionManager } from "./UI_Connection.js";

const t_interval = 100;
const verbose = true;
const vivi_connection_manager = new UI_ConnectionManager(
  "ADC Controller",
  "vivi",
  "latin1", // encoding: Critical for CTC100 Ohm symbol (cp-1252)
  "\r\n", // delimiter
  t_interval, // t_interval,
  1, // flex order
  verbose,
);

function print(message, header = "device_manager.js") {
  if (verbose) {
    console.log(`${header}`, message);
  }
}

export class UI_DeviceManager extends UI_SplashManager {
  constructor() {
    super(
      "./templates/template_devicemanager.html",
      "device_manager",
      "PB_device_manager",
      "PB_device_manager_close",
      true,
      true,
    );
  }

  async _initialize(config) {
    const col_count = 2;
    const container = document.getElementById("connection-container");
    container.classList.remove("grid-cols-2", "grid-cols-3", "grid-cols-4");
    container.classList.add(`grid-cols-${col_count}`);

    const conn = config?.connections ?? {};
    this._init_vivi(conn.vivi);
  }

  _init_vivi(conn_config) {
    vivi_connection_manager.initialize(conn_config);
    window.api_vivi.evt_connection((data) => {
      if (data.connected) {
        print("Temperature: received connected");
        vivi_connection_manager.received_connected(data.protocol);
      } else {
        print("Temperature: received disconnected");
        vivi_connection_manager.received_disconnected();
      }
    });
  }
}
