import { import_template } from "./util/import_template.js";
export { UI_Manager };

class UI_Manager extends EventTarget {
  constructor(div_main_id, verbose = false) {
    super();
    this.verbose = verbose;
    this.div_main_id = div_main_id;
  }

  async _initialize() {
    return;
  }

  async initialize(data) {
    // Load DOM
    this.cacheDOM({
      div_main: this.div_main_id,
    });
    await this._initialize(data);
  }

  received_settings(data) {
    this.print("RECEIVED SETTING");
    this.print(data);
    this._received_settings(data);
  }

  _received_settings(data) {
    return;
  }

  cacheDOM(selectors) {
    for (const [key, id] of Object.entries(selectors)) {
      this[key] = document.getElementById(id);
    }
  }

  CB_remove_all_options(cb) {
    while (cb.options.length > 0) cb.remove(0);
  }

  CB_add_options(cb, list) {
    list.forEach((item) => {
      const option = document.createElement("option");
      option.text = option.value = item;
      cb.add(option);
    });
  }

  setHidden(element, bool) {
    if (bool) {
      element.classList.add("hidden");
    } else {
      element.classList.remove("hidden");
    }
  }

  print(message, header = this.constructor.name) {
    if (this.verbose) {
      console.log(`${header}: ${message}`);
    }
  }

  emit(name, payload) {
    this.dispatchEvent(
      new CustomEvent(name, {
        detail: payload,
      }),
    );
  }

  async import_template( path ) {
    return await import_template(path)
  }
}

