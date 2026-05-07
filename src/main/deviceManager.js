import { EventEmitter } from "node:events";
import { ConnectionManager } from "./connection/ConnectionManager.js";

export class DeviceManager extends EventEmitter {
  constructor(device_info, verbose = 0) {
    super();
    this.verbose = verbose;
    this.device_info = device_info;

    this.connection_manager = new ConnectionManager(verbose);
    this.protocol = null;
    this.connected = false;
    this.default_timeout = 50;
    this.device = null;

    this.t_interval = null; // in ms

    this.reset_request();
    this._stoppedResolve = null;
    this._stopped = Promise.resolve(); // initial resolved
    this.running = false;

    this.api_device = null;
  }

  is_connected() {
    const connected = this.connected;
    const protocol = this.protocol;
    return { connected: connected, protocol: protocol };
  }

  emit_status(data) {
    this.emit(this.api_device.EVT_STATUS, data);
  }

  emit_settings(data) {
    this.emit(this.api_device.EVT_SETTINGS, data);
  }

  emit_connection() {
    const device_info = this.device_info;
    const protocol = this.protocol;
    const connected = this.connected;

    if (this.api_device) {
      this.emit(this.api_device.EVT_CONNECTION, {
        device_info: device_info,
        connected: connected,
        protocol: protocol,
      });
    }
  }

  async _connect(protocol) {
    return true;
  }

  // Connection Logic
  async connect(protocol) {
    this.connected = false;

    // Try Opening Connection
    await this.connection_manager.open(protocol, 1);
    if (!this.connection_manager.is_open()) {
      this.protocol = null;
      this.device = null;
      this.emit_connection();
      return;
    }
    this.device = this.connection_manager.adapter;
    this.protocol = protocol;
    this.encoding = protocol.encoding;
    this.delimiter = protocol.delimiter;

    if (!(await this._connect(protocol))) {
      this.protocol = null;
      this.device = null;
      this.emit_connection();
      return;
    }

    // If Open wait 500 ms then validate device
    // await this.sleep(500);
    if (await this.check_device()) {
      this.log("Connected to valid device");
      this.connected = true;
      this.protocol = protocol;
      this.t_interval = protocol.t_interval;
      await this.init_device();
      this.emit_connection();
    }
  }

  // Disconnect Logic
  async disconnect() {
    this.log("Disconnecting", undefined, "r");
    if (this.connected) {
      await this.prepare_disconnect();
      await this.device.close();
      this.connected = false;
      this.device = null;
    }
    this.emit_connection();
  }

  // Communication Logic

  async start_comm() {
    this.log("Starting Comm");
    if (this.running) return; // guard reentrancy
    this.running = true;
    this.requests = [];

    // create a promise that resolves when we stop
    this._stopped = new Promise((r) => (this._stoppedResolve = r));

    try {
      while (this.running) {
        if (this.requests.length === 0) {
          await this.process_regular();
          // optional: check running again before sleeping
          if (!this.running) break;
          await this.sleep(this.t_interval);
        } else {
          await this.process_request();
        }
      }
    } catch (err) {
      // log/handle as appropriate
      this.log?.("Comm error: " + ((err && err.message) || err));
      // decide whether to rethrow or swallow
    } finally {
      this.log?.("Comm Stopped");
      this._stoppedResolve?.(); // unblock stop_comm()
      this._stoppedResolve = null;
    }
  }

  async stop_comm() {
    this.running = false;
    this.requests = [];
    // Await the loop finishing without polling
    await this._stopped;
  }

  // Request Logics
  reset_request() {
    this._idx_req = 0;
    this.requests = [];
  }

  add_to_requests(request) {
    const idx = this._idx_req;
    this.requests.push({ index: idx, request: request });
    this._idx_req++;
  }

  async process_request() {
    this.log("Processing Request");
    const request = this.requests.shift();
    this.log(request);
    await this._process_request(request);
  }

  async _process_request(req) {
    this.log("Processing Request");
    return;
  }

  async process_regular() {
    await this._process_regular();
  }

  async _process_regular() {
    this.log("Processing Regular");
    return;
  }

  async init_device() {
    this.log("Initializing device...");
    this.register_event_handlers();
    await this._init_device();
    return;
  }

  async _init_device() {
    return true;
  }

  async prepare_disconnect() {
    this.log("Preparing to Disconnect");
    await this._prepare_disconnect();
    await this.stop_comm();
  }

  async on_port_close() {
    this.log("Received Port Closed", undefined, "r");
    this.close();
  }

  async close() {
    this.log("Closing", undefined, "r");
    await this.disconnect();
    return;
  }

  async register_event_handlers() {
    this.device.on("open", async (msg) => {
      if (msg.open === false) {
        await this.on_port_close();
      }
    });

    this.device.on("closed", () => {
      this.running = false;
      this.emit(this.api_device.EVT_CONNECTION, {
        device_info: null,
        connected: false,
        protocol: null,
      });
    });
  }

  async read() {
    // read everything then decode
    const msg = (await this.device.read_all()).toString(this.encoding);
    return msg;
  }

  async write(msg) {
    await this.device.write(msg + this.delimiter);
  }

  async query(msg) {
    await this.write(msg);
    return await this.read();
  }

  async query_s(msg) {
    // return delimiter stripped, single line response
    // assume a single line respone
    return (await this.query(msg)).split(this.delimiter)[0];
  }

  async check_device() {
    this.log("Checking for valid device");
    const isValid = await this._check_device();
    this.log(`Device Validity: ${isValid}`);
    return isValid;
  }

  async _check_device() {
    return true;
  }

  async _write_buffer(buffer) {
    this.device.write(buffer);
  }

  async sleep(ms) {
    // this.log(`Sleeping for ${ms} ms`);
    return await new Promise((res) => setTimeout(res, ms));
  }

  log(msg) {
    if (this.verbose >= 2) {
      console.log(`[DeviceManager]: ${msg}`);
    }
  }
}
