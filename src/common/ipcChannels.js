import { createIpcChannels } from "instrument-ui/common/ipcChannels.js";
import APP_IPC_CHANNELS from "./appIpcChannels.js";

const CH = createIpcChannels(APP_IPC_CHANNELS);

export default CH;
