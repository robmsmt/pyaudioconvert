# pyaudioconvert

Simple utility to convert audio from one form to another (via sox). We will use Sox until we find a fast and efficient way to convert reliably in python


## Requirements
 0. At least py3x
 1. Have sox installed 
 
 
## Install
 0. `pip install pyaudioconvert`
 


## Example Usage

### Converting Single WAVs
```python
#let's start with a 24bit 48kz audio wav 2 channel wav
>>> soxi example_24bit_48k_2ch.wav 

Input File     : 'example_24bit_48k_2ch.wav'
Channels       : 2
Sample Rate    : 48000
Precision      : 24-bit
Sample Encoding: 24-bit Signed Integer PCM

#we prefer 16-bit 16kz mono for our systems, let's use python
>>> import pyaudioconvert as pac
>>> pac.convert_wav_to_16bit_mono('example_24bit_48k_2ch.wav', 'example_16bit_16k_1ch.wav')
Out[2]: 'example_16bit_16k_1ch.wav'

#let's check the new file...
>>> soxi example_16bit_16k_1ch.wav 

Input File     : 'example_16bit_16k_1ch.wav'
Channels       : 1
Sample Rate    : 16000
Precision      : 16-bit
Sample Encoding: 16-bit Signed Integer PCM

```


### Converting Directory of WAVs

Maybe I have a whole folder of WAVS that need converting... this will create a _16k.wav version.

```python
(py36) rob:~/example_test$ ls
1.wav  2.wav  3.wav  4.wav

>>>python

Python 3.6.5 (default, Apr  1 2018, 05:46:30) 
Type 'copyright', 'credits' or 'license' for more information
IPython 6.4.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import pyaudioconvert as pac

In [2]: pac.convert_all_wavs_in_folder()
2.wav
2_16k.wav
3.wav
3_16k.wav
1.wav
1_16k.wav
4.wav
4_16k.wav

(py36) rob:~/example_test$ ls
1_16k.wav  1.wav  2_16k.wav  2.wav  3_16k.wav  3.wav  4_16k.wav  4.wav


```
