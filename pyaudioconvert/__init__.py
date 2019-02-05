name = "pyaudioconvert"

import os, subprocess, tempfile, uuid
from os import listdir
from os.path import isfile, join
import scipy
import scipy.io.wavfile as wav

RUN_ID = str(uuid.uuid4())[:4]

# check that sox is installed
def bool_which(program):

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return True
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return True

    return False


class SoxNotInstalled(Exception):
    pass


class InvalidNonReadableFile(Exception):
    pass


class OverwriteFileError(Exception):
    pass


try:
    assert(bool_which('sox'))
except AssertionError:
    raise SoxNotInstalled()


def _valid_readable_file(file_path):
    # returns false if file does not exist or is not readable (note python can return true/false on a real file)
    if not (os.path.isfile(file_path) and os.access(file_path, os.R_OK)):
        return False
    else:
        # else returns true if file exists and readable
        return True


# def _valid_audiofile(audio_file_path):
#     return _valid_readable_file(audio_file_path)


def _is_24bit_audio(audio_file_path):

    # todo what about non-wavs?

    try:
        _, _ = scipy.io.wavfile.read(audio_file_path)
    except ValueError:
        return True


def _get_mono_audio_only(audio_file_path, selected_channel=0):
    rate, data = scipy.io.wavfile.read(audio_file_path)
    try:
        nchannels = data.shape[1]
    except IndexError:
        nchannels = 1

    if nchannels != 1:
        return data[:, selected_channel]

    return data


def _get_safe_temp_file():

    # todo - how to ensure safe file and no race conditions?
    tempdir = tempfile.gettempdir()
    full_temp_path = os.path.join(tempdir, RUN_ID + str(uuid.uuid4()) + '.wav')

    # check is not already a file
    if os.path.isfile(full_temp_path):
        # unlikely condition but if this happens we can recreate another
        full_temp_path = os.path.join(tempdir, RUN_ID + str(uuid.uuid4()) +'_' + str(uuid.uuid1()) + '.wav')

    return full_temp_path

def _get_audio_sample_rate(wav_file):
    rate, _ = scipy.io.wavfile.read(wav_file)
    return rate

def convert_all_wavs_in_folder(path_location='.', selected_channel=0, sr=16000, overwrite_existing=True):

    '''

    :param path_location: If no path is given it will assume current directory
    :param sr:  SR defaults to 16k
    :param overwrite_existing: Will overwrite existing wavs by default (unless turned off)
    :return:
    '''

    wav_files = [f for f in listdir(path_location) if f.endswith('wav')]
    sr_suffix = str(sr)[0:2]

    for wav in wav_files:
        print(wav)

        new_file_path = wav[:-4] + "ch{}_{}k.wav".format(selected_channel, sr_suffix)

        if os.path.isfile(new_file_path):

            if overwrite_existing:
                print(convert_wav_to_16bit_mono(wav, new_file_path, selected_channel, sr=sr))
            else:
                raise OverwriteFileError

        else:
            print(convert_wav_to_16bit_mono(wav, new_file_path, selected_channel, sr=sr))


def convert_wav_to_16bit_mono(old_wav_path, new_wav_path, selected_channel=0, sr=16000, overwrite_existing=True):

    '''

    :param old_wav_path: The original wav file that needs converting
    :param new_wav_path: The new path or name of the wav to be used
    :param sr: The sample rate (default is 16k)
    :param overwrite_existing: Will overwrite existing wavs by default (unless turned off)
    :return: Returns the name of the new wav on successful creation

    Example usage:
    >>> import pyaudioconvert as pac
    >>> pac.convert_wav_to_16bit_mono('example_24bit_48k_2ch.wav', 'example_16bit_16k_1ch.wav')
    Out[2]: 'example_16bit_16k_1ch.wav'

    '''


    temp_file1_notused = False
    temp_file2_notused = False

    # 0. CHECK - validate audiofile
    try:
        assert(_valid_readable_file(old_wav_path))
    except AssertionError:
        raise InvalidNonReadableFile

    # 1. CHECK - is24bit?
    if _is_24bit_audio(old_wav_path):
        # if 24bit we must convert to 16bit
        # create new safe temp file
        full_temp_path = _get_safe_temp_file()
        # use sox to convert
        subprocess.call(["sox", old_wav_path, '--encoding=signed-integer', '--bits=16', '--type=wav', full_temp_path], stderr=subprocess.STDOUT)

    else:
        # 16bit
        temp_file1_notused = True
        full_temp_path = old_wav_path

    # 2. SET SAMPLE RATE
    if _get_audio_sample_rate(full_temp_path) != sr:
        final_full_temp_path = _get_safe_temp_file()
        subprocess.call(["sox", full_temp_path, '--type=wav', '--rate={}'.format(sr), final_full_temp_path], stderr=subprocess.STDOUT)
    else:
        temp_file2_notused = True
        final_full_temp_path = full_temp_path

    # 3. get mono Audio only & save
    mono_audio = _get_mono_audio_only(final_full_temp_path, selected_channel)

    if os.path.isfile(new_wav_path):
        if overwrite_existing:
            scipy.io.wavfile.write(new_wav_path, sr, mono_audio)
        else:
            raise(OverwriteFileError)
    else:
        scipy.io.wavfile.write(new_wav_path, sr, mono_audio)

    # cleanup temp & finaltemp
    if temp_file1_notused == False:
        os.remove(full_temp_path)

    if temp_file2_notused == False:
        os.remove(final_full_temp_path)

    return new_wav_path
