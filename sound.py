import pyaudio, wave
import numpy as np
import matplotlib.pyplot as plt
from . import log, util

CHUNK = 1024

class Sound(object):

    def __init__(self):
        self.signal = None
        self.bits = None
        self.rate = None
        self.samples = None        
        self.path = None
        self.wf = None

    def load(self, path):
        log.info("Sound.load")
        log.info("--> loading from %s" % path)
        self.path = path
        self.wf = wave.open(self.path, 'rb')
        self.bits = self.wf.getsampwidth() * 8
        if self.bits != 16:
            raise NotImplementedError
        self.signal = np.fromstring(self.wf.readframes(-1), 'Int16') # signed 16-bit samples
        self.wf.rewind()
        self.rate = self.wf.getframerate()
        self.samples = len(self.signal)
        self.duration = self.samples / self.rate        
        log.info("--> bits %s" % self.bits)
        log.info("--> rate %s" % self.rate)
        log.info("--> samples %s" % self.samples)
        log.info("--> duration %fs" % self.duration)
        return self

    def reload(self):
        return self.load(self.path)

    def record(self, duration, path=None, rate=11025):
        log.info("SoundSignal.record")
        if path is None:
            path = "%s.wav" % util.dt(util.timestamp(), tz="America/New_York").strftime("%y%m%d-%H%M%S")    # needs to be local timezone
        log.info("--> recording to %s" % path)
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=rate,
                        input=True,
                        frames_per_buffer=CHUNK)
        log.info("* Recording...")
        frames = []
        for i in range(0, int(rate / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        log.info("--> done")
        stream.stop_stream()
        stream.close()
        p.terminate()

        # write file
        wf = wave.open(path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        self.load(path)
        return self


    def play(self):
        log.info("SoundSignal.play")
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(self.wf.getsampwidth()),
                        channels=self.wf.getnchannels(),
                        rate=self.wf.getframerate(),
                        output=True)
        data = self.wf.readframes(CHUNK)
        while data != '':
            stream.write(data)
            data = self.wf.readframes(CHUNK)
        stream.stop_stream()
        stream.close()
        p.terminate()
        self.wf.rewind()

    def plot(self):

        # 50-5000 hz
        # need a window @ 25 hz, 0.04 seconds
        # 0.04 / (1 / sampling_rate)
        # at 11025, that's 441
        # so at that sampling_rate and higher, 512 is good        
        block_size = 512

        # set up plot
        plt.rcParams['toolbar'] = 'None'
        plt.figure(frameon=True, figsize=(15, 8), dpi=80, facecolor=(1., 1., 1.), edgecolor=(1., 1., 1.))
        
        # show amplitude domain
        plt.subplot(2, 1, 1, axisbg=(1., 1., 1.))
        plt.plot(self.signal, color=(1., 0., 0.))        
        plt.axis([0.0, self.duration * self.rate, 0-(2**self.bits/2), 2**self.bits/2]) # go to bitrate
        # plt.xlabel("Samples")
        # plt.ylabel("Amplitude")
        
        # show spectrogram
        plt.subplot(2, 1, 2, axisbg='#ffffff')
        # plt.subplot(1, 1, 1, axisbg='#ffffff')
        block_overlap = block_size / 2 # power of two, default is 128
        spectrum, freqs, ts, image = plt.specgram(self.signal, NFFT=block_size, Fs=self.rate, noverlap=block_overlap)
        plt.axis([0.0, self.duration, 0, self.rate/2])
        # plt.xlabel("Seconds")
        # plt.ylabel("Frequency")

        # plt.suptitle(self.path)
        fig = plt.gcf()
        fig.canvas.set_window_title(self.path)        

        log.info("--> freq bins %s" % len(freqs))
        log.info("--> time columns %s" % len(ts))

        plt.show()

        # print("spectrum", spectrum) # freq rows of time columns. 
        # print()
        # print(freqs)
        # print()
        # print(ts)


def write_audio(signal, filename, rate=44100):
    from scipy.io import wavfile
    wavfile.write(filename, rate, signal)


