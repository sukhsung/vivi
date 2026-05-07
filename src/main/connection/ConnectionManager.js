import { SerialAdapter } from "./SerialAdapter.js";
import { TCPAdapter } from "./TCPAdapter.js";
import { EventEmitter } from "node:events";

export class ConnectionManager extends EventEmitter {
  constructor(verbose = 0) {
    super();
    this.verbose = verbose;
    this.adapter = null;
    this.protocol = null;
    this.default_timeout = 100;
    this._opening = false;
  }

  is_open() {
    return !!this.adapter?.is_open();
  }

  async _open_once(protocol) {
    try {
      this.adapter = await this._make_adapter(protocol);
      await this.adapter.open();
    } catch (error) {
      this.log(error.message);
      this.adapter = null;
    }
  }

  async open(protocol, attempts = 3) {
    if (this._opening) return;
    this._opening = true;
    let t_sleep = 500;

    try {
      while (attempts > 0) {
        this.log(`Try connecting, up to ${attempts} more times`);
        await this._open_once(protocol);
        if (this.is_open()) {
          this.log("Opened");
          this.adapter.set_timeout(this.default_timeout)
          break;
        } else {
          attempts--;
          await this.sleep(t_sleep);
          t_sleep *= 2;
        }
      }

      if (attempts === 0) {
        this.log("Exhausted open attempts");
      }
    } finally {
      this._opening = false;
    }
  }

  async _make_adapter(protocol) {
    let adapter = null;
    if (protocol.type === "SERIAL") {
      this.protocol = protocol;
      adapter = new SerialAdapter(protocol, this.verbose);
    } else if (protocol.type === "TCP") {
      this.protocol = protocol;
      adapter = new TCPAdapter(protocol, this.verbose);
    } else {
      throw new Error(
        `[ConnectionController]: unsupported protocol: ${protocol.protocol}`,
      );
    }

    // await this.sleep(100)
    return adapter;
  }

  async sleep(ms) {
    this.log(`Sleeping for ${ms} ms`);
    return await new Promise((res) => setTimeout(res, ms));
  }

  log(msg) {
    if (this.verbose >= 2) {
      console.log(`[ConnectionManager]: ${msg}`);
    }
  }
}
