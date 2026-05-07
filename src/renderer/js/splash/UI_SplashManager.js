import { import_template } from "../util/import_template.js";

export { UI_SplashManager };

class UI_SplashManager {
  constructor(
    path_template,
    div_splash,
    PB_open,
    PB_close,
    close_on_outside = true,
    visible_on_boot = false,
  ) {
    this.path_template = path_template;
    this.div_splash = div_splash;
    this.close_on_outside = close_on_outside;
    this.visible_on_boot = visible_on_boot;
    this.PB_open = PB_open;
    this.PB_close = PB_close;
  }

  async initialize(config) {
    await this.create_page();
    await this._initialize(config);
  }

  async _initialize() {
    return;
  }

  async create_page() {
    const template = await import_template(this.path_template);
    document.body.appendChild(template.content.cloneNode(true));
    this.div_splash = document.getElementById(this.div_splash);

    await this._create_page();

    this.PB_open = document.getElementById(this.PB_open);
    this.PB_close = document.getElementById(this.PB_close);

    this.PB_open.addEventListener("click", () => this.show());
    this.PB_close.addEventListener("click", () => this.hide());

    if (this.close_on_outside) {
      this.div_splash.addEventListener("click", (e) => {
        if (e.target === this.div_splash) this.hide();
      });
    }

    if (this.visible_on_boot) {
      this.show();
    } else {
      this.hide();
    }
  }

  _create_page() {
    return;
  }

  show() {
    this.div_splash.classList.add("splash-open");
  }

  hide() {
    this.div_splash.classList.remove("splash-open");
  }
}
