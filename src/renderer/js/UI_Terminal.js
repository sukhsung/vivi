import { UI_Manager } from "./UI_Manager.js";

export { UI_TerminalManager };

class UI_TerminalManager extends UI_Manager {
  constructor() {
    super();
  }

  initialize() {
    this.cacheDOM({
      PB_terminal: "terminal",
    });

    this.PB_terminal.onclick = () => this.open_terminal();
  }

  open_terminal() {
    window.api.openTerminal();
  }
}
