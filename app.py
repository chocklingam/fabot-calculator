import streamlit as st

st.set_page_config(layout="wide")
st.title("FABOT – Industrial Fabric Engineering System")

# ---------------- INPUT PANEL ---------------- #
st.header("INPUT PANEL")

col1, col2 = st.columns(2)

with col1:
    fabric_type = st.selectbox("Fabric Type", ["Single Jersey","Rib","Interlock","Fleece"])

    fleece_type = None
    if fabric_type == "Fleece":
        fleece_type = st.selectbox("Fleece Type", ["2 Thread","3 Thread"])

    gsm = st.number_input("Target GSM", min_value=1.0, value=180.0)
    dia = st.number_input("Machine Dia (inches)", min_value=10.0, value=30.0)
    gg = st.selectbox("Gauge (GG)", [14,16,18,20,24,26,28,32])

    shrinkage = st.number_input("Shrinkage %", min_value=0.0, value=5.0)

with col2:
    st.subheader("Yarn Details")

    face_ne = st.number_input("Face Yarn Ne", min_value=0.0, value=30.0)
    binder_ne = st.number_input("Binder Yarn Ne (optional)", min_value=0.0)
    loop_ne = st.number_input("Loop Yarn Ne (for fleece)", min_value=0.0)

    st.subheader("Composition (%)")

    cotton = st.number_input("Cotton %", 0, 100, 100)
    poly = st.number_input("Polyester %", 0, 100, 0)
    viscose = st.number_input("Viscose %", 0, 100, 0)
    spandex = st.number_input("Spandex %", 0, 20, 0)

    total = cotton + poly + viscose + spandex
    if total != 100:
        st.warning("Total composition must be 100%")
        st.stop()

    color = st.selectbox("Color Depth", ["Light","Medium","Dark"])
    process = st.selectbox("Process", ["Greige","Reactive Dye","Bio Wash","Compacting","Heat Setting","Raising"])

# ---------------- EFFECTIVE TEX ---------------- #

def ne_to_tex(ne):
    return 590.5 / ne if ne > 0 else 0

face_tex = ne_to_tex(face_ne)
binder_tex = ne_to_tex(binder_ne)
loop_tex = ne_to_tex(loop_ne)

if fabric_type == "Fleece":
    if fleece_type == "2 Thread":
        effective_tex = face_tex * 0.65 + loop_tex * 0.35
    elif fleece_type == "3 Thread":
        effective_tex = face_tex * 0.50 + binder_tex * 0.20 + loop_tex * 0.30
else:
    effective_tex = face_tex

# ---------------- LOOP LENGTH ---------------- #

LL = gsm / (effective_tex * 0.60)   # base
LL *= 0.165   # calibrated factor

# Fabric correction
if fabric_type == "Rib":
    LL *= 1.10
elif fabric_type == "Interlock":
    LL *= 1.15
elif fabric_type == "Fleece":
    LL *= 1.20

# Fiber correction
fiber_factor = (
    cotton * 1.00 +
    poly * 0.95 +
    viscose * 1.08 +
    spandex * 0.90
) / 100

LL *= fiber_factor

# Color correction
if color == "Medium":
    LL *= 1.02
elif color == "Dark":
    LL *= 1.04

# Process correction
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

# Clamp
LL = max(2.4, min(3.5, LL))

# ---------------- WIDTH ---------------- #

# Base width factors
if fabric_type == "Single Jersey":
    open_factor = 2.0
    tubular_factor = 1.0
elif fabric_type == "Rib":
    open_factor = 1.9
    tubular_factor = 0.95
elif fabric_type == "Interlock":
    open_factor = 2.0
    tubular_factor = 1.05
elif fabric_type == "Fleece":
    open_factor = 2.1
    tubular_factor = 1.05

# Lycra effect
if spandex > 0:
    finishing_mode = "Open Width"
    open_factor *= 0.92
else:
    finishing_mode = st.selectbox("Finishing Mode", ["Tubular","Open Width"])

# Width calculation
if finishing_mode == "Open Width":
    finished_width = dia * open_factor
else:
    finished_width = dia * tubular_factor

# Fiber width correction
width_factor = (
    cotton * 1.00 +
    poly * 0.97 +
    viscose * 1.05 +
    spandex * 0.92
) / 100

finished_width *= width_factor

# Shrinkage
finished_width *= (1 - shrinkage/100)

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
    st.metric("Finishing Mode", finishing_mode)

    if spandex > 0:
        denier = gsm * (spandex/100) * 1.2
        st.metric("Spandex Denier", round(denier))

# ---------------- SMART INSIGHTS ---------------- #

st.subheader("SMART INSIGHTS")

if spandex > 0:
    st.info("Lycra Fabric → Heat Setting + Open Width Finishing")

if fabric_type == "Fleece":
    st.info("Fleece → Loop yarn dominates GSM")

if viscose > 50:
    st.warning("Viscose high → Expect higher shrinkage & width variation")

if poly > 50:
    st.info("Poly rich → Stable width, lower shrinkage")

if LL < 2.6:
    st.warning("Increase Loop Length → reduce GSM or increase GG")

if LL > 3.1:
    st.warning("Reduce Loop Length → increase GSM or reduce GG")
