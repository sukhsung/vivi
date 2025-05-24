const { DeviceManager, list_serial_ports } = require("./deviceManager.js");
const { ADCProtocol } = require("./ADCProtocol.js");

class ADC8Manager extends DeviceManager {
  constructor(verbose = false) {
    super(verbose);

    this.settings = { sampling: null, adcs: null };
    this.board_type = null;
    this.STOP = null;

    this.NUM_FFT = null;
    this.NUM_CHANNELS = null;
    this.BIPOLAR = 2;
    this.is_acquiring = false;
  }

  async _init_device() {
    const responses = (await this.query("c")).split(this.delimiter);

    this.settings.adcs = [];
    let ch = 0;
    responses.forEach((line) => {
      if (line.startsWith("ADC ")) {
        ch++;
        this.settings.adcs.push({
          label: `Ch ${ch}`,
          gain: 128,
          polarity: 2,
          buffer: "u",
        });
      }
    });
    this.NUM_CHANNELS = this.settings.adcs.length;

    this.ADC_Protocol = new ADCProtocol(this.board_type, this.NUM_CHANNELS);

    // Default setting
    await this.setSampling(400);
    await this.setADC({ ch: 0, gain: 128, polarity: 2, buffer: "u" });
    // this.update_settings()
  }

  async _check_device() {
    // ADC8, 8x specific
    const lines = (await this.query("*")).split(this.delimiter);

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];
      if (line.length > 0) {
        if (line.startsWith("ADC-8 driver")) {
          this.board_type = "ADC-8";
          return true;
        } else if (line.startsWith("ADC-8x driver")) {
          this.board_type = "ADC-8x";
          return true;
        }
      }
    }

    return false;
  }

  async prepare_disconnect() {
    if (this.is_acquiring){
      await this.stop_acquisition();
    }
  }


  async setSampling(sampling) {
    const response = await this.query(`s ${sampling}`);
    // response = 'Sampling rate set to 400.00 Hz'
    const parts = response.split(" ");
    this.sampling = parseFloat(parts[parts.length - 2]);
    this._print(`Sampling set to ${this.sampling} Hz`);
  }

  async setADC(data) {
    // polarity = 1 or 2 (unipolar or bipolar)
    // buffer   = 'b' or 'u' (buffered or unbufferd)
    await this.query(
      `g ${data.ch} ${data.gain} ${data.polarity} ${data.buffer}`,
    );

    if (data.ch == 0) {
      // set all adcs
      this.settings.adcs.forEach((adc) => {
        adc.gain = data.gain;
        adc.polarity = data.polarity;
        adc.buffer = data.buffer;
      });
    } else {
      this.settings.adcs[data.ch - 1].gain = data.gain;
      this.settings.adcs[data.ch - 1].polarity = data.polarity;
      this.settings.adcs[data.ch - 1].buffer = data.buffer;
    }
  }

  async update_settings() {
    if (global.verbose) console.log("Updating status");

    // flush
    await this.device.read_all();

    const responses = (await this.query("c")).split(this.delimiter);

    responses.forEach((line) => {
      if (line.startsWith("Current settings:")) {
        // Sampling
        this.settings.sampling = parseFloat(line.split(" ").pop());
      } else if (line.startsWith("ADC ")) {
        const line_part = line.split(": ");
        const ch = parseInt(line_part[0].split(" ").pop());

        console.log(line_part[1]);
        const settings = line_part[1].split(", ");

        this.settings.adcs[ch - 1].gain = parseInt(
          settings[0].split(" ").pop(),
        );
        this.settings.adcs[ch - 1].polarity =
          settings[1] === "unipolar" ? 1 : 2;
        this.settings.adcs[ch - 1].buffer =
          settings[2] === "buffered" ? "b" : "u";
      }
    });

    this.emit("setting:update");
  }

  async update_labels(labels) {
    for (let i = 0; i < this.NUM_CHANNELS; i++) {
      this.settings.adcs[i].label = labels[i];
    }
  }

  async start_acquisition(t_acquire) {
    this.is_acquiring = true;
    this.emit("acquire:status", { status: "started" });
    this.STOP = false;
    await this.device.read_all();

    await this.write(`b${t_acquire}`);
    this.device.set_timeout(6000);

    await this.device.read_until(Buffer.from("+")); // Skip initial text

    const h = await this.device.read(this.ADC_Protocol.HDR_LEN);
    let sig;
    let hdr;
    if (h.length === this.ADC_Protocol.HDR_LEN) {
      const parser = this.ADC_Protocol.getHeaderParser();
      hdr = parser.parse(h);
      sig = hdr.signature;
    }

    let chans;
    if (sig === "ADC8") {
      chans = hdr.data;
    } else if (sig === "ADC8x-1.") {
      chans = hdr.data;
    } else {
      this._print("Invalid header received, transfer aborted",undefined,'r');
      this._write_buffer(Buffer.from("\n"));
      this.emit("status", { status: "error", message: "Invalid header" });
      return -1;
    }

    let num = 0;
    const gains = [];
    const bipolar = [];

    for (let i = 0; i < this.NUM_CHANNELS; i++) {
      const g = chans[2 * i];
      const b = chans[2 * i + 1] & this.BIPOLAR;

      gains.push(g);
      bipolar.push(b);

      if (g > 0) num++;
    }

    if (num === 0) {
      this._print("Header shows no active ADCs, transfer aborted",undefined,'r');
      this._write_buffer(Buffer.from("\n"));
      return -1;
    } else {
      this._print(`Header shows ${num} active ADCs`);
    }

    const blocksize = num * 3;
    let total_blocks = 0;
    let warned = false;
    let output_data = [];

    if (this.board_type === "ADC-8x" && this.NUM_CHANNELS === 4) {
      await this.device.read(8); // Skip extra header
    }

    let t0 = Date.now();
    let cont = true;
    while (cont) {
      if (t_acquire > 0) {
        let dt = Date.now() - t0;
        let progress = parseInt((dt / (t_acquire * 1000)) * 100);
        this.emit("acquire:status", { status: "progress", value: progress });
      } else {
        this.emit("acquire:status", { status: "progress", value: 0 });
      }

      const nBuf = await this.device.read(1);
      if (nBuf.length === 0) {
        console.log("Timeout");
        break;
      }

      let n = nBuf[0];
      if (n === 0) {
        console.log("End of data");
        break;
      }

      const d = await this.device.read(n);
      if (d.length < n) {
        console.log("Short data buffer received");
        break;
      }

      if (n % blocksize !== 0) {
        if (!warned) {
          console.log("Warning: Invalid buffer length", n);
          warned = true;
        }
        n -= n % blocksize;
      }

      for (let i = 0; i < n; i += blocksize) {
        const slice = d.slice(i, i + blocksize);
        const volts = this.ADC_Protocol.convert_values(
          slice,
          gains,
          bipolar,
          num,
        );
        output_data.push(volts);

        if (output_data.length === this.NUM_FFT) {
          this.emit("acquire:live-data", output_data);
          output_data = [];
          break;
        }
      }

      total_blocks += Math.floor(n / blocksize);

      if (this.STOP) {
        this._print("Acquisition Termination Requested");
        break;
      }
    }

    this._write_buffer(Buffer.from("\n"));
    this.device.set_timeout(this.default_timeout);
    await this.device.read_all(); // Flush

    if (t_acquire > 0) {
      this.emit("acquire:status", { status: "progress", value: 100 });
    }

    this._print("Acquisition has finished");
    this.is_acquiring = false;
    this.emit("acquire:status", { status: "finished" });
  }

  async stop_acquisition() {
    this._print("Stopping Acquisition");
    this.STOP = true;
    while (this.is_acquiring){
      this._print("Still Acquiring")
      await this._sleep( 300 )
    }
    return
  }
}

module.exports = { ADC8Manager, list_serial_ports };
