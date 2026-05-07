import path from "node:path";
import os from "node:os";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_CONFIG_PATH = path.join(
  __dirname,
  "..",
  "assets",
  "vivi.config.default",
);

const CONFIG_DIR = path.join(os.homedir(), "vivi");
const CONFIG_PATH = path.join(CONFIG_DIR, "vivi.config");

function load_default_config() {
  return JSON.parse(fs.readFileSync(DEFAULT_CONFIG_PATH, "utf-8"));
}

function load_config() {
  if (!fs.existsSync(CONFIG_PATH)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
    fs.copyFileSync(DEFAULT_CONFIG_PATH, CONFIG_PATH);
    return load_default_config();
  }
  try {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, "utf-8"));
  } catch {
    return load_default_config();
  }
}

export const config = load_config();
