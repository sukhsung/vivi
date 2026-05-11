import { LogManager as LogManagerBase } from "instrument-ui";
import path from "node:path";
import fs from "node:fs";

export class LogManager extends LogManagerBase {
  constructor(verbose) {
    super(verbose, path.join("Desktop", "vivi-log"));
    this.f_csv = null;
    this.f_json = null;
    this.f_fft = null;
  }

  async close() {
    this._print("Closing");
    await Promise.all([
      this.close_stream(this.f_csv),
      this.close_stream(this.f_json),
      this.close_stream(this.f_fft),
    ]);
  }

  close_stream(stream) {
    if (!stream || stream.closed || stream.destroyed) return Promise.resolve();
    return new Promise((resolve) => {
      stream.once("close", resolve);
      stream.end();
    });
  }

  write_data_raw(data) {
    data.forEach((line) => {
      this.f_csv.write(line.toString() + "\n");
    });
  }

  async write_data_fft(ffts) {
    ffts = this.transpose(ffts);
    ffts.forEach((line) => {
      this.f_fft.write(line.toString() + "\n");
    });
  }

  start_log(t_acquisition, settings) {
    this._print("Starting");
    const time_stamp = this.get_time();

    this.fname = `${time_stamp}`;
    let path_csv = path.join(this.path, `${this.fname}.csv`);
    let path_json = path.join(this.path, `${this.fname}.json`);
    let path_fft = path.join(this.path, `${this.fname}_fft.csv`);
    let counter = 0;

    while (fs.existsSync(path_csv)) {
      counter++;
      this.fname = `${time_stamp}_${counter}`;
      path_csv = path.join(this.path, `${this.fname}.csv`);
      path_fft = path.join(this.path, `${this.fname}_fft.csv`);
      path_json = path.join(this.path, `${this.fname}.json`);
    }

    this.f_csv = fs.createWriteStream(path_csv, { flags: "a" });
    this.f_json = fs.createWriteStream(path_json, { flags: "a" });
    this.f_fft = fs.createWriteStream(path_fft, { flags: "a" });

    this.f_csv.addListener("close", () => {
      this._print("f_csv closing");
      this.f_csv = null;
    });
    this.f_json.addListener("close", () => {
      this._print("f_json closing");
      this.f_json = null;
    });
    this.f_fft.addListener("close", () => {
      this._print("f_fft closing");
      this.f_fft = null;
    });

    const metadata = {
      acquisition_time: t_acquisition == 0 ? "live" : t_acquisition,
      settings: settings,
    };
    this.f_json.write(JSON.stringify(metadata, null, 2));
    this.f_json.end();

    this.emit(this.api_log.EVT_STATUS, {
      status: "started",
      fname: this.fname,
    });
  }

  stop_log() {
    if (!this.f_csv || !this.f_fft) return;
    this.f_csv.end();
    this.f_fft.end();
    this.emit(this.api_log.EVT_STATUS, {
      status: "finished",
      fname: this.fname,
    });
  }

  transpose(matrix) {
    return matrix[0].map((_, colIndex) => matrix.map((row) => row[colIndex]));
  }
}
