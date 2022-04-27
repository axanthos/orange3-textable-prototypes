import speech_recognition as speechRecognition
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
from _textable.widgets.TextableUtils import (
	OWTextableBaseWidget, ProgressBar,
)
from Orange.widgets import widget, gui, settings
from Orange.widgets.settings import Setting
from Orange.widgets.utils.widgetpreview import WidgetPreview

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from LTTL.Segmentation import Segmentation


path = "/Users/rebeccakneubuehler/Desktop/UNIL/deuxiemePartie/ish/informatiqueTextuelle/p22_progTexte2/projet/orange3-textable-prototypes/orangecontrib/textable_prototypes/widgets/testAudioFiles_7min.wav"

class OWTextableAudioFiles(OWTextableBaseWidget):
	"""Orange widget that converts audio files into segmented text"""

	name = "Audio Files"
	description = "Convert audio into segmented text"
	icon = "icons/audioFiles.png"
	priority = 10

	# Inputs and ouputs
	inputs = []
	outputs = [("Transcripted data", Segmentation)]

	want_main_area = False
	resizing_enabled = True
	
	#def sendData(self):
	#	if (
	#		(self.displayAdvancedSettings and not self.files) or
	#		not (self.file or self.displayAdvancedSettings)
	#		):
	#		self.infoBox.setText(u'Please select input file.', 'warning')
	#		self.send('Text data', None, self) 
	#		# Appeler la fonction get_large_audio_transcirption	
	#		self.get_large_audio_transcription(path)
	#		return
	
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
		# Initiating a progress bar
		progressBar = ProgressBar(
			self,
			iterations = len(chunks)
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
			# Advance the progress bar
			progressBar.advance()	
		# Delete the directory 
		if os.path.exists(folder_name):
			if len(os.listdir(folder_name)) == 0:
				os.rmdir(folder_name)
			else:
				print("The folder is not empty.")
		else:
			print("The folder does not exist.")	
		# End the progress bar
		progressBar.finish()	
		# Returns the texte for all chunks detected
		return whole_text


if __name__ == '__main__':
    WidgetPreview(OWTextableAudioFiles).run()

