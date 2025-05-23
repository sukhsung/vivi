import { UI_Manager } from "./UI_Manager.js";
export { UI_AcquisitionManager };

class UI_AcquisitionManager extends UI_Manager {
  constructor() {
    super();
  }

  initialize() {
    this.cacheDOM({
      TB_NUM_FFT: "TB_NUM_FFT",
      TB_acquireTime: "TB_acquireTime",
      PB_view_start: "PB_view_start",
      PB_view_stop: "PB_view_stop",
      PB_acquire_start: "PB_acquire_start",
      PB_stop: "PB_stop",
      progress: "progress",
    });

    this.t_acquire = parseInt(this.TB_acquireTime.value);
    this.NUM_FFT = parseInt(this.TB_NUM_FFT.value);

    this.register_handler_NUM_FFT();
    this.register_handler_t_acquire();

    this.PB_view_start.onclick = () => {
      this.onclick_view();
    };
    this.PB_acquire_start.onclick = () => {
      this.onclick_acquire();
    };
    this.PB_stop.onclick = () => {
      this.onclick_stop();
    };

    this.setHidden(this.PB_stop, true);
  }

  register_handler_NUM_FFT() {
    this.TB_NUM_FFT.addEventListener("blur", () => {
      this.onchange_NUM_FFT();
    });

    this.TB_NUM_FFT.addEventListener("keydown", (evt) => {
      if (evt.key === "Enter") {
        this.onchange_NUM_FFT();
      }
    });
  }

  register_handler_t_acquire() {
    this.TB_acquireTime.addEventListener("blur", () => {
      this.onchange_t_acquire();
    });

    this.TB_acquireTime.addEventListener("keydown", (evt) => {
      if (evt.key === "Enter") {
        this.onchange_t_acquire();
      }
    });
  }

  onchange_t_acquire() {
    this.t_acquire = parseInt(this.TB_acquireTime.value);
    if (isNaN(this.t_acquire)) {
      this.t_acquire = 120;
    }
    this.TB_acquireTime.value = this.t_acquire.toString();
  }

  onchange_NUM_FFT() {
    this.NUM_FFT = parseInt(this.TB_NUM_FFT.value);
    if (isNaN(this.NUM_FFT)) {
      this.NUM_FFT = 1024;
    }

    if (this.NUM_FFT < 16) {
      this.NUM_FFT = 16;
    }

    if (!this.isPowerOfTwo(this.NUM_FFT)) {
      this.NUM_FFT = this.nextPowerOfTwo(this.NUM_FFT);
    }
    this.TB_NUM_FFT.value = this.NUM_FFT.toString();
  }

  isPowerOfTwo(n) {
    return Number.isInteger(n) && n > 0 && (n & (n - 1)) === 0;
  }
  nextPowerOfTwo(n) {
    const power = Math.log2(n);
    const upper = 2 ** Math.ceil(power);
    const lower = 2 ** Math.floor(power);
    const mid = (upper + lower) / 2;

    if (n >= mid) {
      return upper;
    } else {
      return lower;
    }
  }

  received_started() {
    this.TB_NUM_FFT.disabled = true;
    this.TB_acquireTime.disabled = true;

    // UI logic
    this.setHidden(this.PB_view_start, true);
    this.setHidden(this.PB_acquire_start, true);
    this.setHidden(this.PB_stop, false);
  }

  received_finished() {
    this.TB_NUM_FFT.disabled = false;
    this.TB_acquireTime.disabled = false;

    // UI logic
    this.setHidden(this.PB_view_start, false);
    this.setHidden(this.PB_acquire_start, false);
    this.setHidden(this.PB_stop, true);
    this.set_progress_mode("finished");
  }

  async start_acquisition(NUM_FFT, t, labels) {
    await window.api_acquire.startAcquire({
      NUM_FFT: NUM_FFT,
      t: t,
      labels: labels,
    });
  }

  async onclick_view() {
    this.dispatchEvent(new Event("start-view"));
    this.set_progress_mode("live");
  }

  async onclick_acquire() {
    if (this.t_acquire > 0) {
      this.set_progress_mode("acquire");
      this.dispatchEvent(new Event("start-acquire"));
    }
  }

  async onclick_stop() {
    await window.api_acquire.stopAcquire();
  }

  update_progress(progress) {
    // this.progress.value = progress.toString();
    // const percent = (value / max) * 100;
    if (this.mode === "acquire") {
      this.progress.style.width = `${progress}%`;
    }
  }

  set_progress_mode(mode) {
    this.mode = mode;
    if (mode === "acquire") {
      this.progress.classList.remove("animate-flicker");
      this.progress.style.width = "0%"; // reset or update as needed
      // example update later: progress.style.width = "50%";
    } else if (mode === "live") {
      this.progress.style.width = "100%"; // or any fixed value to show full bar
      this.progress.classList.add("animate-flicker");
    } else if (mode === "finished") {
      this.progress.classList.remove("animate-flicker");
      this.progress.style.width = "100%"; // reset or update as needed
    }
  }
}
