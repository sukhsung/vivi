const { SerialDevice, list_serial_ports } = require("./serial.js");
const EventEmitter = require("events");

class DeviceManager extends EventEmitter {
  constructor(verbose = false) {
    super();
    this.verbose = verbose;
    this.connected = false;
    this.default_timeout = 100;
    this.device = null
  }

  async tryConnect( protocol, retry=true){
    this.protocol = protocol
    this.connect( this.protocol )

    this.print( "Waiting 1 s, before checking")
    await new Promise(res => setTimeout(res, 1000));
    if (this.connected) {
      this.print('Actually Connected')
    } else if (retry) {
      this.print('Not Connected, Retry')
      this.tryConnect( this.protocol, false)
    }

  }

  isConnected() {
    return this.connected
  }

  register_event_handlers() {
    this.device.on("open", (msg) => {
      if (msg.open) {
        this.onreceived_open();
      } else {
        this.onreceived_close();
      }
    });
  }

  async onreceived_close() {
    this.print("Port is closed");
    this.connected = false;
    this.device = null
    this.emit("connection", { connected: false });
  }

  async onreceived_open() {
    const devValid = await this.check_device();

    if (!devValid) {
      this.print("Invalid device, closing port");
      this.device.port.close();
      this.connected = false;

    } else {
      this.print("Device check passed");
      await this.initialize();

      this.connected = true;
      this.emit("connection", { connected: true });
    }
  }

  async disconnect() {
    this.print("Disconnecting");
    if (this.connected) {
      this.device.close();
    }
  }

  async connect(protocol) {
    this.print("Connecting");
    this.encoding = protocol.encoding;
    this.delimiter = protocol.delimiter;

    if (protocol.type === "SERIAL") {
      try {
        this.device = new SerialDevice(protocol, this.verbose);
        this.register_event_handlers();
        this.device.set_timeout(this.default_timeout);
        await this.device.open();
      } catch (error) {
        this.print(error.message)
        this.device = null
        this.emit("connection", { connected: false });
      }
    }
  }

  async query( msg ) {
    await this.write(msg)
    return await this.read()
  }

  async read() {
    // read everything then decode
    const msg = (await this.device.read_all()).toString(this.encoding);
    this.print( msg, this.constructor.name +': Reading' )
    return msg;
  }

  async _write(buffer) {
    this.device.write(buffer);
  }

  async write(msg) {
    this.print( msg, this.constructor.name +': Writing' )
    const buffer = Buffer.from(msg + this.delimiter, this.encoding);
    await this._write(buffer);
  }

  async initialize() {
    print("Initializing device...");
    return;
  }

  async check_device() {
    return  await this._check_device()
  }

  async _check_device() {
    print("Checking for valid device");
    return true;
  }

  async run_command(msg) {
    await this.write(msg);
    const response = await this.read();
    await this.update_settings();
    return response;
  }

  print(message, header=this.constructor.name) {
    if (this.verbose) {
      message = message.split('\n')

      if (message.length <= 1) {
        console.log("\x1b[32m%s:\x1b[0m \x1b[33m%s\x1b[0m" , header, message[0]);
      }
      else {
          console.log("\x1b[32m%s:\x1b[0m" , header);
        message.forEach( m => {
          console.log("    \x1b[33m%s\x1b[0m" , m);
        });
      }
    }
  }
}

module.exports = { DeviceManager, list_serial_ports };
