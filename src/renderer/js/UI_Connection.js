import { UI_Manager } from "./UI_Manager.js";
export { UI_ConnectionManager };

const BAUDRATES = [
  4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600,
];

class UI_ConnectionManager extends UI_Manager {
  constructor( verbose=false ) {
    super(verbose)
    this.protocol = {
      address: null,
      type: null,
      baudRate: null,
      encoding: "utf8",
      delimiter: "\n",
    };
  }

  received_connected(){
    this.print( "received connected")
    this.PB_connect.disabled = true
    this.PB_disconnect.disabled = false
    this.PB_disconnect.innerHTML = 'Disconnect'
    this.setHidden( this.PB_connect, true )
    this.setHidden( this.PB_disconnect,false )

  }
  received_disconnected(){
    this.print( "received disconnected")
    this.PB_connect.disabled = false
    this.PB_refresh.disabled = false
    this.CB_baudrate.disabled = false
    this.TB_address.disabled = false
    this.CB_protocol.disabled = false
    this.CB_port_list.disabled = false
    this.PB_connect.innerHTML = 'Connect'
    this.PB_disconnect.disabled = true
    this.setHidden( this.PB_connect, false )
    this.setHidden( this.PB_disconnect,true )

    this.update_portList()
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
    const ports = await window.api_connection.listSerialPorts();
    this.CB_remove_all_options(this.CB_port_list);
    this.CB_add_options(this.CB_port_list, ports);
  }

  async onclick_refresh() {
    await this.update_portList();
    this.PB_refresh.disabled = true
    this.PB_refresh.disabled = false
  }

  async onclick_connect() {
    this.PB_connect.innerHTML = 'Connecting...'
    this.PB_connect.disabled = true
    this.PB_refresh.disabled = true
    this.CB_baudrate.disabled = true
    this.TB_address.disabled = true
    this.CB_protocol.disabled = true
    this.CB_port_list.disabled = true

    await this.update_protocol();
    window.api_connection.connectDevice(this.protocol);
  }

  async onclick_disconnect() {
    this.PB_connect.innerHTML = 'Disonnecting...'
    this.PB_disconnect.disabled = true
    window.api_connection.disconnectDevice();
  }

}
