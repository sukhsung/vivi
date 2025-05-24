# Vivi - Geophone ADC Controller

`Vivi` is [electron](https://www.electronjs.org) based GUI for controlling ADC-8 and ADC-8x boards developed by Winfield Hill and Alan Stern at the Rowland Institute at Harvard.

## Windows:

## MacOS:
1. Download `.dmg` file and copy `Vivi.app` into `/Applications` folder.
2. Run `xattr -cr /Applications/Vivi.app` in terminal to bypass codesigning
3. Run `Vivi.app`

## Linux:

## Development and Build  Instruction
1. Download and install `Node.js`
2. Clone this repository and navigate to repository in terminal
   a. `git clone git@github.com:sukhsung/vivi.git`
   b. `cd vivi`
3. Run `npm install` to install dependencies
   a. Tailwind needs to compile `output.css`
   b. Run `npx @tailwindcss/cli -i ./src/renderer/css/input.css -o ./src/renderer/css/output.css --watch`
5. Run `npm start` to start the application without buidling
6. RUn `npm run make` to build the application locally


Special thanks and Acknowledgements to 
1. Winfield Hill (Rowland Institute at Harvard) for hardware design and aseembly.
2. Alan Stern (Rowland Institute at Harvard) for firmware design and initial data collection code designs.
3. William Millsaps and Miti Shah (Hovden Lab, U of Michigan for testing codes.
