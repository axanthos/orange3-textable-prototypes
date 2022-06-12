.. meta::
   :description: Orange3 Textable Prototypes documentation, Audio File
                 widget
   :keywords: Orange3, Textable, Prototypes, documentation, Audio, File,
              widget

.. _Audio File:

Audio File
=============

.. image:: figures/audioFile_widget.png

Transcribe an audio file into text and segment it depending on volume parameters. 


Author
------

* Gavin Vinasi
* Johan Cuda
* Rebecca Kneubuehler


Signals
-------

Input : None

Outputs :

* ``Text data``

    A segmentation of the transcripted audio.

Description
-----------

This widget is designed to import one audio file, wether it is an mp3 file or a wav file, and to transcribe it into a single segmentation, or multiple segments depending on volumes parameters, in Orange Canvas. 
The user can transcript any audio file, and the output is a segmentation. Each segment has one annotation with the key *title*. 


Basic interface
~~~~~~~~~

In this basic interface (see :ref:"figure 1 <audioFile_fig1>" below), the **Audio File** widget simply lets the user import an audio file and transcript it into a segmentation. The user must also pick the corresponding language. 

.. _audioFile_fig1:

.. figure:: figures/audioFile_fig1.png
    :align: center
    :scale: 50 %
    :alt: Basic interface of the audio File widget

    Figure 1: **Audio file** widget (basic interface).

The **File path** section lets the user choose the path of the audio file he/she wants to transcribe. 

The **Input language** section lets the user choose the language of the corresponding audio file. The default value is french. 

The **Send** button lets the user send the desired output into a segmentation. The **Send automatically** checkbox disables the button and the widget attempt to <utomatically emit a segmentation at every modification of its interface. 

The **Advanced settings** lets the user add different settings to sharpen the desired segmentation and extends the basic interface to the advanced interface. 


Advanced interface
~~~~~~~~~~~~~~~~~~

The advanced version of **Audio file**  (see :ref:"figure 2 
<audioFile_fig2>" below) lets the user refine the settings of the desired segmentation by modifying volumes parameters. 

.. _audioFile_fig2:

.. figure:: figures/audioFile_fig2.png
    :align: center
    :alt: Advanced interface of the Audio file widget
    
    Figure 2: **Audio file** widget (advanced interface).
    

The **Maximum volume (in dBFS)** lets the user pick the maximum level of volume that will be significant to make a segment. 

The **Minimum duration (in milliseconds)** lets the user pick the minimum duration during which the **Maximum volume** needs to last. Those two parameters combined, the user can refine how the segmentation is being segmented.  

The **Segment the audio file with the parameters** checkbox allows the user to get segments depending on those precise parameters. 

Installation
------------

Install ffmpeg
~~~~~~~~~~~~~~

Mac OS: `Install ffmpeg <https://superuser.com/questions/624561/install-ffmpeg-on-os-x>`_ (we recommend using homebrew)

Windows : `Install ffmpeg Windows <https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/>`_

Linux/Ubuntu : `Install ffmpeg <https://www.tecmint.com/install-ffmpeg-in-linux/>`_


Messages
--------

Information
~~~~~~~~~~~

*Successfully transcripted*
    This confirms that the widget has operated properly and that the segmentation has been sent to ouput, in the case of no advanced settings chosen. 

*<n> segments sent to output (<m> characters)*
    This confirms that the widget has operated properly and that the segments have been sent to ouput, in the case of when the user wants to segment depending on the advanced settings. 


Warnings
~~~~~~~~

*Settings were changed, please click "Send" when ready* 
    Settings have changed but the **Send automatically** checkbox
    has not been selected, so the user is prompted to click the **Send**
    button (or equivalently check the box) in order for computation and data
    emission to proceed.

*You must use mp3 or wav audio files.* 
    Input file was not in mp3 or wav format, the user must try another file.




Errors
~~~~~~

*Please select input file*
    The user want to start the process of the transcription without selecting the audio file. 

*You seem to have overuseed the built-in API key, refer to the documentation for further informations.*
    The built-in API key is limited to certain amount of requests per day, and as long as Google keeps the service running of course. If you want to avoid this problem, you can setup an account to use the official Google Cloud Speech API following `these instructions <https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst>`_. (Check the recognizer_instance.recognize_google_cloud section)
    
Note
~~~~

There are at the moment no error messages regarding problems with ffmpeg installation. It is to the user's responsibility to install it using (or not) one of the tutorials provided in this document.
