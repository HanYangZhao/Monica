# -*- coding: utf-8-*-
"""
    The Mic class handles all interactions with the microphone and speaker.
"""
import logging
import tempfile
import wave
import audioop
import pyaudio
import alteration
import jasperpath
import socket

port = 3443
ip = "192.168.2.204"
audioParams = (1,2,8000,0,'NONE','not compressed')
class Mic:

    speechRec = None
    speechRec_persona = None

    def __init__(self, speaker, passive_stt_engine, active_stt_engine):
        """
        Initiates the pocketsphinx instance.

        Arguments:
        speaker -- handles platform-independent audio output
        passive_stt_engine -- performs STT while Jasper is in passive listen
                              mode
        acive_stt_engine -- performs STT while Jasper is in active listen mode
        """
        self._logger = logging.getLogger(__name__)
        self.speaker = speaker
        self.passive_stt_engine = passive_stt_engine
        self.active_stt_engine = active_stt_engine
        self._logger.info("Initializing PyAudio. ALSA/Jack error messages " +
                          "that pop up during this process are normal and " +
                          "can usually be safely ignored.")
        self._audio = pyaudio.PyAudio()
        self._logger.info("Initialization of PyAudio completed.")

    def __del__(self):
        self._audio.terminate()

    def getScore(self, data):
        rms = audioop.rms(data, 2)
        score = rms / 3
        return score

    def fetchThreshold(self):

        # TODO: Consolidate variables from the next three functions
        THRESHOLD_MULTIPLIER = 1.8
        RATE = 8000
        CHUNK = 512

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1
        #stream = self._audio.open(format=pyaudio.paInt16,
        #                          channels=1,
        #                          rate=RATE,
        #                          input=True,
        #                          frames_per_buffer=CHUNK)
        #Create a socket connection for connecting to the server:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        print "connected to socket"

        

        # stores the audio data
        frames = []

        # stores the lastN score values
        lastN = [i for i in range(20)]

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, RATE / CHUNK * THRESHOLD_TIME):

            data = client_socket.recv(512)
            tempWave = wave.open("temp.wav", 'wb')
            tempWave.setparams(audioParams)
            tempWave.writeframes(data);
            tempWave.close()
            tempWave = wave.open("temp.wav", 'rb')
            data = tempWave.readframes(512)
            tempWave.close()
            frames.append(data)

            # save this data point as a score
            lastN.pop(0)
            lastN.append(self.getScore(data))
            average = sum(lastN) / len(lastN)

        client_socket.close()
        #stream.stop_stream()
        #stream.close()
        # this will be the benchmark to cause a disturbance over!
        THRESHOLD = average * THRESHOLD_MULTIPLIER

        return THRESHOLD

    def passiveListen(self, PERSONA):
        """
        Listens for PERSONA in everyday sound. Times out after LISTEN_TIME, so
        needs to be restarted.
        """

        THRESHOLD_MULTIPLIER = 1.8
        RATE = 8000
        CHUNK = 512

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1

        # number of seconds to listen before forcing restart
        LISTEN_TIME = 10

        # prepare recording stream
        #stream = self._audio.open(format=pyaudio.paInt16,
        #                          channels=1,
        #                          rate=RATE,
        #                          input=True,
        #                          frames_per_buffer=CHUNK)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        print "connected to socket"

        # stores the audio data
        frames = []

        # stores the lastN score values
        lastN = [i for i in range(30)]

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, RATE / CHUNK * THRESHOLD_TIME):

            data = client_socket.recv(512)
            tempWave = wave.open("temp1.wav", 'wb')
            tempWave.setparams(audioParams)
            tempWave.writeframes(data);
            tempWave.close()
            tempWave = wave.open("temp1.wav", 'rb')
            data = tempWave.readframes(512)
            tempWave.close()
            frames.append(data)

            # save this data point as a score
            lastN.pop(0)
            lastN.append(self.getScore(data))
            average = sum(lastN) / len(lastN)

        # this will be the benchmark to cause a disturbance over!
        THRESHOLD = average * THRESHOLD_MULTIPLIER

        # save some memory for sound data
        frames = []

        # flag raised when sound disturbance detected
        didDetect = False

        # start passively listening for disturbance above threshold
        for i in range(0, RATE / CHUNK * LISTEN_TIME):

            data = client_socket.recv(512)
            tempWave = wave.open("temp1.wav", 'wb')
            tempWave.setparams(audioParams)
            tempWave.writeframes(data);
            tempWave.close()
            tempWave = wave.open("temp1.wav", 'rb')
            data = tempWave.readframes(512)
            tempWave.close()
            frames.append(data)

            score = self.getScore(data)

            if score > THRESHOLD:
                didDetect = True
                break

        # no use continuing if no flag raised
        if not didDetect:
            print "No disturbance detected"
            client_socket.close()
            #stream.stop_stream()
            #stream.close()
            return (None, None)

        # cutoff any recording before this disturbance was detected
        frames = frames[-20:]

        # otherwise, let's keep recording for few seconds and save the file
        DELAY_MULTIPLIER = 1
        for i in range(0, RATE / CHUNK * DELAY_MULTIPLIER):
            data = client_socket.recv(512)
            tempWave = wave.open("temp1.wav", 'wb')
            tempWave.setparams(audioParams)
            tempWave.writeframes(data);
            tempWave.close()
            tempWave = wave.open("temp1.wav", 'rb')
            data = tempWave.readframes(512)
            tempWave.close()
            frames.append(data)


        # save the audio data
        client_socket.close()

        with tempfile.NamedTemporaryFile(mode='w+b') as f:
            wav_fp = wave.open(f, 'wb')
            wav_fp.setnchannels(1)
            wav_fp.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wav_fp.setframerate(RATE)
            wav_fp.writeframes(''.join(frames))
            wav_fp.close()
            f.seek(0)
            # check if PERSONA was said
            transcribed = self.passive_stt_engine.transcribe(f)

        if any(PERSONA in phrase for phrase in transcribed):
            return (THRESHOLD, PERSONA)

        return (False, transcribed)

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False):
        """
            Records until a second of silence or times out after 12 seconds

            Returns the first matching string or None
        """

        options = self.activeListenToAllOptions(THRESHOLD, LISTEN, MUSIC)
        if options:
            return options[0]

    def activeListenToAllOptions(self, THRESHOLD=None, LISTEN=True,
                                 MUSIC=False):
        """
            Records until a second of silence or times out after 12 seconds

            Returns a list of the matching options or None
        """

        RATE = 8000
        CHUNK = 512
        LISTEN_TIME = 12

        # check if no threshold provided
        if THRESHOLD is None:
            THRESHOLD = self.fetchThreshold()

        self.speaker.play(jasperpath.data('audio', 'beep_hi.wav'))

        # prepare recording stream
        #stream = self._audio.open(format=pyaudio.paInt16,
        #                          channels=1,
        #                          rate=RATE,
        #                          input=True,
        #                          frames_per_buffer=CHUNK)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        print "connected to socket"
        

        frames = []
        # increasing the range # results in longer pause after command
        # generation
        lastN = [THRESHOLD * 1.2 for i in range(30)]

        for i in range(0, RATE / CHUNK * LISTEN_TIME):

            data = client_socket.recv(512)
            tempWave = wave.open("temp1.wav", 'wb')
            tempWave.setparams(audioParams)
            tempWave.writeframes(data);
            tempWave.close()
            tempWave = wave.open("temp1.wav", 'rb')
            data = tempWave.readframes(512)
            tempWave.close()
            frames.append(data)

            score = self.getScore(data)
            lastN.pop(0)
            lastN.append(score)

            average = sum(lastN) / float(len(lastN))

            # TODO: 0.8 should not be a MAGIC NUMBER!
            if average < THRESHOLD * 0.8:
                break

        self.speaker.play(jasperpath.data('audio', 'beep_lo.wav'))

        # save the audio data
        #stream.stop_stream()
        #stream.close()
        client_socket.close()
        with tempfile.SpooledTemporaryFile(mode='w+b') as f:
            wav_fp = wave.open(f, 'wb')
            wav_fp.setnchannels(1)
            wav_fp.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wav_fp.setframerate(RATE)
            wav_fp.writeframes(''.join(frames))
            wav_fp.close()
            f.seek(0)
            return self.active_stt_engine.transcribe(f)

    def say(self, phrase,
            OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):
        # alter phrase before speaking
        phrase = alteration.clean(phrase)
        self.speaker.say(phrase)
