import subprocess
import time

def play(audio_file_path):
    subprocess.call(["aplay", "-q", audio_file_path])

play("/root/pinball/mysound.wav")
time.sleep(1)
print("butt")
play("/root/pinball/mysound.wav")
