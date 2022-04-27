# importing libraries
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import filetype
import tempfile


def detect_format(file):
    """A function that detects the format of a file"""
    file_type = filetype.guess(file)
    return file_type.extension


def to_wav(file):
    """A function to convert mp3 files to wav files"""

    # files
    source = file
    destination = file.replace(".mp3", ".wav")

    # convert wav to mp3
    sound = AudioSegment.from_mp3(source)
    sound.export(destination, format="wav")

    return destination


# create a speech recognition object
r = sr.Recognizer()


# a function that splits the audio file into chunks
# and applies speech recognition


def get_large_audio_transcription(path, set_silence_len=500, set_silence_threshold=14):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """

    # Check type of the audio file and change it to wav if mp3
    audio_type = detect_format(path)
    print(audio_type)

    if audio_type == "mp3":
        path = to_wav(path)

    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)
    # split audio sound where silence is 700 milliseconds or more and get chunks
    chunks = split_on_silence(sound,
                              # experiment with this value for your target audio file
                              min_silence_len=set_silence_len,
                              # adjust this per requirement
                              silence_thresh=sound.dBFS - set_silence_threshold,
                              # keep the silence for 1 second, adjustable as well
                              keep_silence=500,
                              )

    whole_text = ""
    # create a temporary folder to handle the chunks, will be deleted upon completion of the task
    with tempfile.TemporaryDirectory() as tempDict:
        # process each chunk
        for i, audio_chunk in enumerate(chunks, start=1):
            # export audio chunk and save it in
            # the `folder_name` directory.
            chunk_filename = os.path.join(tempDict, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            # recognize the chunk
            with sr.AudioFile(chunk_filename) as source:
                audio_listened = r.record(source)
                # try converting it to text
                try:
                    text = r.recognize_google(audio_listened)
                except sr.UnknownValueError as e:
                    print("Error:", str(e))
                else:
                    text = f"{text.capitalize()}. "
                    print(chunk_filename, ":", text)
                    whole_text += text
    # return the text for all chunks detected
    return whole_text


def main():
    path = "/Users/johancuda/PycharmProjects/pythonProject/testLargeAudioFiles/OSR_us_000_0010_8k.wav"
    print("\nFull text:", get_large_audio_transcription(path))


if __name__ == "__main__":
    main()
