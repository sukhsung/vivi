# Vivi - Geophone ADC Controller

**Vivi** is an [Electron](https://www.electronjs.org)-based GUI for controlling ADC-8 and ADC-8x boards developed by Winfield Hill and Alan Stern at the Rowland Institute at Harvard.

---

## 📦 Installation Instructions

### 🪟 Windows
_TODO: Add instructions here (e.g., run `.exe`, install path, etc.)_

### 🍎 macOS
1. Download the `.dmg` file from the [Releases](https://github.com/sukhsung/vivi/releases) page.
2. Copy `Vivi.app` into the `/Applications` folder.
3. Open Terminal and run:

   ```
   xattr -cr /Applications/Vivi.app
   ```
   This removes macOS Gatekeeper's quarantine since the app is not code-signed.

4. Launch Vivi.app.

### Linux:
_TODO: Add instructions here (e.g., run `.exe`, install path, etc.)_

## 🛠 Development and Build  Instruction
1. Download and install [`Node.js`](https://nodejs.org)
2. Clone this repository and navigate into it
   ```
   git clone git@github.com:sukhsung/vivi.git
   cd vivi
   ```
3. Install dependenceis
   ```npm install`
4. Compile Tailwind CSS (required for UI styling):
   ```
   npx @tailwindcss/cli -i ./src/renderer/css/input.css -o ./src/renderer/css/output.css --watch
   ```
5. Run the app in development mode:
   ```
   npm start
   ```
6. Build platform-specific distributables locally
   ```
   npm run make
   ```

## 🙏 Acknowledgements

Special thanks to:

Winfield Hill – Hardware design and assembly (Rowland Institute at Harvard)
Alan Stern – Firmware and initial data acquisition code (Rowland Institute at Harvard)
William Millsaps and Miti Shah – Testing support (Hovden Lab, University of Michigan)
