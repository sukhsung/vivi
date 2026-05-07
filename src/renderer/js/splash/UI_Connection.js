import { UI_Manager } from "../UI_Manager.js";
export { UI_ConnectionManager };

const BAUDRATES = [
  4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600,
];

class UI_ConnectionManager extends UI_Manager {
  constructor(
    name,
    device_type,
    encoding,
    delimiter,
    t_interval = 250,
    order,
    verbose = false,
  ) {
    super("connection-container", verbose);

    this.name = name;
    this.device_info = { type: device_type };
    this.protocol = {
      address: null,
      type: null,
      baudRate: null,
      encoding: encoding,
      delimiter: delimiter,
      t_interval: t_interval,
    };

    const api_map = {
      vivi: window.api_vivi,
    };
    this.api_device = api_map[device_type];
    this.order = order;
  }

  async get_current_status() {
    const data = await this.api_device.is_connected();
    this.print(data);
    if (data.connected) {
      this.received_connected(data.protocol);
    } else {
      this.received_disconnected();
    }
  }

  received_connected(protocol) {
    this.print("received connected");
    this.PB_connect.disabled = true;
    this.PB_refresh.disabled = true;
    this.CB_baudrate.disabled = true;
    this.TB_address.disabled = true;
    this.CB_protocol.disabled = true;
    this.CB_port_list.disabled = true;
    this.PB_disconnect.disabled = false;
    this.PB_disconnect.textContent = "Disconnect";
    this.setHidden(this.PB_connect, true);
    this.setHidden(this.PB_disconnect, false);

    this.protocol = protocol;
    this.update_protocol();
  }
  received_disconnected() {
    this.print("received disconnected");
    this.PB_connect.disabled = false;
    this.PB_refresh.disabled = false;
    this.CB_baudrate.disabled = false;
    this.TB_address.disabled = false;
    this.CB_protocol.disabled = false;
    this.CB_port_list.disabled = false;
    this.PB_connect.textContent = "Connect";
    this.PB_disconnect.disabled = true;
    this.setHidden(this.PB_connect, false);
    this.setHidden(this.PB_disconnect, true);

    this.update_portList();
  }

  async _initialize(conn_config) {
    const {
      address = "",
      protocol = "TCP",
      baudrate = 115200,
    } = conn_config ?? {};

    const [wrapper] = await this._create_connection_setting();
    wrapper.classList.add(`order-${this.order}`);
    this.div_main.appendChild(wrapper);

    const div_label = wrapper.querySelector("#label");
    this.UI_portlist = wrapper.querySelector("#UI_portlist");
    this.UI_address = wrapper.querySelector("#UI_address");
    this.CB_protocol = wrapper.querySelector("#protocol");
    this.CB_port_list = wrapper.querySelector("#port_list");
    this.CB_baudrate = wrapper.querySelector("#baudrate");
    this.PB_refresh = wrapper.querySelector("#refresh");
    this.PB_connect = wrapper.querySelector("#connect");
    this.PB_disconnect = wrapper.querySelector("#disconnect");
    this.TB_address = wrapper.querySelector("#address");

    div_label.textContent = this.name;

    this.CB_protocol.onchange = () => this.onchange_protocol();
    // this.TB_address.oninput = () => this.oninput_address();
    this.CB_port_list.onchange = () => this.onchange_port();

    this.CB_add_options(this.CB_baudrate, BAUDRATES);
    const baudrateIdx = BAUDRATES.indexOf(baudrate);
    this.CB_baudrate.selectedIndex = baudrateIdx >= 0 ? baudrateIdx : 5;

    this.PB_connect.onclick = () => this.onclick_connect();
    this.PB_disconnect.onclick = () => this.onclick_disconnect();
    this.PB_disconnect.disabled = true;
    this.PB_refresh.onclick = () => this.onclick_refresh();

    this.update_portList();
    this.TB_address.value = address;
    this.CB_protocol.value = protocol;
    this.onchange_protocol();

    await this.get_current_status();
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
    const ports = await window.api_device_manager.listSerialPorts();
    this.CB_remove_all_options(this.CB_port_list);
    this.CB_add_options(this.CB_port_list, ports);
  }

  async onclick_refresh() {
    this.PB_refresh.disabled = true;
    await this.update_portList();
    this.PB_refresh.disabled = false;
  }

  async onclick_connect() {
    this.PB_connect.textContent = "Connecting...";
    this.PB_connect.disabled = true;
    this.PB_refresh.disabled = true;
    this.CB_baudrate.disabled = true;
    this.TB_address.disabled = true;
    this.CB_protocol.disabled = true;
    this.CB_port_list.disabled = true;

    await this.update_protocol();
    this.api_device.connect({
      device_info: this.device_info,
      protocol: this.protocol,
    });
  }

  async onclick_disconnect() {
    this.PB_connect.textContent = "Disconnecting...";
    this.PB_disconnect.disabled = true;
    this.api_device.disconnect();
  }

  async _create_connection_setting() {
    // const template = document.getElementById("template-connection");
    const template = await this.import_template(
      "./templates/template_connection.html",
    );
    const clone = template.content.cloneNode(true);

    const wrapper = clone.querySelector("div");

    return [wrapper];
  }
}
