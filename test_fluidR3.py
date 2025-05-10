import time
import fluidsynth

# Initialize FluidSynth
sf_path = "soundfonts/FluidR3_GM.sf2"
fs = fluidsynth.Synth()
fs.start()

# Load SoundFont
sfid = fs.sfload(sf_path)
fs.program_select(0, sfid, 0, 0)

# Notes to Test (C3 to C5)
test_notes = [48, 60, 72]  # C3, C4 (Middle C), C5

print("🎹 Starting SoundFont Program Test...")

for program in range(0, 128):
    fs.program_select(0, sfid, 0, program)
    print(f"Program {program}: Playing C3, C4, C5")

    for note in test_notes:
        fs.noteon(0, note, 100)
        time.sleep(0.3)
        fs.noteoff(0, note)

    time.sleep(0.5)  # Pause before next program

print("🎵 Test Complete!")
fs.delete()