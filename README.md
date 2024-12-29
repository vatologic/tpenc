# tpenc
Multi-thread multi-pass true peak MP3 encoder

## Dependencies
### python 3.x
### homebrew
The missing package manager for macOS. https://brew.sh
### freac
Free cross platform audio encoding tool, needed for the multi-threaded LAME MP3 encoding. Has GUI, but only using the CLI executable. https://freac.org
### afclip
Apple's clipping detection tool (included in the lastest versions of macOS) but also available for free as a part of Apple Digital Masters "Mastering Tools" https://www.apple.com/apple-music/apple-digital-masters/
### ffmpeg 
For macOS, install from commandline with homebrew
```sh
brew install ffmpeg
```
### ffprobe 
For macOS, install from commandline with homebrew
```sh
brew install ffprobe
```
## config.json
```json
{
    "verbose": false,
    "wav": {
        "codec_name": "pcm_s24le",
        "sample_rate" : 48000
    },
    "mp3": {
        "threads": 32,
        "quality": 1,
        "encoder": "LAME",
        "method": "CBR"
    },
}
```
Edit  to change the default required input encoding. By default the script needs 24-bits 48Khz .wav files in the pcm_s24le codec.

"quality" is a setting of the LAME encoder used to create the MP3. It handles the noise shaping & psycho acoustic algorithms. Range is 0 to 9, where 0 is slow as a snail but has the best results and 9 races through it while doing a sloppy job. It has nothing to do with the bitrate, just how hard the algorythm is working to do the job.

"threads" are currently set to 32 by default. On my current system this works 120% better than single threaded. On my old Intel Xeon system 15 threads worked optimal. I came at this number after testing all threads from 1 to 32 and ran that entire test 32 times. On average 32 worked best for an Apple M2. On other systems I suggest at least 12.

```json
{
    "lib": {
        "ffmpeg": {
            "cmd": "/opt/homebrew/bin/ffmpeg",
            "info": "Install with Homebrew; brew install ffmpeg"
        }
}
```

The cmd parameter is the absolute path to the executeable, in order to find the path you use 'witch' in the terminal
```sh
$ which ffmpeg
/opt/homebrew/bin/ffmpeg
```

## What does it -really- do?

Beyond encoding MP3 files really fast (up to 120% faster in my latest tests) - it does something no other MP3 encoder can do; true peak (inter sample) encoding. Due to the chaotic and lossy nature of MP3 encoding, a WAV file that was mastered at -0.1 dB TPFS will usually end up with inter sample peaks in the encoded MP3 way beyond the -0.1 dB TPFS of the original.

At heart it is basically a while loop where an MP3 is encoded from the original WAV, then check the result for clipping. If so, lower the gain by the highest detected peak above 0 dB TPFS. Then check that result, see if it clips and repeat the process until the MP3 is encoded without peaks.

Instead of re-encoding the same file, every loop a temporary copy of the orignal WAV file is made, lowered by the clipping and then encoded from the temporary file. Every loop a new temporary copy is used, so nothing gets re-encoded and stays clean. The original WAV file is not altered in any way.

Lower bitrates usually take a few more rounds of processing, due to the desctructive nature of MP3 encoding.

## Caveats
The drag & drop input is based on how macOS handles it in zsh; it uses / to escape spaces and special characters.

## FAQ
Will you release a Windows, Linux or MacOS (Intel) version?
> I own neather of those systems, but Python, freac and ffmpeg/ffprobe are availble for all all those platforms.

## Other Questions?
I'm usually found on Instagram, just send me a DM https://instagram.com/vatogonzalez