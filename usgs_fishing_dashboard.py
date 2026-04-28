
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="WNC Hatch Priority Tool", layout="wide")

SITE = "03441000"

def temp_to_f(c):
    return (c * 9/5) + 32

def fetch_usgs(param):
    url = f"https://waterservices.usgs.gov/nwis/iv/?format=json&sites={SITE}&parameterCd={param}&period=P7D"
    data = requests.get(url).json()
    vals = data["value"]["timeSeries"][0]["values"][0]["value"]
    df = pd.DataFrame(vals)
    df["value"] = pd.to_numeric(df["value"])
    return df

# Expanded bug dataset
BUG_DB = [
    {"name":"Midge","temp_min":35,"temp_max":55,
     "stages":[{"stage":"Larva","flies":["Zebra Midge"],"size":"#20–26"},
               {"stage":"Pupa","flies":["RS2","WD-40"],"size":"#20–24"}]},

    {"name":"BWO","temp_min":40,"temp_max":60,
     "stages":[{"stage":"Nymph","flies":["BWO Nymph"],"size":"#18–22"},
               {"stage":"Emerger","flies":["RS2"],"size":"#18–20"},
               {"stage":"Dry","flies":["BWO Dry"],"size":"#18–20"}]},

    {"name":"Caddis","temp_min":48,"temp_max":70,
     "stages":[{"stage":"Larva","flies":["Green Rockworm"],"size":"#14–16"},
               {"stage":"Pupa","flies":["Peeking Caddis"],"size":"#14–16"},
               {"stage":"Adult","flies":["Elk Hair Caddis"],"size":"#14–16"}]},

    {"name":"Sulphur","temp_min":58,"temp_max":66,
     "stages":[{"stage":"Nymph","flies":["Sulphur Nymph"],"size":"#16–18"},
               {"stage":"Dry","flies":["Comparadun"],"size":"#16–18"}]},

    {"name":"Terrestrial","temp_min":65,"temp_max":85,
     "stages":[{"stage":"Adult","flies":["Beetle","Ant"],"size":"#12–18"}]}
]

from datetime import datetime
import pytz

def get_time_of_day():
    tz = pytz.timezone("America/New_York")  # change if needed
    local_time = datetime.now(tz)
    hour = local_time.hour

    if hour < 11:
        return "morning"
    elif hour < 17:
        return "afternoon"
    else:
        return "evening"

def score_bug(temp, bug):
    center = (bug["temp_min"] + bug["temp_max"]) / 2
    width = (bug["temp_max"] - bug["temp_min"]) / 2
    dist = abs(temp - center)
    return max(0, 100 - (dist / width) * 100)

def prioritize_bugs(temp):
    scored = []
    for bug in BUG_DB:
        if bug["temp_min"] <= temp <= bug["temp_max"]:
            scored.append((score_bug(temp, bug), bug))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [b for _, b in scored[:3]]

def best_stage(bug, tod):
    if tod == "morning":
        return bug["stages"][0]
    elif tod == "afternoon":
        for s in bug["stages"]:
            if s["stage"] in ["Pupa","Emerger"]:
                return s
    elif tod == "evening":
        for s in bug["stages"]:
            if s["stage"] in ["Adult","Dry"]:
                return s
    return bug["stages"][0]

# Load data
flow_df = fetch_usgs("00060")
temp_df = fetch_usgs("00010")

flow = flow_df.iloc[-1]["value"]
temp_f = temp_to_f(temp_df.iloc[-1]["value"])

tod = get_time_of_day()
top_bugs = prioritize_bugs(temp_f)

# UI
st.title("🎣 WNC Hatch Priority Tool")

c1,c2 = st.columns(2)
c1.metric("Flow (CFS)", round(flow,1))
c2.metric("Water Temp (°F)", round(temp_f,1))

st.subheader("🔥 Top Bugs Right Now")

flies = []

for bug in top_bugs:
    stage = best_stage(bug, tod)
    st.markdown(f"### {bug['name']}")
    st.write(f"Stage: {stage['stage']}")
    st.write(f"Flies: {', '.join(stage['flies'])}")
    st.write(f"Size: {stage['size']}")
    flies.extend(stage["flies"])

st.subheader("🎯 Tie These On")

for f in list(set(flies))[:3]:
    st.write(f"- {f}")

st.caption(f"Time of Day: {tod}")
