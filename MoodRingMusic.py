import streamlit as st
import pandas as pd

# Allowed Activities
allowed_activities = ["work", "sleep", "free", "play", "family"]

# Diurnal Energy Levels by Hour
diurnal_energy = [
    "Low", "Low", "Lowest", "Lowest", "Lowest", "Low",      
    "Rising", "Rising",                                    
    "High", "High", "High", "High",                         
    "Moderate", "Moderate",                                 
    "High", "High", "High", "Moderate", "Moderate", "Moderate",  
    "Decreasing", "Decreasing", "Low", "Low"                
]

# Time of Day Emojis
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

# Alignment Calculation with Emoji
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

# Base BPM Mapping
def base_bpm(energy):
    mapping = {
        "Lowest": 80,
        "Low": 90,
        "Rising": 110,
        "Moderate": 120,
        "High": 140,
        "Decreasing": 100
    }
    return mapping.get(energy, 120)

def alignment_modifier(alignment, energy):
    if "Enhance" in alignment:
        if energy in ["High", "Rising"]:
            return 10  # Boost BPM during high energy periods
        elif energy in ["Low", "Decreasing"]:
            return -10  # Calm things down during low energy periods
    if "Oppose" in alignment:
        if energy in ["High", "Rising"]:
            return -10  # Calm things down when too energized
        elif energy in ["Low", "Decreasing"]:
            return 10  # Try to wake things up
    return 0  # Neutral stays neutral or moderate periods stay stable

# Final BPM Calculation
def calculate_bpm(energy, alignment):
    bpm_value = base_bpm(energy) + alignment_modifier(alignment, energy)
    return max(min(bpm_value, 160), 80)  # Clamp between 80 and 160
    
# Initialize Calendar in Session State
if "activity_schedule" not in st.session_state:
    st.session_state.activity_schedule = [
        "sleep", "sleep", "sleep", "sleep", "sleep", "sleep",    
        "family", "family",                                      
        "work", "work", "work", "work",                          
        "free", "free",                                          
        "work", "work", "work", "family", "family", "play",      
        "play", "free", "sleep", "sleep"                         
    ]

st.title("🎵 Mood Ring Music")

# --- Display Finalized Alignment Table FIRST ---
combined_schedule = []
for hour in range(24):
    activity = st.session_state.activity_schedule[hour]
    energy = diurnal_energy[hour]
    alignment = calculate_alignment(activity, energy)
    bpm = calculate_bpm(energy, alignment)
    
    combined_schedule.append({
        "Hour": f"{hour:02d}:00",
        "🕒": time_of_day_symbol(hour),
        "Alignment": alignment,
        "Activity": activity,
        "Diurnal Energy": energy,
        "BPM": bpm
    })

df = pd.DataFrame(combined_schedule)

def highlight_alignment(val):
    base_val = val.split()[1].lower()
    color = {
        "enhance": "#d4edda",
        "neutral": "#fff3cd",
        "oppose": "#f8d7da"
    }.get(base_val, "white")
    return f"background-color: {color};"

styled_df = df.style.applymap(highlight_alignment, subset=["Alignment"])

st.subheader("📋 Current Mood Alignment and BPM")
st.dataframe(styled_df.hide(axis="index"), use_container_width=True)

# --- Editable Activity Schedule BELOW ---
st.subheader("✏️ Edit Activities for Each Hour")

for hour in range(24):
    st.session_state.activity_schedule[hour] = st.selectbox(
        f"{hour:02d}:00 {time_of_day_symbol(hour)}",
        allowed_activities,
        index=allowed_activities.index(st.session_state.activity_schedule[hour]),
        key=f"activity_{hour}"
    )