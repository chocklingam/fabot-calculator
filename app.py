import streamlit as st

st.set_page_config(layout="wide")

st.title("FABOT – Production Fabric Engine (Tiruppur Calibrated)")

# ---------------- INPUT PANEL ---------------- #
st.header("INPUT PANEL")

col1, col2 = st.columns(2)

with col1:
    ne = st.number_input("Ne", min_value=0.0, value=30.0)
    tex = st.number_input("Tex (optional)", min_value=0.0, value=0.0)
    gsm = st.number_input("GSM", min_value=1.0, value=180.0)
    dia = st.number_input("Machine Dia (inches)", min_value=10.0, value=30.0)
    gg = st.selectbox("GG", [14,16,18,20,24,26,28,32])

with col2:
    fabric_type = st.selectbox("Fabric Type", ["Single Jersey","Rib","Interlock"])
    structure = st.selectbox("Structure", ["1x1","2x2","3x3"])
    composition = st.slider("Spandex %", 0, 20, 0)
    color = st.selectbox("Color Depth", ["Light","Medium","Dark"])
    process = st.selectbox("Process", ["Greige","Reactive Dye","Bio Wash","Compacting","Heat Setting","Raising"])

shrinkage = st.number_input("Shrinkage %", min_value=0.0, value=5.0)
finishing_mode = st.selectbox("Finishing Mode", ["Tubular","Open Width"])

# ---------------- YARN CONVERSION ---------------- #
if tex > 0:
    ne = 590.5 / tex

# ---------------- LOOP LENGTH ---------------- #
LL = (gsm / ne) / gg
LL *= 0.165   # calibrated

# ---------------- FABRIC TYPE CORRECTION ---------------- #
if fabric_type == "Rib":
    LL *= 1.1
elif fabric_type == "Interlock":
    LL *= 1.15

# ---------------- STRUCTURE CORRECTION ---------------- #
if structure == "2x2":
    LL *= 1.05
elif structure == "3x3":
    LL *= 1.08

# ---------------- COLOR IMPACT ---------------- #
if color == "Light":
    LL *= 1.01
elif color == "Medium":
    LL *= 1.02
elif color == "Dark":
    LL *= 1.04

# ---------------- PROCESS IMPACT ---------------- #
if process == "Bio Wash":
    LL *= 1.04
elif process == "Reactive Dye":
    LL *= 1.02
elif process == "Raising":
    LL *= 1.05
elif process == "Heat Setting":
    LL *= 0.98
elif process == "Compacting":
    LL *= 0.97

# ---------------- WIDTH CALCULATION ---------------- #
if fabric_type == "Single Jersey":
    open_factor = 2.0
    tubular_factor = 1.0
elif fabric_type == "Rib":
    open_factor = 1.9
    tubular_factor = 0.95
elif fabric_type == "Interlock":
    open_factor = 2.0
    tubular_factor = 1.05

# Lycra effect
if composition > 0:
    open_factor *= 0.92

if finishing_mode == "Open Width":
    finished_width = dia * open_factor
else:
    finished_width = dia * tubular_factor

# Shrinkage adjustment
finished_width *= (1 - shrinkage/100)

# Reverse planning (grey width)
grey_width = finished_width / (1 - shrinkage/100)

# ---------------- STATUS ---------------- #
if LL < 2.5:
    status = "TIGHT ⚠"
elif LL > 3.2:
    status = "LOOSE ⚠"
else:
    status = "OK ✔"

# ---------------- RESULT PANEL ---------------- #
st.header("RESULT PANEL")

col3, col4 = st.columns(2)

with col3:
    st.metric("Loop Length", f"{round(LL,2)} mm")
    st.metric("Status", status)
    st.metric("Finished Width", f"{round(finished_width,1)} in")

with col4:
    st.metric("Grey Width", f"{round(grey_width,1)} in")
    st.metric("Suggested GG", gg)
    st.metric("Spandex %", f"{composition}%")

# ---------------- SMART SUGGESTIONS ---------------- #
st.subheader("SMART SUGGESTIONS")

if LL < 2.6:
    st.warning("Increase Loop Length → Reduce GSM or increase GG")

if LL > 3.1:
    st.warning("Reduce Loop Length → Increase GSM or reduce GG")

if composition > 0:
    st.info("Lycra Fabric → Use Heat Setting + Open Width Finishing")
