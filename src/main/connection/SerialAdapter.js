import { SerialPort } from "serialport";
import { BaseAdapter } from "./BaseAdapter.js";

export class SerialAdapter extends BaseAdapter {
  constructor(protocol, verbose = 0) {
    super(protocol, verbose);
  }

  async _open() {
    this.device = new SerialPort({
      path: this.protocol.address,
      baudRate: this.protocol.baudRate,
      autoOpen: false,
      lock: false,
    });
    
  }

  flush() {
    if (this.is_open()) {
      this.log("Flushing");
      this.device.flush();
    } else {
      this.log("Device not open, can't flush");
    }
  }

  _close_dev() {
    this.device.close();
  }

  log(msg) {
    if (this.verbose >= 3) {
      console.log(`[SerialAdapter]: ${msg}`);
    }
  }
}
