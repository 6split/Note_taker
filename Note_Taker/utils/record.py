# import required libraries
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv

def record(time, file_name="recording.wav"):
    # Sampling frequency
    freq = 44100

    # Recording duration
    duration = time

    # Start recorder with the given values 
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq), 
                    samplerate=freq, channels=2)

    # Record audio for the given number of seconds
    sd.wait()

    # This will convert the NumPy array to an audio
    # file with the given sampling frequency
    write(file_name, freq, recording)

    # Convert the NumPy array to audio file
    wv.write(file_name, recording, freq, sampwidth=2)