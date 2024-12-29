# tpenc

Multi-thread multi-pass true peak MP3 encoder

 
## Dependencies

* freac; 
Free cross platform audio encoding tool, needed for the multi-threaded LAME MP3 encoding. Has GUI, but only using the CLI executable. https://freac.org
* afclip; 
Apple's clipping detection tool, available for free as a part of Apple's "Mastered for iTunes" suite. https://www.apple.com/itunes/mastered-for-itunes/"
* ffmpeg; 
For macOS, install with homebrew; brew install ffmpeg
* ffprobe; 
 For macOS, install with homebrew; brew install ffprobe


## Config
Edit config.json to change the default input encoding. By default the script needs 24-bits 48Khz .wav files

"threads" are currently set to 32 by default. On my current system this works 120% better than single threaded. On my old Intel Xeon system 15 worked optimal.

## Workflow
1. Run script ./tpenc.py 
2. Drag & drop .wav file
3. Choose bitrate and regular or true peak encoding
4. Let it run
5. MP3 file appears in the same folder as the original WAV file

The true peak encoding of an MP3 works by first doing a single encoding from the original WAV to MP3 then analyzing the results. If nothing clips, process is complete.

If the file does have (inter inter sample or true peak) clipping, a temporary copy of the WAV file is made from the original. This copy is then reduced in gain by ffmpeg with the dB's clipping from afclip's analysis. Then another MP3 encoding is done from that temporary have > another analysis > still clipping > new copy from the original WAV is made and reduced even further. This way, there is no encoding-upon-encoding and no degradation - and it leaves the original untouched.

## Caveats
Due to the way macOS handles terminal input (drag & drop) differently for bash than zsh, it took a bit of finicky code to get the input right.

## Todo
* Add ffmpeg to the required apps in the config and script
	
