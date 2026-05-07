import net from "node:net";
import { BaseAdapter } from "./BaseAdapter.js";

export class TCPAdapter extends BaseAdapter {
  constructor(protocol, verbose = 0) {
    super(protocol, verbose);
  }

  async _open() {
    const host = this.protocol.address.split(":")[0];
    const port = parseInt(this.protocol.address.split(":")[1], 10);
    this.device = await net.createConnection({ host: host, port: port });
    this.device.setNoDelay(true);

    this.device.open = ()=>{}
    this.device.isOpen = true
  }

  flush() {
    this.log("Flush called (no-op for TCP)");
  }

  _close_dev() {
    this.device.destroy();
  }

  log(msg) {
    if (this.verbose >= 3) {
      console.log(`[TCPAdapter]: ${msg}`);
    }
  }
}
