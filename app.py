import streamlit as st
import pandas as pd
from midi_generator import MidiGenerator
from audio_renderer import AudioRenderer
from markov_melody import MarkovMelodyGenerator
from motif_melody import MotifMelodyGenerator

# ----- Constants -----
allowed_activities = ["work", "sleep", "free", "play", "family"]
diurnal_energy = [
    "Low", "Low", "Lowest", "Lowest", "Lowest", "Low",
    "Rising", "Rising", "High", "High", "High", "High",
    "Moderate", "Moderate", "High", "High", "High", "Moderate",
    "Moderate", "Moderate", "Decreasing", "Decreasing", "Low", "Low"
]
bpm_mapping = {
    "Lowest": 80, "Low": 90, "Rising": 110,
    "Moderate": 120, "High": 140, "Decreasing": 100
}

def time_of_day_symbol(hour):
    if 0 <= hour <= 4 or 21 <= hour <= 23:
        return "🌙"
    elif 5 <= hour <= 6:
        return "🌅"
    elif 7 <= hour <= 18:
        return "☀️"
    elif 19 <= hour <= 20:
        return "🌇"
    return "🌙"

def calculate_alignment(activity, energy):
    if activity == "sleep" and energy in ["Low", "Lowest"]:
        return "✅ Enhance"
    if activity == "work" and energy == "High":
        return "✅ Enhance"
    if activity == "play" and energy in ["Moderate", "High"]:
        return "✅ Enhance"
    if activity == "family" and energy in ["Moderate", "Rising", "Decreasing"]:
        return "✅ Enhance"
    if activity == "free" and energy in ["Moderate", "Decreasing"]:
        return "✅ Enhance"
    if activity == "work" and energy in ["Low", "Lowest", "Decreasing"]:
        return "❌ Oppose"
    if activity == "sleep" and energy in ["High", "Rising"]:
        return "❌ Oppose"
    if activity == "play" and energy in ["Low", "Lowest"]:
        return "❌ Oppose"
    return "⚪ Neutral"

def alignment_modifier(alignment, energy):
    if "Enhance" in alignment:
        return 10 if energy in ["High", "Rising"] else -10
    if "Oppose" in alignment:
        return -10 if energy in ["High", "Rising"] else 10
    return 0

def calculate_bpm(energy, alignment):
    bpm_value = bpm_mapping[energy] + alignment_modifier(alignment, energy)
    return max(min(bpm_value, 160), 80)

# ----- Streamlit UI -----
st.title("🎵 Mood Ring Music")

if "current_hour" not in st.session_state:
    st.session_state.current_hour = 7
if "activity_schedule" not in st.session_state:
    st.session_state.activity_schedule = ["sleep"] * 6 + ["family"] * 2 + ["work"] * 4 + \
        ["free"] * 2 + ["work"] * 3 + ["family"] * 2 + ["play"] * 2 + ["free", "sleep", "sleep"]

current_hour = st.session_state.current_hour
current_energy = diurnal_energy[current_hour]
current_activity = st.session_state.activity_schedule[current_hour]
alignment = calculate_alignment(current_activity, current_energy)
current_bpm = calculate_bpm(current_energy, alignment)

st.subheader(f"🕒 Current Time: {current_hour:02d}:00")
st.write(f"**Activity:** {current_activity}")
st.write(f"**Diurnal Energy:** {current_energy}")
st.write(f"**Alignment:** {alignment}")
st.write(f"**BPM:** {current_bpm}")

col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ Back Hour"):
        st.session_state.current_hour = (current_hour - 1) % 24
        st.rerun()
with col2:
    if st.button("➡️ Advance Hour"):
        st.session_state.current_hour = (current_hour + 1) % 24
        st.rerun()

# ----- Melody Generator Selection -----
melody_method = st.selectbox(
    "🎶 Select Melody Generator",
    options=["Markov", "Motif"],
    index=0
)

melody_length = st.slider("🎼 Melody Length (notes)", min_value=8, max_value=64, value=16, step=4)

# ----- Determine Key and Scale -----
key_root, scale_type = MidiGenerator.KEY_MAPPINGS.get(
    (alignment.replace('✅ ', '').replace('❌ ', '').replace('⚪ ', ''), current_energy),
    ("C", "major")
)

# ----- Generate Melody -----
scale_notes = MidiGenerator.NOTE_MAP
scale_intervals = MidiGenerator.SCALES[scale_type]
scale_midi_notes = [scale_notes[key_root] + i for i in scale_intervals]

if melody_method == "Markov":
    melody_generator = MarkovMelodyGenerator(scale_midi_notes)
else:
    melody_generator = MotifMelodyGenerator(scale_midi_notes)

melody_notes = melody_generator.generate_melody(length=melody_length)

# ----- Audio and MIDI Output -----
audio_renderer = AudioRenderer()
audio_wave = audio_renderer.generate_song_audio(
    bpm=current_bpm,
    key_root=key_root,
    scale_type=scale_type,
    melody_notes=melody_notes,
    duration_sec=30  # Increased from 4 to 30 seconds
)
audio_buffer = audio_renderer.export_wav(audio_wave)
st.audio(audio_buffer, format="audio/wav")

midi_gen = MidiGenerator(bpm=current_bpm, alignment=alignment, energy=current_energy)
midi_gen.generate_song()  # Consider passing melody_notes directly if you want perfect sync
midi_buffer = midi_gen.export()

st.download_button("📥 Download MIDI", data=midi_buffer, file_name=f"hour_{current_hour:02d}.mid", mime="audio/midi")

# ----- Full Schedule -----
combined_schedule = []
for hour in range(24):
    activity = st.session_state.activity_schedule[hour]
    energy = diurnal_energy[hour]
    align = calculate_alignment(activity, energy)
    bpm = calculate_bpm(energy, align)
    combined_schedule.append({
        "Hour": f"{hour:02d}:00",
        "🕒": time_of_day_symbol(hour),
        "Alignment": align,
        "Activity": activity,
        "Diurnal Energy": energy,
        "BPM": bpm
    })

df = pd.DataFrame(combined_schedule)
st.subheader("📋 Full 24-Hour Schedule")
st.dataframe(df.style.hide(axis="index"), use_container_width=True)

st.subheader("✏️ Edit Activities by Hour")
for hour in range(24):
    st.session_state.activity_schedule[hour] = st.selectbox(
        f"{hour:02d}:00 {time_of_day_symbol(hour)}",
        allowed_activities,
        index=allowed_activities.index(st.session_state.activity_schedule[hour]),
        key=f"activity_{hour}"
    )