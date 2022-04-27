import speech_recognition as speechRecognition
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence


path = "/Users/rebeccakneubuehler/Desktop/UNIL/deuxiemePartie/ish/informatiqueTextuelle/p22_progTexte2/projet/orange3-textable-prototypes/orangecontrib/textable_prototypes/widgets/testAudioFiles_7min.wav"

# A function that applies speech recognition to a large audio file
def get_large_audio_transcription(self, path):
	""" Splitting the large audio file into chunks
	and apply speech recognition on each of these chunks """	
	# Open the file using pydub
	sound = AudioSegment.from_wav(path)
	# Split audio sound where silence is 700 miliseconds or more and get chunks
	chunks = split_on_silence(sound,
		min_silence_len = 500,
		silence_thresh = sound.dBFS-14,
		keep_silence = 500,
	)
	folder_name = "audio-chunks"
	# create a directory to store the audio chunks
	if not os.path.isdir(folder_name):
		os.mkdir(folder_name)
	whole_text = ""
	# process each chunk
	for i, audio_chunk in enumerate(chunks, start = 1):	
		# Export audio chunk and save it in the "folder_name" directory
		chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
		audio_chunk.export(chunk_filename, format = "wav")
		# Recognize the chunk
		with speechRecognition.AudioFile(chunk_filename) as source:
			audio_listened = self.recognition.record(source)
			# Try converting it to text
			try:
				text = self.recognition.recognize_google(audio_listened, language = "fr_FR")
			except speechRecognition.UnknownValueError as e:
				print("Error : ", str(e))
			else:
				text = f"{text.capitalize()}. "
				print(chunk_filename, " : ", text)
				whole_text += text
		# Delete the audio chunks
		if os.path.exists(chunk_filename):
			os.remove(chunk_filename)
		else:
			print("The file does not exist.")
	# Delete the directory 
	if os.path.exists(folder_name):
		if len(os.listdir(folder_name)) == 0:
			os.rmdir(folder_name)
		else:
			print("The folder is not empty.")
	else:
		print("The folder does not exist.")	
	# Returns the texte for all chunks detected
	return whole_text

