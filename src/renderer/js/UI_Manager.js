export { UI_Manager };

class UI_Manager extends EventTarget {
  constructor() {
    super();
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
}
