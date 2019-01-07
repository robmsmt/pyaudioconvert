name = "pyaudioconvert"

import os, subprocess, tempfile, uuid
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


def _get_mono_audio_only(audio_file_path):
    rate, data = scipy.io.wavfile.read(audio_file_path)
    try:
        nchannels = data.shape[1]
    except IndexError:
        nchannels = 1

    if nchannels != 1:
        return data[:, 0]

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


def convert_wav_to_16bit_mono(old_wav_path, new_wav_path, sr=16000, overwrite_existing=True):

    temp_file_is_old_wav = False

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
        temp_file_is_old_wav = True
        full_temp_path = old_wav_path

    # 2. get mono Audio only
    mono_audio = _get_mono_audio_only(full_temp_path)

    # 3. Save audio (16k or set SR)
    if os.path.isfile(new_wav_path):

        if overwrite_existing:
            scipy.io.wavfile.write(new_wav_path, sr, mono_audio)
        else:
            raise(OverwriteFileError)

    else:
        scipy.io.wavfile.write(new_wav_path, sr, mono_audio)

    # cleanup temp
    if temp_file_is_old_wav == False:
        os.remove(full_temp_path)

    return new_wav_path
