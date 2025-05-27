const net = require("net");
const EventEmitter = require("events");

class TCPDevice extends EventEmitter {
  constructor(protocol, verbose = false) {
    super();
    this.encoding = protocol.encoding || "utf8";
    this.verbose = verbose;

    this.host = protocol.address.split(":")[0];
    this.port = parseInt(protocol.address.split(":")[1], 10);
    this.timeout = 100;

    this._socket = null;
    this._buffer = Buffer.alloc(0);
    this._readResolvers = [];
  }

  open() {
    if (this._socket) {
      this._print("TCP connection already open");
      return;
    }

    this._socket = net.createConnection(
      { host: this.host, port: this.port },
      () => {
        this._print("TCP connection opened");
        this.emit("open", { open: true });
      }
    );

    this._socket.on("data", (chunk) => {
      this._buffer = Buffer.concat([this._buffer, chunk]);

      this._readResolvers = this._readResolvers.filter(({ size, resolve }) => {
        if (this._buffer.length >= size) {
          const result = this._buffer.slice(0, size);
          this._buffer = this._buffer.slice(size);
          resolve(result);
          return false;
        }
        return true;
      });
    });

    this._socket.on("error", (err) => {
      this._print("TCP Error: " + err.message, "r");
    });

    this._socket.on("close", () => {
      this._print("TCP connection closed");
      this.emit("open", { open: false });
      this._socket = null;
    });
  }

  close() {
    if (this._socket) {
      this._socket.destroy();
      this._socket = null;
    }
  }

  flush() {
    this._print("Flush called (no-op for TCP)");
  }

  write(msg) {
    if (typeof msg === "string") {
      msg = Buffer.from(msg, this.encoding);
    }
    this._socket?.write(msg);
  }

  set_timeout(timeout) {
    this.timeout = timeout;
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
          (r) => r.resolve !== wrappedResolve
        );
        const partial = this._buffer;
        this._buffer = Buffer.alloc(0);
        console.warn(
          `TCP read timeout: returning partial data ${partial.length}/${size} bytes`
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
          new Error(`read_until timeout: never found "${target.toString()}"`)
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

  _print(message, color = "y") {
    const col =
      color === "r"
        ? "\x1b[31m"
        : color === "g"
        ? "\x1b[32m"
        : color === "y"
        ? "\x1b[33m"
        : "\x1b[0m";

    if (this.verbose) {
      message = message.split("\n");
      if (message.length <= 1) {
        console.log(
          `\x1b[32m${this.constructor.name}:\x1b[0m ${col}${message[0]}\x1b[0m`
        );
      } else {
        console.log(`\x1b[32m${this.constructor.name}:\x1b[0m`);
        message.forEach((m) => {
          console.log(`    ${col}${m}\x1b[0m`);
        });
      }
    }
  }
}


module.exports = { TCPDevice };
