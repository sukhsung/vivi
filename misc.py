
# noise-density.py
"""Program to compute noise spectral density in nV / sqrt(Hz) for ADC-8 data."""
def calc_noise_density( infile, outfile, nchans=4, rate=1024, bool_plot=True, bool_text =False):
    import math
    import numpy as np

    NUM_DFT = 1024


    if bool_text:
        data = np.loadtxt(infile)
        nsamples = data.shape[0]
        if len(data.shape) == 1:
            data = np.reshape(data, (nsamples, 1))
        if nchans != data.shape[1]:
            nchans = data.shape[1]
            print("Wrong number of channels specified; using", nchans)
    else:
        data = np.fromfile(infile, dtype=np.dtype("<f4"))
        nsamples = data.shape[0] // nchans
        data = np.reshape(data, (nsamples, nchans))

        total_power = np.zeros((NUM_DFT // 2 + 1, nchans))
        navg = 0
    for i in range(0, nsamples - NUM_DFT, NUM_DFT):
        f = np.fft.rfft(data[i:, :], NUM_DFT, axis=0)		# Noise spectrum
        f = np.square(np.real(f)) + np.square(np.imag(f))	# Power spectrum
        total_power += f
        navg += 1
    f = np.sqrt(total_power / navg)

    # Normalize and convert to nV / sqrt(Hz)
    f *= 1.0e9 / math.sqrt(NUM_DFT * 0.5 * rate)

    # Round off to a reasonable number of decimals
    f = f.round(6)

    xscale = rate / NUM_DFT

    if outfile != "/":
        outfile = open(outfile, "w")
    for i, row in enumerate(f):
        print(i * xscale, *row, file=outfile)
    outfile.close()

    if bool_plot:
        import matplotlib.pyplot as plt

        x = np.linspace(0., rate * 0.5, NUM_DFT // 2 + 1)
        fig, ax = plt.subplots(figsize=(7,3))
        ax.set_xlim(x[0], x[-1])
        ymax = np.max(f[1:, :])
        ax.set_ylim(1e-1, 2. * ymax)
        ax.grid(True, "both")
        colors = ['r','b','tomato','deepskyblue']
        for i in range(f.shape[1]):
                ax.semilogy(x, f[:,i], c=colors[i],label=f"Channel {i+1}")
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("nV/sqrt(Hz)")
        fig.tight_layout()
        ax.legend()
        plt.show()



timestamp = time.strftime( "%H%M", time.localtime())
datestamp = time.strftime( "%Y%m%d", time.localtime())
dirdefault = "results/"+datestamp

parser = argparse.ArgumentParser(description=
        "Continuous data transfer from an ADC-8 board, version " + VERSION)
parser.add_argument("-d", "--dev",
        help="The ADC-8 board's serial-port device name")
parser.add_argument("-w", "--wait", type=int, default=0,
        help="Optional time to wait in seconds")
parser.add_argument("-o", "--out", default= dirdefault,
        help="Output data Directory (- for stdout and text format)")
parser.add_argument("-t", "--time", type=int, nargs="?", default=120,
        help="Time in seconds to transfer data (omit for indefinite)")
parser.add_argument("-g", "--gain", type=int, default=128,
        help="Gain for ADC, Default = 128")
parser.add_argument("-s", "--sampling", type=int, default=400,
        help="Sampling Freqeuncy in Hz, Default = 400Hz")


args = parser.parse_args()
if args.time < 0:
    args.time = 0


if args.dev is None:
    portlist = get_port_list()
    if len(portlist) == 0:
        print("No USB serial port devices available")
        sys.exit(1)
    elif len(portlist) == 1:
        args.dev = portlist[0].device
    else:
        print("Available USB serial ports:")
        for p in portlist:
            print("    ", p.device)
        args.dev = input("Enter a port name: ")
        print()

board = Board(args.dev)
print("Connected to ADC-8 board:", args.dev)
print("           Serial number:", board.serial_number)

# Set Gain and Sampling Rate
board.write(b"g 0 "+args.gain+"\n")
a = board.read(1500)
print(a.decode())
board.write(b"s "+args.sampling+"\n")
a = board.read(1500)
print(a.decode())
# Read the current settings
board.write(b"c\n")
a = board.read(1500)
print(a.decode())

if not os.path.exists( args.out):
    os.makedirs( args.out)

fpath  = os.path.join( args.out, timestamp)
outpath = fpath+".out"
outfile = open(fpath, "wb")

if args.wait > 0:
    print("Waiting for", args.wait, "seconds...")
    time.sleep(args.wait)

# Start the continuous read
print("Transferring data, press Enter to stop...")
board.write(f"b{args.time}\n".encode())
board.dev.timeout = 6
board.read_until(b"+")		# Skip initial text

sig = b""
h = board.read(HDR_LEN)
if len(h) == HDR_LEN:
    hdr = struct.unpack(f"<4sHBB {2 * NUM_CHANNELS}B", h)
    sig = hdr[0]		# The signature
if sig != b"ADC8":
    print("Invalid header received, transfer aborted")
    board.write(b"\n")
    sys.exit()

chans = hdr[4:]			# The ADC channel entries
num = 0
gains = [chans[2 * i] for i in range(NUM_CHANNELS)]
bipolar = [chans[2 * i + 1] & BIPOLAR for i in range(NUM_CHANNELS)]
for g in gains:
    if g > 0:
        num += 1
if num == 0:
    print("Header shows no active ADCs, transfer aborted")
    board.write(b"\n")
    sys.exit()

blocksize = num * 3
volts = [0.] * num
out_structure = struct.Struct(f"<{num}f")
out_buffer = bytearray(num * NUM_CHANNELS)

def convert_values(block):
    """Convert the 24-bit values in block to floating-point numbers
    and store them in the global variable volts."""

    j = v = 0
    for i, g in enumerate(gains):
        if g == 0:
            continue
        x = (block[j] + (block[j+1] << 8) + (block[j+2] << 16)) * SCALE_24
        if bipolar[i]:
            x = 2. * x - 1.
        volts[v] = round(x * VREF / g, 9)
        j += 3
        v += 1

total_blocks = 0
warned = False

threading.Thread(target=poll_stdin, daemon=True).start()

# Receive and store the data
while True:
    n = board.read(1)		# Read the buffer's length byte
    if len(n) == 0:
        print("Timeout")
        break
    n = n[0]
    if n == 0:
        print("End of data")
        break

    d = board.read(n)		# Read the buffer contents
    if len(d) < n:
        print("Short data buffer received")
        break
    if n % blocksize != 0:
        if not warned:
            print("Warning: Invalid buffer length", n)
            warned = True
        n -= n % blocksize


    for i in range(0, n, blocksize):
        # Convert the block data to floats and write them out
        convert_values(d[i:i + blocksize])

        out_structure.pack_into(out_buffer, 0, *volts)
        outfile.write(out_buffer)

    total_blocks += n // blocksize
    if stdin_available.is_set():
        print("Termination requested")
        break

board.write(b"\n")
print("Transfer ended")
print(total_blocks, "blocks received")

board.dev.timeout = 0.01
board.read(1000)		# Flush any extra output
outfile.close()
board.close()

calc_noise_density( fpath, outpath)