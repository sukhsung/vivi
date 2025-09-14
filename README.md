# Vivi - Geophone ADC Controller

**Vivi** is an [Electron](https://www.electronjs.org)-based GUI for controlling ADC-8 and ADC-8x boards developed by Winfield Hill and Alan Stern at the Rowland Institute at Harvard.

---

## Installation Instructions

### Windows
1. Download the `.exe` file from the [Releases](https://github.com/sukhsung/vivi/releases) page.
2. Run `vivi-x.x.x.Setup.exe`. The software wil auto-install this might take a couple minutes.
3. By default a shortcut should be auto-generated, but if you can't find it, the software is installed to `C:\Users\user-name\AppData\Local\vivi\vivi.exe`. 

### macOS
1. Download the `.dmg` file from the [Releases](https://github.com/sukhsung/vivi/releases) page.
2. Copy `Vivi.app` into the `/Applications` folder.
3. Open Terminal and run:

   ```
   xattr -cr /Applications/vivi.app
   ```
   This removes macOS Gatekeeper's quarantine since the app is not code-signed.

4. Launch Vivi.app.

### Linux (.deb, .rpm):
rpm installer has not been tested at all.
1. Download and install .deb file from the [Releases](https://github.com/sukhsung/vivi/releases) page.
2. Launch the software from terminal
   ```
   vivi
   ```
3. If the device can't be connected with `Error: Permission denied, cannot open /dev/your-device`, run following command to grant read/write access to your serial port
   ```
   sudo chmod 666 /dev/your-device
   ```
   This is temporary fix and might be resetted after a reboot. Alternatively, you can add the current user to `dialout` user group
   ```
   sudo usermod -a -G dialout $USER
   ```


## Development and Build Instruction
1. Download and install [`Node.js`](https://nodejs.org)
2. Clone this repository and navigate into it
   ```
   git clone https://github.com/sukhsung/vivi.git
   cd vivi
   ```
3. Install dependenceis
   ```
   npm install
   ```
5. Run the app in development mode:
   ```
   npm start
   ```
6. Build platform-specific distributables locally
   ```
   npm run make
   ```
7. Optional: Compile Tailwind CSS during developments (required for UI styling):
   ```
   npx @tailwindcss/cli -i ./src/renderer/css/input.css -o ./src/renderer/css/output.css --watch
   ```

## Acknowledgements

Special thanks to:

- Winfield Hill – Hardware design and assembly (Rowland Institute at Harvard)
- Alan Stern – Firmware and initial data acquisition code (Rowland Institute at Harvard)
- William Millsaps and Miti Shah – Testing support (Hovden Lab, University of Michigan)
