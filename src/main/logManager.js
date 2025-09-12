const { dialog, shell } = require("electron");
const EventEmitter = require("events");

const path = require("path");
const os = require("os");
const fs = require("fs");

class LogManager extends EventEmitter {
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
  }

  async close() {
    this._print("Closing");
    if (this.f_csv !== null) {
      this.f_csv.end();
      this.f_csv = null;
    }
    if (this.f_json !== null) {
      this.f_json.end();
      this.f_json = null;
    }
    return;
  }

  set_win(win) {
    this.win = win;
  }

  write_data(data) {
    // Format Data
    data.forEach((line) => {
      this.f_csv.write(line.toString() + "\n");
    });
  }

  start_log(t_acquisition, settings) {
    this._print("Starting");
    const time_stamp = this.get_time();

    this.fname = `${time_stamp}`;
    let path_csv = path.join(this.path, `${this.fname}.csv`);
    let path_json = path.join(this.path, `${this.fname}.json`);
    let counter = 0;

    while (fs.existsSync(path_csv)) {
      counter++;
      this.fname = `${time_stamp}_${counter}`;
      path_csv = path.join(this.path, `${this.fname}.csv`);
      path_json = path.join(this.path, `${this.fname}.json`);
    }

    this.f_csv = fs.createWriteStream(path_csv, { flags: "a" }); // 'a' = append
    this.f_json = fs.createWriteStream(path_json, { flags: "a" }); // 'a' = append

    let metadata = {
      acquisition_time: t_acquisition == 0 ? "live" : t_acquisition,
      settings: settings,
    };
    this.f_json.write(JSON.stringify(metadata, null, 2));
    this.f_json.end();
    this.f_json = null;

    this.emit("log:status", { status: "started", fname: this.fname });
  }

  stop_log() {
    this.f_csv.end();
    // this.f_csv = null;
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
    console.log("Creating " + path);
    if (!fs.existsSync(path)) {
      fs.mkdirSync(path, { recursive: true });
    }
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

module.exports = { LogManager };
