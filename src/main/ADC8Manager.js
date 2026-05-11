import { DeviceManager } from "instrument-ui/main/DeviceManager.js";
import CH from "../common/ipcChannels.js";
import { ADCProtocol } from "./ADCProtocol.js";

const BIPOLAR = 2;
export const EVT_RAW_DATA = "vivi:raw-data";

export class ADC8Manager extends DeviceManager {
  constructor(verbose = false) {
    super(
      {
        board_type: null,
        NUM_CHANNELS: null,
      },
      verbose,
    );

    this.settings = { sampling: null, adcs: null, NUM_FFT: null };
    this.STOP = null;

    this.is_acquiring = false;

    this.api_device = CH.VIVI;
  }

  emit_acquisition_status(data) {
    this.emit_status({ kind: "acquire", ...data });
  }

  emit_raw_data(data) {
    this.emit(EVT_RAW_DATA, data);
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
    this.device_info.NUM_CHANNELS = this.settings.adcs.length;

    this.ADC_Protocol = new ADCProtocol(
      this.device_info.board_type,
      this.device_info.NUM_CHANNELS,
    );

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
          this.device_info.board_type = "ADC-8";
          return true;
        } else if (line.startsWith("ADC-8x driver")) {
          this.device_info.board_type = "ADC-8x";
          return true;
        }
      }
    }

    return false;
  }

  async prepare_disconnect() {
    if (this.is_acquiring) {
      await this.stop_acquisition();
    }
  }

  async run_command(msg) {
    await this.write(msg);
    const response = await this.read();
    await this.update_settings();
    return response;
  }

  async setSampling(sampling) {
    const response = await this.query(`s ${sampling}`);
    // response = 'Sampling rate set to 400.00 Hz'
    const parts = response.split(" ");
    this.settings.sampling = parseFloat(parts[parts.length - 2]);
    this.settings.sampling = this.settings.sampling;
    this.log(`Sampling set to ${this.settings.sampling} Hz`);
    this.emit_settings(this.settings);
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
    this.emit_settings(this.settings);
  }

  async setAllGain(data) {
    await this.query(`g 0 ${data.gain}`);

    // set all adcs
    this.settings.adcs.forEach((adc) => {
      adc.gain = data.gain;
      if ("polarity" in data) adc.polarity = data.polarity;
      if ("buffer" in data) adc.buffer = data.buffer;
    });
    this.emit_settings(this.settings);
  }

  async update_settings() {
    this.log("Updating status");

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

        this.log(line_part[1]);
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

    this.emit_settings(this.settings);
  }

  async update_labels(labels) {
    for (let i = 0; i < this.device_info.NUM_CHANNELS; i++) {
      this.settings.adcs[i].label = labels[i];
    }
  }

  async start_acquisition(t_acquire, t_delay) {
    this.is_acquiring = true;
    this.STOP = false;

    // Delay Logic
    this.log(`Delay for ${t_delay}s`);
    this.emit_acquisition_status({ status: "delay" });

    let delay = true;
    let t0 = Date.now();
    let t_elapsed = 0;
    let progress = 100;
    while (delay) {
      t_elapsed = (Date.now() - t0) / 1000;
      progress = parseInt((t_elapsed / t_delay) * 100);

      this.emit_acquisition_status({
        status: "progress",
        value: 100 - progress,
      });
      if (t_elapsed >= t_delay) {
        delay = false;
      } else {
        await this.sleep(10, false);
      }

      if (this.STOP) {
        this.log("Acquisition Termination Requested");
        break;
      }
    }

    // Acquisition Cycle
    let mode;
    if (t_acquire == 0) {
      mode = "live";
    } else if (t_acquire > 0) {
      mode = "acquire";
    }
    this.emit_acquisition_status({ status: "started", mode: mode });
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
      this.log("Invalid header received, transfer aborted", undefined, "r");
      this._write_buffer(Buffer.from("\n"));
      this.emit_acquisition_status({
        status: "error",
        message: "Invalid header",
      });
      return -1;
    }

    let num = 0;
    const gains = [];
    const bipolar = [];

    for (let i = 0; i < this.device_info.NUM_CHANNELS; i++) {
      const g = chans[2 * i];
      const b = chans[2 * i + 1] & BIPOLAR;

      gains.push(g);
      bipolar.push(b);

      if (g > 0) num++;
    }

    if (num === 0) {
      this.log("Header shows no active ADCs, transfer aborted", undefined, "r");
      this._write_buffer(Buffer.from("\n"));
      return -1;
    } else {
      this.log(`Header shows ${num} active ADCs`);
    }

    const blocksize = num * 3;
    let total_blocks = 0;
    let warned = false;
    let output_data = [];

    if (
      this.device_info.board_type === "ADC-8x" &&
      this.device_info.NUM_CHANNELS === 4
    ) {
      await this.device.read(8); // Skip extra header
    }

    t0 = Date.now();
    let cont = true;
    while (cont) {
      if (t_acquire > 0) {
        let dt = Date.now() - t0;
        let progress = parseInt((dt / (t_acquire * 1000)) * 100);
        this.emit_acquisition_status({
          status: "progress",
          value: progress,
        });
      } else {
        this.emit_acquisition_status({ status: "progress", value: 0 });
      }

      const nBuf = await this.device.read(1);
      if (nBuf.length === 0) {
        this.log("Timeout");
        break;
      }

      let n = nBuf[0];
      if (n === 0) {
        this.log("End of data");
        break;
      }

      const d = await this.device.read(n);
      if (d.length < n) {
        this.log("Short data buffer received");
        break;
      }

      if (n % blocksize !== 0) {
        if (!warned) {
          this.log("Warning: Invalid buffer length", n);
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

        if (output_data.length === this.settings.NUM_FFT) {
          this.emit_raw_data(output_data);
          output_data = [];
          break;
        }
      }

      total_blocks += Math.floor(n / blocksize);

      if (this.STOP) {
        this.log("Acquisition Termination Requested");
        break;
      }
    }

    this._write_buffer(Buffer.from("\n"));
    this.device.set_timeout(this.default_timeout);
    await this.device.read_all(); // Flush

    if (t_acquire > 0) {
      this.emit_acquisition_status({ status: "progress", value: 100 });
    }

    this.log("Acquisition has finished");
    this.is_acquiring = false;
    this.emit_acquisition_status({ status: "finished" });
  }

  async stop_acquisition() {
    this.log("Stopping Acquisition");
    this.STOP = true;
    while (this.is_acquiring) {
      this.log("Still Acquiring");
      await this.sleep(300);
    }
    return;
  }
}
