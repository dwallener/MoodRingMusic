import streamlit as st
import numpy as np
import io
import mido
from scipy.io import wavfile

# --- Sine Wave Audio Generation ---
def generate_sine_wave(frequency, duration_sec, bpm, sample_rate=44100):
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    beats_per_sec = bpm / 60
    modulation = (np.sin(2 * np.pi * beats_per_sec * t) > 0).astype(float)
    audio_wave = 0.5 * np.sin(2 * np.pi * frequency * t) * modulation
    return (audio_wave * 32767).astype(np.int16)  # 16-bit PCM

# --- Generate Audio Bytes ---
def generate_audio_clip(bpm, duration_sec=4, frequency=440):
    audio = generate_sine_wave(frequency, duration_sec, bpm)
    buffer = io.BytesIO()
    wavfile.write(buffer, 44100, audio)
    buffer.seek(0)
    return buffer

# --- Generate Simple MIDI File ---
def generate_midi_clip(bpm, duration_sec=4):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))

    ticks_per_beat = mid.ticks_per_beat
    note_duration = int(ticks_per_beat / 2)  # Eighth notes
    num_notes = int((bpm / 60) * duration_sec * 2)

    for _ in range(num_notes):
        track.append(mido.Message('note_on', note=60, velocity=64, time=0))
        track.append(mido.Message('note_off', note=60, velocity=64, time=note_duration))

    buffer = io.BytesIO()
    mid.save(file=buffer)
    buffer.seek(0)
    return buffer

# --- Streamlit App ---
st.title("🎵 Mood Ring Music - Live Prototype")

if "current_hour" not in st.session_state:
    st.session_state.current_hour = 7  # Start at 07:00h

bpm_mapping = {
    "Lowest": 80,
    "Low": 90,
    "Rising": 110,
    "Moderate": 120,
    "High": 140,
    "Decreasing": 100
}

diurnal_cycle = [
    "Low", "Low", "Lowest", "Lowest", "Lowest", "Low",      
    "Rising", "Rising",                                    
    "High", "High", "High", "High",                         
    "Moderate", "Moderate",                                 
    "High", "High", "High", "Moderate", "Moderate", "Moderate",  
    "Decreasing", "Decreasing", "Low", "Low"                
]

current_hour = st.session_state.current_hour
current_energy = diurnal_cycle[current_hour]
current_bpm = bpm_mapping[current_energy]

st.subheader(f"🕒 Current Time: {current_hour:02d}:00")
st.write(f"**Diurnal Energy:** {current_energy}")
st.write(f"**BPM:** {current_bpm}")

audio_buffer = generate_audio_clip(current_bpm)
st.audio(audio_buffer, format="audio/wav")

midi_buffer = generate_midi_clip(current_bpm)
st.download_button("📥 Download MIDI", data=midi_buffer, file_name="mood_ring_music.mid", mime="audio/midi")

if st.button("➡️ Advance Hour"):
    st.session_state.current_hour = (current_hour + 1) % 24
    st.experimental_rerun()