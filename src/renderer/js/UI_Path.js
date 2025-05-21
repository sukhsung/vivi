import {UI_Manager} from './UI_Manager.js'
export { UI_PathManager };

class UI_PathManager extends UI_Manager {
  constructor() {
    super()
  }

  async initialize() {
    this.cacheDOM({
      PB_browse: "PB_browse",
      PB_open: "PB_open",
      TB_path: "TB_path",
      TB_log: "TB_log",
    });

    this.PB_browse.onclick = () => {
      this.onclick_browse();
    };

    this.PB_open.onclick = () => {
      this.onclick_open();
    };
    this.TB_path.value = await window.log_api.getCurrentPath() || "No Path Set";
  }

  async onclick_browse() {
    this.path = await window.log_api.selectPath();
    if (this.path) {
      this.TB_path.value = this.path;
    }
  }

  async onclick_open() {
    await window.log_api.openPath();
  }

  received_started(file_name) {
    this.PB_browse.disabled = true;
    this.TB_log.innerHTML = `Log Started: ${file_name}.csv`;
  }

  received_finished(file_name) {
    this.PB_browse.disabled = false;
    this.TB_log.innerHTML = `Log Finished: ${file_name}.csv`;
  }

  received_error() {
    this.TB_log.innerHTML = `Something Wrong`;
  }

}
