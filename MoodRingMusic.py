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

# Calculate Base BPS from Diurnal Energy
def base_bps(energy):
    mapping = {
        "Lowest": 1.0,
        "Low": 1.5,
        "Rising": 2.0,
        "Moderate": 2.5,
        "High": 3.0,
        "Decreasing": 2.0
    }
    return mapping.get(energy, 2.0)

# Calculate Alignment Modifier
def alignment_modifier(alignment):
    if "Enhance" in alignment:
        return 0.5
    if "Oppose" in alignment:
        return -0.5
    return 0.0

# Final BPS Calculation
def calculate_bps(energy, alignment):
    bps_value = base_bps(energy) + alignment_modifier(alignment)
    return round(max(bps_value, 0.5), 2)  # Ensure minimum BPS of 0.5

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
    bps = calculate_bps(energy, alignment)
    
    combined_schedule.append({
        "Hour": f"{hour:02d}:00",
        "🕒": time_of_day_symbol(hour),
        "Alignment": alignment,
        "Activity": activity,
        "Diurnal Energy": energy,
        "BPS": bps
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

st.subheader("📋 Current Mood Alignment and BPS")
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