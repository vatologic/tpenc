#!/opt/homebrew/anaconda3/bin/python3
import json, os, sys, subprocess, re, time, math, shutil
from pathlib import Path

config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.json")


multipass = True


# Load config & global def
# --------------------------------------------------------------------------------

# Throw fatal error and exit
def ferr(message):
    sys.exit("[FATAL ERROR]\n" + str(message))

# Load config
try:
    with open(config_file, 'r') as file:
        config = json.load(file)
except:
    ferr(str(config_file) + " not found!")

# Message for verbose mode only
def ver(message):
    if (config["verbose"] == True):
        print("✔ " + str(message))

def ts():
    return int(time.time_ns() / 1000000)

# Preflight checks
# --------------------------------------------------------------------------------

def preflight(file_in):

    # Check if all the required 3rd party apps are present
    for app in config["lib"]:
        if (os.path.isfile(config["lib"][app]["cmd"]) != True):
            ferr(str(app) + " not found at " + config["lib"][app]["cmd"] + "\n" + str(config["lib"][app]["info"]))
    ver("Apps")

    # Check if the incoming file is available
    if (os.path.isfile(file_in) != True):
        return ("File not found!")
    else:
        ver("Input file")

    # Check if the incoming file is a wav file
    if (Path(file_in).suffix != '.wav'):
        return ("Not a .wav file!")
    else:
        ver("File extenion")

    # Check if the output path is writeable
    path_out = os.path.dirname(os.path.abspath(file_in))
    if (os.access(path_out, os.W_OK) != True):
        return ("Output path is not writeable: " + path_out)
    else:
        ver("Output path")

    ## ffprobe checks
    try:
        ffprobe_raw = subprocess.run([config['lib']['ffprobe']['cmd'] + ' -v error -hide_banner -print_format json -show_format -show_streams ' + '"' + str(file_in) + '"'], shell=True, capture_output=True, text=True)
        if (ffprobe_raw.returncode != 0):
            ferr("ffprobe returned error")
        else:
            ver("ffprobe")
        try:
            ffprobe = json.loads(ffprobe_raw.stdout)
        except:
            ferr("ffprobe returned invalid JSON")
    except:
        ferr("ffprobe runtime error")

    # Check codec
    if (ffprobe['streams'][0]['codec_name'] != config["wav"]["codec_name"]):
        return ("Input file codec is {} instead of {}".format(ffprobe['streams'][0]['codec_name'], config["wav"]["codec_name"]))
    else:
        ver("Codec")

    # Check sample rate
    if (ffprobe['streams'][0]['sample_rate'] != str(config["wav"]["sample_rate"])):
        return ("Input file sample rate is {} instead of {}".format(ffprobe['streams'][0]['sample_rate'], config["wav"]["sample_rate"]))
    else:
        ver("Sample rate")

    # All good!
    return True



# afclip
# --------------------------------------------------------------------------------

def afclip(file_in):
    # run afclip
    try:
        afclip_raw = subprocess.run([config['lib']['afclip']['cmd'] + ' -x ' + '"' + str(file_in) + '"'], shell=True, capture_output=True, text=True)
        if (afclip_raw.returncode != 0):
            ferr("afclip returned error")
        else:
            afclip_data = afclip_raw.stdout
            #ver("afclip")
    except:
        ferr("afclip runtime error")

    # parse data
    clipping = False
    clipping_db = 0.0

    if (afclip_data.find("no samples clipped") != -1):
        #ver("no clipping detected")
        return clipping_db
    else:
        try:
            regex = r"(?:(?P<seconds>\d+\.\d+)\s+(?P<sample>\d+\.\d+)\s+(?P<chan>\d+)\s+(?P<value>(-)?\d+.\d+)\s+(?P<decibels>\d+\.\d+))"
            matches = re.finditer(regex, afclip_data, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                current_db = float(match.group(6))
                if ( current_db > clipping_db):
                    clipping_db = current_db
            #ver("Clipping {} dB".format(clipping_db))
            return clipping_db
        except:
            ferr("Parsing afclip data went wrong")


# freac
# --------------------------------------------------------------------------------

def freac(file_in, file_out, bitrate):
    freac_cmd = '"{}" --quiet --encoder={} -m {} -b {} -q {} --superfast --threads={} -o "{}" "{}"'.format(
        config['lib']['freac']['cmd'],
        config['mp3']['encoder'],
        config['mp3']['method'],
        str(bitrate),
        config['mp3']['quality'],
        config['mp3']['threads'],
        file_out,
        file_in)
    try:
        timestamp_start = ts()
        freac_raw = subprocess.run([freac_cmd], shell=True, capture_output=True, text=True)
        if (freac_raw.returncode != 0):
            ferr("freac returned error")
        else:
            pass
            #ver("freac encoded in {} sec".format(math.floor((ts()-timestamp_start)/100)/10))
    except:
        ferr("Freac aborted")

# filename output

def file_out(file_in, serial = False):
    extension = 'mp3'
    if (serial == False):
        return Path(file_in).with_suffix('.'+extension)
    else:
        return Path(file_in).with_suffix('.{}.{}'.format(str(serial),extension))

def intermediate(file_in, remove = False):

    temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp', os.path.basename(file_in) )

    if (os.path.isfile(temp_file) != True):
        ver("\tIntermediate file created")
        shutil.copy(file_in,temp_file)
    if (remove == True and os.path.isfile(temp_file) == True):
        os.remove(temp_file)
        ver("Intermediate file removed")
    return temp_file

def reduceGain(file_in, db = 0.0):
    # Use Temp file
    temp_file = intermediate(file_in)
    ffmpeg_command = '{} -y -i "{}" -filter:a "volume={}dB" -acodec {} -ar {} "{}"'.format(config["lib"]["ffmpeg"]["cmd"], file_in, (db*-1), config["wav"]["codec_name"], config["wav"]["sample_rate"],temp_file)
    subprocess.run([ffmpeg_command], shell=True, capture_output=True, text=True)
    #ver("Gain recuded by {} dB".format(str(db)))
                    

def ask_user_file():
    #ver("menu override")
    #return "/Users/Shared/Temp/Bucket/mmpte/Vato Gonzalez ft. Scrufizzer - Boom Riddim [Style & Flex] (v6).wav"
    return input(">  ").strip().replace("\\","")

def ask_bitrate():
    return input(">  ")

def header():
    os.system('clear')
    print("{} v{} | multi-thread multi-pass true-peak MP3 encoder | 2025 {}".format(config["app"], config["version"], config["vendor"]))
    print("-----------------------------------------------------------------------------------\n")

# Runtime
# --------------------------------------------------------------------------------

header()

print("Drag and drop 2448 .WAV file")
file_in = ask_user_file()
pf = preflight(file_in)
if (pf != True):
    print(pf)
    file_in = ask_user_file()

header()
print("Regular encoding:")
print("[1] 96  kb/sec (Preview)")
print("[2] 128 kb/sec (Streaming)")
print("[3] 320 kb/sec (High quality)")
print("")
print("True-peak encoding:")
print("[4] 96  kb/sec (Preview)")
print("[5] 128 kb/sec (Streaming)")
print("[6] 320 kb/sec (High quality)")
print("")
print("[q] Quit\n")
print("")

options = ["1","2","3", "4", "5", "6", "q"]
bitrate_choice = ask_bitrate()
while (bitrate_choice not in options):
    bitrate_choice = ask_bitrate()

if (bitrate_choice == "q"):
    sys.exit()
else:
    match bitrate_choice:
        case "1" | "4":
            bitrate = 96
        case "2" | "5":
            bitrate = 128
        case "3" | "6":
            bitrate = 320

if bitrate_choice in ["1","2","3"]:
    multipass = False

header()
print("Processing")

# Convert
freac(file_in, file_out(file_in), bitrate)

# Multipass
passes = 1

if (multipass == True):
    # Analyze; first pass
    clipping = afclip(file_out(file_in))

    # Set increasing var
    gain_reduction = 0.0

    # Loop until clipping is finally 0.0
    if (clipping != 0.0):
        ver("Clipping detected, running multipass")
        intermediate(file_in)
    while (clipping != 0.0):
        passes += 1
        # Add previous clipping to total gain reduction
        gain_reduction = gain_reduction + clipping
        ver("\tReducing gain by: {} dB".format(math.ceil(gain_reduction*1000)/1000))

        # reduce gain on basis of original
        reduceGain(file_in, gain_reduction)

        # encode again, this time from the intermediate - not the original
        freac(intermediate(file_in), file_out(file_in), bitrate)

        # Check for clipping again
        clipping = afclip(file_out(file_in))
    
# Cleanup
intermediate(file_in, True)

# Final message
header()
if (multipass == True):
    print("MP3 True-Peak encoded at {} kb/sec in {} pass(es) at -{} dB.\n\n".format(bitrate, passes, math.ceil(gain_reduction*100)/100))
else:
    print("MP3 encoded at {} kb/sec.\n\n".format(bitrate))