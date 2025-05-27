const { SerialDevice, list_serial_ports } = require("./serial.js");
const { TCPDevice } = require("./serial_tcp.js");
const EventEmitter = require("events");

class DeviceManager extends EventEmitter {
  constructor(verbose = false) {
    super();
    this.verbose = verbose;
    this.connected = false;
    this.default_timeout = 100;
    this.device = null;
  }

  // Connection Logic
  async connect_once(protocol) {
    // Attempt to connect once and return device validity
    this._print("Connecting");
    this.encoding = protocol.encoding;
    this.delimiter = protocol.delimiter;

    if (protocol.type === "SERIAL") {
      try {
        this.device = new SerialDevice(protocol, this.verbose);
        this.device.set_timeout(this.default_timeout);
        await this.device.open();
      } catch (error) {
        this._print(error.message);
        this.device = null;
        return;
      }
    } else if (protocol.type === "TCP") {
      try {
        this.device = new TCPDevice(protocol, this.verbose);
        this.device.set_timeout(this.default_timeout);
        await this.device.open();
      } catch (error) {
        this._print(error.message);
        this.device = null;
        return;
      }
    } else {
      this._print("Invalid protocol");
    }

    // wait `000 ms then validate device
    await this._sleep(1000);
    return await this.check_device();
  }

  async connect(protocol, retry = 2) {
    this._print(`Try connecting, up to ${retry} more times`);

    const isValid = await this.connect_once(protocol); // Actual Connection Logic

    this._print("Waiting 1 s, before checking");
    await this._sleep(1000);
    if (isValid) {
      this._print("Connected to valid device");
      this.connected = true;
      await this.init_device();
      this.emit("connection", { connected: true });
      return;
    } else if (retry > 0) {
      this._print("Not Connected, Retry");
      await this.connect(protocol, retry - 1);
    } else if (retry == 0) {
      this._print("Not Connected, Not retrying");
      this.connected = false;
      this.emit("connection", { connected: false });
      return;
    } else {
      this._print("Weird edge case...");
    }
  }

  // Disconnect Logic
  async disconnect() {
    this._print("Disconnecting", undefined, "r");
    if (this.connected) {
      await this.device.close();
      this.connected = false;
      this.device = null;
    }
    this.emit("connection", { connected: false });
  }

  async init_device() {
    this._print("Initializing device...");
    this.register_event_handlers();
    await this._init_device();
    return;
  }

  async _init_device() {
    return;
  }

  async prepare_disconnect() {
    return;
  }

  async on_port_close() {
    this._print("Received Port Closed", undefined, "r");
    this.close();
  }

  async close() {
    this._print("Closing", undefined, "r");
    await this.prepare_disconnect();
    await this.disconnect();
    return;
  }

  async register_event_handlers() {
    this.device.on("open", async (msg) => {
      if (msg.open === false) {
        await this.on_port_close();
      }
    });
  }

  async read() {
    // read everything then decode
    const msg = (await this.device.read_all()).toString(this.encoding);
    this._print(msg, this.constructor.name + ": Reading");
    return msg;
  }

  async write(msg) {
    this._print(msg, this.constructor.name + ": Writing");
    const buffer = Buffer.from(msg + this.delimiter, this.encoding);
    await this._write_buffer(buffer);
  }

  async query(msg) {
    await this.write(msg);
    return await this.read();
  }

  async check_device() {
    this._print("Checking for valid device");
    const isValid = await this._check_device();
    this._print(`Device Validity: ${isValid}`);
    return isValid;
  }

  async _check_device() {
    return true;
  }

  async run_command(msg) {
    await this.write(msg);
    const response = await this.read();
    await this.update_settings();
    return response;
  }

  isConnected() {
    return this.connected;
  }

  async _write_buffer(buffer) {
    this.device.write(buffer);
  }

  async _sleep(ms) {
    this._print(`Sleeping for ${ms} ms`);
    return await new Promise((res) => setTimeout(res, 1000));
  }

  _print(message, header = this.constructor.name, color = "y") {
    let col;
    if (color === "r") {
      col = "\x1b[31m";
    } else if (color === "g") {
      col = "\x1b[32m";
    } else if (color === "y") {
      col = "\x1b[33m";
    }

    if (this.verbose) {
      message = message.split("\n");

      if (message.length <= 1) {
        console.log("\x1b[32m%s:\x1b[0m %s%s\x1b[0m", header, col, message[0]);
      } else {
        console.log("\x1b[32m%s:\x1b[0m", header);
        message.forEach((m) => {
          console.log("    %s%s\x1b[0m", col, m);
        });
      }
    }
  }
}

module.exports = { DeviceManager, list_serial_ports };
