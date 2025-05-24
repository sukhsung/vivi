const { SerialPort } = require("serialport");
const EventEmitter = require("events");

class SerialDevice extends EventEmitter {
  constructor(protocol, verbose = false) {
    super();
    this.encoding = protocol.encoding;
    this.verbose = verbose;

    this.port = new SerialPort({
      path: protocol.address,
      baudRate: protocol.baudRate,
      autoOpen: false,
    });
    // If Port is already open, close
    if (this.port.isOpen) this.port.close();
    this.register_event_handlers();

    this.timeout = 100; // Default timeout in ms

    this._buffer = Buffer.alloc(0);
    this._readResolvers = [];
  }

  register_event_handlers() {
    // register event handlers
    this.port.on("open", (err) => {
      if (err) {
        this._print("Fail to open serial port");
      } else {
        this._print("Serial Port is open");
      }
      this.flush();
      this.emit("open", { open: true });
    });

    this.port.on("close", (err) => {
      if (err) {
        if (err.disconnected) {
          this._print("Serial port is disconnected");
        } else {
          this._print("Fail to close serial port");
        }
      } else {
        this._print("serial Port is closed");
      }

      this.emit("open", { open: false });
    });

    this.port.on("error", (err) => {
      this._print(err.message);
    });

    this.port.on("data", (chunk) => {
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
    });
  }

  set_timeout(timeout) {
    this.timeout = timeout;
  }

  flush() {
    if (this.port.isOpen) {
      this._print("Flushing");
      this.port.flush();
    }
  }

  open() {
    if (!this.port.isOpen) {
      this.port.open();
    } else {
      this._print("Port is already open");
    }
  }

  close() {
    if (this.port.isOpen) {
      this.port.close();
    }
  }

  write(msg) {
    this.port.write(msg);
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
        this._buffer = new Uint8Array(); // clear buffer
        console.warn(
          `Serial read timeout: returning partial data ${partial.length}/${size} bytes`,
        );
        resolve(partial);
      }, this.timeout);

      const wrappedResolve = (data) => {
        clearTimeout(timeoutId);
        resolve(data);
      };

      this._readResolvers.push({
        size,
        resolve: wrappedResolve,
      });
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

async function list_serial_ports() {
  const ports = await SerialPort.list();
  const validPorts = ports
    .filter((port) => port.productId !== undefined) // Check if PID exist
    .map((port) => port.path); // Return just the path (e.g., "/dev/ttyUSB0")

  return validPorts;
}

module.exports = { SerialDevice, list_serial_ports };
