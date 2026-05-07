import { dialog, shell } from "electron";
import EventEmitter from "node:events";
import path from "node:path";
import os from "node:os";
import fs from "node:fs";

export class LogManager extends EventEmitter {
  constructor(verbose) {
    super();
    this.verbose = verbose;
    this.win = null;
    this.home = os.homedir();

    this.path = path.join(this.home, "vivi", this.get_date());
    this.mkdir(this.path);

    this.fname = null;
    this.f_csv = null;
    this.f_json = null;
    this.f_fft = null;
  }

  async close() {
    this._print("Closing");
    if (this.f_csv !== null) {
      this.f_csv.end();
    }
    if (this.f_json !== null) {
      this.f_json.end();
    }
    if (this.f_fft !== null) {
      this.f_fft.end();
    }
    return;
  }

  set_win(win) {
    this.win = win;
  }

  write_data_raw(data) {
    // Format Data
    data.forEach((line) => {
      this.f_csv.write(line.toString() + "\n");
    });
  }

  async write_data_fft(ffts) {
    ffts = this.transpose(ffts);
    // Format Data
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

    this.f_csv = fs.createWriteStream(path_csv, { flags: "a" }); // 'a' = append
    this.f_json = fs.createWriteStream(path_json, { flags: "a" });
    this.f_fft = fs.createWriteStream(path_fft, { flags: "a" });

    this.f_csv.addListener("close", () => {
      this._print( 'f_csv closing')
      this.f_csv = null;
    });
    this.f_json.addListener("close", () => {
      this._print( 'f_json closing')
      this.f_json = null;
    });
    this.f_fft.addListener("close", () => {
      this._print( 'f_fft closing')
      this.f_fft = null;
    });

    let metadata = {
      acquisition_time: t_acquisition == 0 ? "live" : t_acquisition,
      settings: settings,
    };
    this.f_json.write(JSON.stringify(metadata, null, 2));
    this.f_json.end();

    this.emit("log:status", { status: "started", fname: this.fname });
  }

  stop_log() {
    this.f_csv.end();
    this.f_fft.end();
    this.emit("log:status", { status: "finished", fname: this.fname });
  }

  get_time() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    return `${hours}${minutes}`;
  }

  async open_path() {
    shell.openPath(this.path);
  }

  async select_dir() {
    const result = await dialog.showOpenDialog(this.win, {
      properties: ["openDirectory"],
    });
    if (result.canceled) return null;

    this.path = path.join(result.filePaths[0], this.get_date());
    this.mkdir(this.path);

    return this.path;
  }

  get_date() {
    const today = new Date();
    return today.toISOString().split("T")[0]; // "YYYY-MM-DD"
  }

  mkdir(path) {
    this._print("Creating " + path);
    if (!fs.existsSync(path)) {
      fs.mkdirSync(path, { recursive: true });
    }
  }

  transpose(matrix) {
    return matrix[0].map((_, colIndex) => matrix.map((row) => row[colIndex]));
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
