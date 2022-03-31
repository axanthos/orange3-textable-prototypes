from pydub import AudioSegment

src = "Clean and Dance - An Jone.mp3"

dst = "test.wav"

sound = AudioSegment.from_mp3(src)
sound.export(dst, format="wav")