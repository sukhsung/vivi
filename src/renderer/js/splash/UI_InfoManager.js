import { import_template } from "../util/import_template.js";
import { UI_SplashManager } from "./UI_SplashManager.js";

export { UI_InfoManager };

class UI_InfoManager extends UI_SplashManager {
  constructor() {
    super(
      "./templates/template_info.html",
      "info-overlay",
      "PB_info",
      "PB_info_close",
      true,
      false,
    );
  }

  async _create_page() {
    this.version = await window.api_app.get_version();
    document.getElementById("info_version").textContent = `v${this.version}`;
  }
}
