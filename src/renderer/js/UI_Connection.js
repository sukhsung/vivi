import { UI_Manager } from "./UI_Manager.js";
export { UI_ConnectionManager };

const BAUDRATES = [
  4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600,
];

class UI_ConnectionManager extends UI_Manager {
  constructor() {
    super()
    this.protocol = {
      address: null,
      type: null,
      baudRate: null,
      encoding: "utf8",
      delimiter: "\n",
    };
  }

  initialize() {
    // Load DOM
    this.cacheDOM({
      CB_protocol: "protocol",
      TB_address: "address",
      CB_port_list: "port_list",
      CB_baudrate: "baudrate",
      PB_connect: "connect",
      PB_disconnect: "disconnect",
      PB_refresh: "refresh",
      UI_portlist: "UI_portlist",
      UI_address: "UI_address",
    });

    this.CB_protocol.onchange = () => this.onchange_protocol();
    this.TB_address.oninput = () => this.oninput_address();
    this.CB_port_list.onchange = () => this.onchange_port();

    this.CB_add_options(this.CB_baudrate, BAUDRATES);
    this.CB_baudrate.selectedIndex = 1;

    this.PB_connect.onclick = () => this.onclick_connect();
    this.PB_disconnect.onclick = () => this.onclick_disconnect();
    this.PB_disconnect.disabled = true;
    this.PB_refresh.onclick = () => this.onclick_refresh();

    this.update_portList();
  }

  onchange_protocol() {
    this.protocol.type = this.CB_protocol.value;

    const isTCP = this.protocol.type === "TCP";

    this.setHidden(this.UI_portlist, isTCP);
    this.setHidden(this.UI_address, !isTCP);

    if (!isTCP) this.update_portList();
  }

  onchange_port() {
    this.protocol.address = this.CB_port_list.value;
  }

  async update_protocol() {
    this.protocol.type = this.CB_protocol.value;
    this.protocol.address =
      this.protocol.type === "SERIAL"
        ? this.CB_port_list.value
        : this.TB_address.value;
    this.protocol.baudRate = Number(this.CB_baudrate.value);
  }

  async update_portList() {
    const ports = await window.api.listSerialPorts();
    this.CB_remove_all_options(this.CB_port_list);
    this.CB_add_options(this.CB_port_list, ports);
  }

  async onclick_refresh() {
    this.update_portList();
  }

  async onclick_connect() {
    await this.update_protocol();
    await window.api.connectDevice(this.protocol);
  }

  async onclick_disconnect() {
    const response = await window.api.disconnectDevice();
    console.log(response);
    if (!response.connected) {
      this.setHidden(this.PB_disconnect, true);
      this.setHidden(this.PB_connect, false);
    }
  }

}
