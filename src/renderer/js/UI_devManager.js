import { UI_Manager } from "./UI_Manager.js";
export { UI_devManager };

class UI_devManager extends UI_Manager {
  constructor() {
    super();
  }

  initialize() {
    // Load DOM
    this.cacheDOM({
      div_busy_left: "busy_left",
      div_connection: "connection",
      div_control: "control",

      div_busy_right: "busy_right",
      div_viewer: "viewer",
    });

    // this.toggle_panel_left("busy");
    // this.toggle_panel_left("control");
    this.toggle_panel_left("connection");
    this.toggle_panel_right("busy");
  }
  async received_connected() {
    this.toggle_panel_left("control");
    this.toggle_panel_right("viewer");
  }

  async received_disconnected() {
    this.toggle_panel_left("connection");
    this.toggle_panel_right("busy");
  }

  async received_started() {
    this.toggle_panel_left("busy");
  }

  async received_finished() {
    this.toggle_panel_left("control");
  }

  toggle_panel_left(page) {
    if (page === "connection") {
      this.setHidden(this.div_connection, false);
      this.setHidden(this.div_control, true);
      this.div_busy_left.classList.add("opacity-0", "pointer-events-none");
    } else if (page === "control") {
      this.setHidden(this.div_connection, true);
      this.setHidden(this.div_control, false);
      this.div_busy_left.classList.add("opacity-0", "pointer-events-none");
    } else if (page === "busy") {
      this.div_busy_left.classList.remove("opacity-0", "pointer-events-none");
    }
  }

  toggle_panel_right(page) {
    if (page === "viewer") {
      this.div_busy_right.classList.add("opacity-0", "pointer-events-none");
    } else if (page === "busy") {
      this.div_busy_right.classList.remove("opacity-0", "pointer-events-none");
    }
  }
}
