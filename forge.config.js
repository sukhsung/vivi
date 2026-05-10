import pluginFuses from "@electron-forge/plugin-fuses";
import fuses from "@electron/fuses";

const { FusesPlugin } = pluginFuses;
const { FuseV1Options, FuseVersion } = fuses;

const config = {
  packagerConfig: {
    name: "vivi",
    executableName: "vivi", // File name of the actual binary
    asar: true,
    icon: "./src/assets/app-icon",
    osxSign: false, //{}, // object must exist even if empty
  },
  rebuildConfig: {
    force: true,
  },
  makers: [
    { name: "@electron-forge/maker-dmg", platforms: ["darwin"] },

    {
      name: "@electron-forge/maker-squirrel",
      platforms: ["win32"],
      config: {
        name: "vivi",
        setupExe: "vivi-${version}-setup.exe",
      },
    },

    {
      name: "@rabbitholesyndrome/electron-forge-maker-portable",
      platforms: ["win32"],
      config: {
        productName: "vivi",
        artifactName: "vivi-${version}-portable.exe",
      },
    },

    {
      name: "@electron-forge/maker-deb",
      executableName: "vivi",
      config: {
        options: {
          name: "vivi",
          maintainer: "https://shsung.com",
          icon: "./src/assets/app-icon.png",
        },
      },
    },

    {
      name: "@electron-forge/maker-rpm",
      executableName: "vivi",
      config: {
        options: {
          name: "vivi",
          maintainer: "https://shsung.com",
          icon: "./src/assets/app-icon.png",
        },
      },
    },
  ],
  plugins: [
    new FusesPlugin({
      version: FuseVersion.V1,
      [FuseV1Options.RunAsNode]: false,
      [FuseV1Options.EnableCookieEncryption]: true,
      [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
      [FuseV1Options.EnableNodeCliInspectArguments]: false,
      [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
    }),
  ],
};

export default config;
