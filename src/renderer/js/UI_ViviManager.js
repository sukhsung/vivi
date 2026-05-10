import { UI_Manager } from "../../../node_modules/instrument-ui/src/renderer/js/UI_Manager.js";

export class UI_ViviManager extends UI_Manager {
  constructor(verbose = false) {
    super(verbose);
  }

  initialize() {
    // Load DOM
    this.cacheDOM({
      div_busy_left: "busy_left",
      div_connection: "connection",
      div_control: "control",
      div_busy_left_status: "busy_left_status",

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

  async received_started(mode) {
    this.toggle_panel_left("busy");
    if (mode == "live") {
      this.set_busy_left_msg("Live Acquisition in Progress");
    } else if (mode == "acquire") {
      this.set_busy_left_msg("Timed Acquisition in Progress");
    }
  }

  async received_delay() {
    this.toggle_panel_left("busy");
    this.set_busy_left_msg("Pre-acqusition Delay in Progress");
  }

  async received_finished() {
    this.toggle_panel_left("control");
  }

  set_busy_left_msg(msg) {
    this.div_busy_left_status.innerHTML = msg;
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
