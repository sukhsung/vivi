const { SerialPort } = require("serialport");

class SerialDevice {
  constructor(protocol) {
    this.port = new SerialPort({
      path: protocol.address,
      baudRate: protocol.baudRate,
      autoOpen: false,
    });

    this.encoding = protocol.encoding;

    this.timeout = 100; // Default timeout in ms
    this._buffer = Buffer.alloc(0);
    this._readResolvers = [];

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

    this.port.on("open", () => {
      if (global.verbose) {
        console.log("Serial Port is Open");
      }
    });

    this.port.open((err) => {
      if (err) {
        console.error("Error opening serial port:", err.message);
      } else if (global.verbose) {
        console.log("Serial Port is Open");
      }
    });
  }

  set_timeout(timeout) {
    this.timeout = timeout;
  }
  close() {
    if (!this.port?.isOpen) return;

    this.port.close((err) => {
      if (err) console.error("Serial port close error:", err.message);
      else if (global.verbose) console.log("Serial port closed.");
    });
  }

  write(msg) {
    this.port.write(msg, (err) => {
      if (err) console.error("Write error:", err.message);
    });
  }

  read(size) {
    return new Promise((resolve, reject) => {
      if (this._buffer.length >= size) {
        const chunk = this._buffer.slice(0, size);
        this._buffer = this._buffer.slice(size);
        return resolve(chunk);
      }

      const timeoutId = setTimeout(() => {
        this._readResolvers = this._readResolvers.filter(
          (r) => r.resolve !== resolve
        );
        reject(
          new Error(
            `Timeout: Only received ${this._buffer.length}/${size} bytes`
          )
        );
      }, this.timeout);

      this._readResolvers.push({
        size,
        resolve: (data) => {
          clearTimeout(timeoutId);
          resolve(data);
        },
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
}

async function list_serial_ports() {
  const ports = await SerialPort.list();
  const validPorts = ports
    .filter((port) => port.productId !== undefined) // Check if PID exist
    .map((port) => port.path); // Return just the path (e.g., "/dev/ttyUSB0")

  return validPorts;
}

module.exports = { SerialDevice, list_serial_ports };
