
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="WNC Hatch Tool", layout="wide")

SITE = "03441000"

def temp_to_f(c): return (c*9/5)+32

def fetch_usgs(param):
    url=f"https://waterservices.usgs.gov/nwis/iv/?format=json&sites={SITE}&parameterCd={param}&period=P7D"
    data=requests.get(url).json()
    vals=data["value"]["timeSeries"][0]["values"][0]["value"]
    df=pd.DataFrame(vals)
    df["value"]=pd.to_numeric(df["value"])
    return df

# Expanded dataset
BUG_DB = [
    {"name":"Midge","temp_min":35,"temp_max":55,
     "stages":[
        {"stage":"Larva","flies":["Zebra Midge"],"size":"#20–26"},
        {"stage":"Pupa","flies":["RS2","WD-40"],"size":"#20–24"}
     ]},

    {"name":"BWO","temp_min":40,"temp_max":60,
     "stages":[
        {"stage":"Nymph","flies":["BWO Nymph"],"size":"#18–22"},
        {"stage":"Emerger","flies":["RS2","Soft Hackle"],"size":"#18–20"},
        {"stage":"Dry","flies":["BWO Dry"],"size":"#18–20"}
     ]},

    {"name":"Blue Quill","temp_min":45,"temp_max":55,
     "stages":[
        {"stage":"Emerger","flies":["Soft Hackle"],"size":"#16–18"},
        {"stage":"Dry","flies":["Blue Quill Dry"],"size":"#16–18"}
     ]},

    {"name":"Quill Gordon","temp_min":45,"temp_max":55,
     "stages":[
        {"stage":"Nymph","flies":["Quill Gordon Nymph"],"size":"#12–14"},
        {"stage":"Dry","flies":["Quill Gordon Dry"],"size":"#12–14"}
     ]},

    {"name":"March Brown","temp_min":50,"temp_max":60,
     "stages":[
        {"stage":"Nymph","flies":["Pheasant Tail"],"size":"#12–14"},
        {"stage":"Dry","flies":["March Brown Dry"],"size":"#12–14"}
     ]},

    {"name":"Caddis","temp_min":48,"temp_max":70,
     "stages":[
        {"stage":"Larva","flies":["Green Rockworm"],"size":"#14–16"},
        {"stage":"Pupa","flies":["Peeking Caddis","Soft Hackle"],"size":"#14–16"},
        {"stage":"Adult","flies":["Elk Hair Caddis","X-Caddis"],"size":"#14–16"}
     ]},

    {"name":"Sulphur","temp_min":58,"temp_max":66,
     "stages":[
        {"stage":"Nymph","flies":["Sulphur Nymph"],"size":"#16–18"},
        {"stage":"Emerger","flies":["Sulphur Emerger"],"size":"#16–18"},
        {"stage":"Dry","flies":["Comparadun"],"size":"#16–18"}
     ]},

    {"name":"Light Cahill","temp_min":58,"temp_max":68,
     "stages":[
        {"stage":"Dry","flies":["Light Cahill Dry"],"size":"#16–18"}
     ]},

    {"name":"Isonychia","temp_min":60,"temp_max":70,
     "stages":[
        {"stage":"Nymph","flies":["Iso Nymph"],"size":"#10–14"},
        {"stage":"Dry","flies":["Iso Dry"],"size":"#10–14"}
     ]},

    {"name":"Stonefly","temp_min":45,"temp_max":65,
     "stages":[
        {"stage":"Nymph","flies":["Pat’s Rubber Legs"],"size":"#8–14"}
     ]},

    {"name":"Terrestrial","temp_min":65,"temp_max":85,
     "stages":[
        {"stage":"Adult","flies":["Beetle","Ant","Hopper"],"size":"#10–18"}
     ]}
]

def get_hatch_phase(temp):
    if temp < 50: return "nymph"
    elif temp < 60: return "emerge"
    else: return "dry"

def phase_to_stage(phase):
    return {
        "nymph": ["Larva","Nymph"],
        "emerge": ["Pupa","Emerger"],
        "dry": ["Dry","Adult"]
    }.get(phase, ["Nymph"])

def score_bug(temp, bug):
    center=(bug["temp_min"]+bug["temp_max"])/2
    width=(bug["temp_max"]-bug["temp_min"])/2
    dist=abs(temp-center)
    return max(0,100-(dist/width)*100)

def prioritize_bugs(temp):
    scored=[]
    for bug in BUG_DB:
        if bug["temp_min"]<=temp<=bug["temp_max"]:
            scored.append((score_bug(temp,bug),bug))
    scored.sort(reverse=True,key=lambda x:x[0])
    return [b for _,b in scored[:4]]

# Load data
flow_df = fetch_usgs("00060")
temp_df = fetch_usgs("00010")

flow = flow_df.iloc[-1]["value"]
temp_f = temp_to_f(temp_df.iloc[-1]["value"])

phase = get_hatch_phase(temp_f)
valid_stages = phase_to_stage(phase)
top_bugs = prioritize_bugs(temp_f)

st.title("🎣 WNC Hatch Tool (Expanded)")

c1,c2 = st.columns(2)
c1.metric("Flow (CFS)", round(flow,1))
c2.metric("Temp °F", round(temp_f,1))

st.subheader("🧠 Hatch Phase")
st.write(phase)

flies=[]

st.subheader("🔥 Top Bugs")
for bug in top_bugs:
    filtered=[s for s in bug["stages"] if s["stage"] in valid_stages]
    stage=filtered[0] if filtered else bug["stages"][0]

    st.markdown(f"### {bug['name']}")
    st.write(f"Stage: {stage['stage']}")
    st.write(f"Flies: {', '.join(stage['flies'])}")
    st.write(f"Size: {stage['size']}")

    flies.extend(stage["flies"])

st.subheader("🎯 Tie These On")
for f in list(set(flies))[:5]:
    st.write(f"- {f}")
