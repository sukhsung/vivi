import { UI_SplashManager } from "../../../../node_modules/instrument-ui/src/renderer/js/splash/UI_SplashManager.js";
import { UI_ConnectionManager } from "../../../../node_modules/instrument-ui/src/renderer/js/splash/UI_Connection.js";
import { instrumentTemplateUrl } from "../../../../node_modules/instrument-ui/src/renderer/js/util/package_urls.js";
import { make_printer } from "../../../../node_modules/instrument-ui/src/common/printer.js";

const t_interval = 100;
const verbose = true;
const vivi_connection_manager = new UI_ConnectionManager(
  "ADC Controller",
  "vivi",
  "utf-8",
  "\n", // delimiter
  t_interval, // t_interval,
  1, // flex order
  verbose,
  window.api_vivi,
);

const print = make_printer(verbose, "UI_DeviceManager", false);

export class UI_DeviceManager extends UI_SplashManager {
  constructor() {
    super(
      instrumentTemplateUrl("template_devicemanager.html"),
      "device_manager",
      "PB_device_manager",
      "PB_device_manager_close",
      true,
      true,
    );
  }

  async _initialize(config) {
    document.getElementById("panel_logo")?.classList.add("bg-app-500");

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
        this.hide();
      } else {
        print("Temperature: received disconnected");
        vivi_connection_manager.received_disconnected();
      }
    });
  }
}
