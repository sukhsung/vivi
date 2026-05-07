import { import_template } from "./util/import_template.js";
import { UI_Manager } from "./UI_Manager.js";

export { UI_KeyboardManager };

const CLEARANCE = 12;

class UI_KeyboardManager extends UI_Manager {
  constructor() {
    super();
    this._keyboard_on = true;
    // Numpad state
    this._numpad_input = null;
    this._buffer = "";
    // QWERTY state
    this._qwerty_input = null;
    this._symbols_on = false;

  }

  async create_keyboards(){
    const template_numpad = await import_template("./templates/template_keyboard_numeric.html");
    document.body.appendChild(template_numpad.content.cloneNode(true));
    

    const template_qwerty = await import_template("./templates/template_keyboard_qwerty.html");
    document.body.appendChild(template_qwerty.content.cloneNode(true));

  }

  async initialize() {
    await this.create_keyboards();

    this.cacheDOM({
      numpad: "numpad",
      qwerty: "qwerty",
      PB_keyboard: "PB_keyboard",
      PB_numpad_close: "PB_numpad_close",
      PB_qwerty_close: "PB_qwerty_close",
      qwerty_letters: "qwerty-letters",
      qwerty_symbols: "qwerty-symbols",
      qwerty_layer_toggle: "qwerty-layer-toggle",
      numpad_buffer_value: "numpad_buffer_value",
      qwerty_buffer_value: "qwerty_buffer_value",
    });

    this.PB_keyboard.addEventListener("click", () => this._toggle());
    this._init_numpad();
    this._init_qwerty();

    document.addEventListener("mousedown", (e) => {
      if (
        !this.numpad.classList.contains("hidden") &&
        !this.numpad.contains(e.target) &&
        e.target !== this._numpad_input
      ) {
        this._close_numpad();
      }
      if (
        !this.qwerty.classList.contains("hidden") &&
        !this.qwerty.contains(e.target) &&
        e.target !== this._qwerty_input
      ) {
        this._close_qwerty();
      }
    });

    document.addEventListener("focusin", (e) => {
      if (!this._keyboard_on) return;
      if (e.target.matches("input[type=number]")) {
        this._close_qwerty();
        this._open_numpad(e.target);
      } else if (
        e.target.matches(
          "input:not([type=number]):not([type=checkbox]):not([type=radio]):not([type=range]):not([type=file]), textarea",
        )
      ) {
        this._close_numpad();
        this._open_qwerty(e.target);
      }
    });
  }

  // ── Toggle ──────────────────────────────────────────────────

  _toggle() {
    this._keyboard_on = !this._keyboard_on;
    this.PB_keyboard.classList.toggle("keyboard-off", !this._keyboard_on);
    if (!this._keyboard_on) {
      this._close_numpad();
      this._close_qwerty();
    }
    this.emit("keyboard_toggle", { keyboard_on: this._keyboard_on });
  }

  // ── Shared positioning ──────────────────────────────────────

  _position(el, input) {
    el.style.top = "-9999px";
    el.style.left = "-9999px";
    el.classList.remove("hidden");

    const h = el.offsetHeight;
    const w = el.offsetWidth;
    const rect = input.getBoundingClientRect();

    const top =
      window.innerHeight - rect.bottom >= h + CLEARANCE
        ? rect.bottom + CLEARANCE
        : rect.top - h - CLEARANCE;
    const left = Math.max(8, Math.min(rect.left, window.innerWidth - w - 8));

    el.style.top = `${top}px`;
    el.style.left = `${left}px`;
  }

  _show_buffer() {
    this._render_buffer();
  }

  _hide_buffer() {
    this.numpad_buffer_value.textContent = "";
    this.qwerty_buffer_value.textContent = "";
  }

  _render_buffer() {
    const value = this._buffer || "\u00A0";
    this.numpad_buffer_value.textContent = value;
    this.qwerty_buffer_value.textContent = value;
  }

  _commit_buffer(input, value = this._buffer) {
    if (!input) return;
    input.value = "";
    input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
  }

  // ── Numpad ──────────────────────────────────────────────────

  _init_numpad() {

    this.PB_numpad_close.addEventListener("click", () => this._close_numpad());

    this.numpad.querySelectorAll("[data-key]").forEach((btn) => {
      btn.addEventListener("mousedown", (e) => {
        e.preventDefault();
        this._press_digit(btn.dataset.key);
      });
    });

    this.numpad
      .querySelector("[data-action='backspace']")
      .addEventListener("mousedown", (e) => {
        e.preventDefault();
        this._numpad_backspace();
      });
    this.numpad
      .querySelector("[data-action='negate']")
      .addEventListener("mousedown", (e) => {
        e.preventDefault();
        this._press_negate();
      });
    this.numpad
      .querySelector("[data-action='enter']")
      .addEventListener("mousedown", (e) => {
        e.preventDefault();
        this._numpad_enter();
      });
  }

  _open_numpad(input) {
    this._numpad_input = input;
    this._buffer = "";
    this._show_buffer();
    this._position(this.numpad, input);
  }

  _close_numpad() {
    this.numpad.classList.add("hidden");
    this._numpad_input = null;
    this._buffer = "";
    this._hide_buffer();
  }

  _press_digit(key) {
    if (key === "." && this._buffer.includes(".")) return;
    if (key === "." && this._buffer === "") this._buffer = "0";
    if (key === "." && this._buffer === "-") this._buffer = "-0";
    this._buffer += key;
    this._render_buffer();
  }

  _numpad_backspace() {
    this._buffer = this._buffer.slice(0, -1);
    this._render_buffer();
  }

  _press_negate() {
    this._buffer = this._buffer.startsWith("-")
      ? this._buffer.slice(1)
      : "-" + this._buffer;
    this._render_buffer();
  }

  _numpad_enter() {
    if (this._numpad_input) {
      const val = parseFloat(this._buffer);
      this._commit_buffer(this._numpad_input, isNaN(val) ? "" : String(val));
      this._numpad_input.blur();
    }
    this._close_numpad();
  }

  // ── QWERTY ──────────────────────────────────────────────────

  _init_qwerty() {
    this.PB_qwerty_close.addEventListener("click", () => this._close_qwerty());

    this.qwerty.querySelectorAll("[data-lower]").forEach((btn) => {
      btn.addEventListener("mousedown", (e) => {
        e.preventDefault();
        const shifted = this.qwerty.classList.contains("shifted");
        const char =
          shifted && btn.dataset.upper ? btn.dataset.upper : btn.dataset.lower;
        this._insert_char(char);
        if (shifted) this.qwerty.classList.remove("shifted");
      });
    });

    this.qwerty.querySelectorAll("[data-action]").forEach((btn) => {
      btn.addEventListener("mousedown", (e) => {
        e.preventDefault();
        switch (btn.dataset.action) {
          case "shift":
            this.qwerty.classList.toggle("shifted");
            break;
          case "backspace":
            this._qwerty_backspace();
            break;
          case "enter":
            this._qwerty_enter();
            break;
          case "layer-toggle":
            this._set_symbols(!this._symbols_on);
            break;
        }
      });
    });
  }

  _open_qwerty(input) {
    this._qwerty_input = input;
    this._buffer = "";
    this._set_symbols(false);
    this.qwerty.classList.remove("shifted");
    this._show_buffer();
    this._position(this.qwerty, input);
  }

  _close_qwerty() {
    this.qwerty.classList.add("hidden");
    this._qwerty_input = null;
    this._buffer = "";
    this._hide_buffer();
  }

  _set_symbols(on) {
    this._symbols_on = on;
    if (on) this.qwerty.classList.remove("shifted");
    this.qwerty_letters.classList.toggle("hidden", on);
    this.qwerty_symbols.classList.toggle("hidden", !on);
    this.qwerty_layer_toggle.textContent = on ? "ABC" : "?123";
  }

  _insert_char(char) {
    if (!this._qwerty_input) return;
    this._buffer += char;
    this._render_buffer();
  }

  _qwerty_backspace() {
    if (!this._qwerty_input) return;
    this._buffer = this._buffer.slice(0, -1);
    this._render_buffer();
  }

  _qwerty_enter() {
    if (this._qwerty_input) {
      this._commit_buffer(this._qwerty_input);
      this._qwerty_input.blur();
    }
    this._close_qwerty();
  }
}
