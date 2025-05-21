const { SerialDevice, list_serial_ports } = require("./serial.js");
const EventEmitter = require("events");

class DeviceManager extends EventEmitter {
  constructor() {
    super();
    this.connected = false;
    this.default_timeout = 100;
  }

  async disconnect() {
    this.device.close();
    this.connected = false;

    this.emit("status", { status: "disconnected" });
  }

  async connect(protocol) {
    this.encoding = protocol.encoding;
    this.delimiter = protocol.delimiter;

    if (protocol.type === "SERIAL") {
      this.device = new SerialDevice(protocol);
      this.device.set_timeout(this.default_timeout);
    }

    const devValid = await this.check_device();

    if (!devValid) {
      if (global.verbose) console.log("Invalid device, closing port");
      this.device.port.close();
    } else {
      if (global.verbose) console.log("Device check passed");
      await this.initialize();
    }

    this.connected = devValid;

    const status = {
      status: "connected",
      NUM_CHANNELS: this.NUM_CHANNELS,
      settings: this.settings,
    };
    this.emit("status", status);
    return status;
  }

  async read() {
    // read everything then decode
    const msg = (await this.device.read_all()).toString(this.encoding);
    if (global.verbose) {
      console.log("Reading :" + msg);
    }
    return msg;
  }

  async _write(buffer) {
    try {
      this.device.write(buffer);
    } catch (e) {
      console.error("Serial write error:", e);
    }
  }

  async write(msg) {
    if (global.verbose) {
      console.log("Writing :" + msg);
    }
    const buffer = Buffer.from(msg + this.delimiter, this.encoding);
    this._write(buffer);
  }

  async initialize() {
    if (global.verbose) console.log("Initializing device...");
    return;
  }

  async check_device() {
    if (global.verbose) console.log("Checking for valid device");
    return true;
  }

  async run_command(msg) {
    await this.write(msg);
    const response = await this.read();
    await this.update_settings();
    return response;
  }
}

module.exports = { DeviceManager, list_serial_ports };
