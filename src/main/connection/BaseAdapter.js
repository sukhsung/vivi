import { EventEmitter } from "node:events";

export class BaseAdapter extends EventEmitter {
  constructor(protocol, verbose = 0) {
    super();

    this.verbose = verbose;
    this.protocol = protocol;
    this.encoding = protocol.encoding;
    this.delimiter = protocol.delimiter;
    this.timeout = 100;
    this.device = null;

    this._buffer = Buffer.alloc(0);
    this._readResolvers = [];
  }

  set_timeout(timeout) {
    this.timeout = timeout;
  }

  is_open() {
    return !!this.device?.isOpen;
  }

  async open() {
    if (this.is_open()) {
      this.log("Connection already open");
      return;
    }

    this.log("Opening");

    await this._open();
    this.device.on("open", () => this._on_open());
    this.device.on("data", (chunk) => this._on_data(chunk));
    this.device.on("close", () => this._on_close());
    this.device.on("error", (err) => {
      this.log(err.message);
    });

    this.device.open();
    await this.sleep(100);
  }

  close() {
    if (this.is_open()) {
      this._close_dev();
      this.device = null;
    }
  }

  flush() {
    throw new Error(
      `[${this.constructor.name}]: flush() not defined`,
    );
  }

  async write(msg) {
    let buf;
    if (typeof msg === "string") {
      buf = Buffer.from(msg, this.encoding);
    } else if (Buffer.isBuffer(msg)) {
      buf = msg;
    } else {
      throw new Error(`[BaseAdapter]: write() expects String or Buffer`);
    }
    await this.device.write(buf);
  }

  read(size) {
    return new Promise((resolve) => {
      if (this._buffer.length >= size) {
        const chunk = this._buffer.slice(0, size);
        this._buffer = this._buffer.slice(size);
        return resolve(chunk);
      }

      const timeoutId = setTimeout(() => {
        this._readResolvers = this._readResolvers.filter(
          (r) => r.resolve !== wrappedResolve,
        );
        const partial = this._buffer;
        this._buffer = Buffer.alloc(0);
        if (this.verbose >= 1) console.warn(
          `read timeout: returning partial data ${partial.length}/${size} bytes`,
        );
        resolve(partial);
      }, this.timeout);

      const wrappedResolve = (data) => {
        clearTimeout(timeoutId);
        resolve(data);
      };

      this._readResolvers.push({ size, resolve: wrappedResolve });
    });
  }

  read_all(timeout = this.timeout) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const result = this._buffer;
        this._buffer = Buffer.alloc(0);
        resolve(result);
      }, timeout);
    });
  }

  read_until(target, timeout = this.timeout) {
    if (!Buffer.isBuffer(target)) {
      target = Buffer.from(target, this.encoding);
    }

    return new Promise((resolve, reject) => {
      const check = () => {
        const idx = this._buffer.indexOf(target);
        if (idx !== -1) {
          const end = idx + target.length;
          const out = this._buffer.slice(0, end);
          this._buffer = this._buffer.slice(end);
          resolve(out);
          return true;
        }
        return false;
      };

      if (check()) return;

      const timeoutId = setTimeout(() => {
        reject(
          new Error(`read_until timeout: never found "${target.toString()}"`),
        );
      }, timeout);

      const poll = () => {
        if (check()) {
          clearTimeout(timeoutId);
        } else {
          setTimeout(poll, 5);
        }
      };

      poll();
    });
  }

  _on_open() {
    this.log("Open");
    this.flush();
  }

  _on_data(chunk) {
    this._buffer = Buffer.concat([this._buffer, chunk]);

    // Resolve any waiting read(size) promises if enough data has arrived
    this._readResolvers = this._readResolvers.filter(({ size, resolve }) => {
      if (this._buffer.length >= size) {
        const result = this._buffer.slice(0, size);
        this._buffer = this._buffer.slice(size);
        resolve(result);
        return false; // remove from list
      }
      return true;
    });
  }

  _on_close() {
    this.log("Connection closed");
    for (const { resolve } of this._readResolvers) {
      resolve(Buffer.alloc(0));
    }
    this._readResolvers = [];
    this._buffer = Buffer.alloc(0);
    this.emit("closed");
    this.device = null;
  }

  async sleep(ms) {
    this.log(`Sleeping for ${ms} ms`);
    return await new Promise((res) => setTimeout(res, ms));
  }

  log(msg) {
    if (this.verbose >= 3) {
      console.log(`[BaseAdapter]: ${msg}`);
    }
  }
}
