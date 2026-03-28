import streamlit as st
import math

st.set_page_config(layout="wide")
st.title("FABOT – Tiruppur Production System")

# -------- LAYOUT -------- #
col1, col2 = st.columns([1,1])

# -------- INPUT PANEL -------- #
with col1:
    st.subheader("INPUT PANEL")

    ne = st.number_input("Ne", min_value=0.0)
    tex_input = st.number_input("Tex", min_value=0.0)

    gsm = st.number_input("GSM", min_value=1.0)
    shrinkage = st.number_input("Shrinkage %", min_value=0.0)

    dia = st.number_input("Machine Dia (inches)", min_value=10.0)

    fabric_type = st.selectbox("Fabric Type", ["Single Jersey", "Rib", "Interlock"])

    if fabric_type == "Single Jersey":
        gg_options = [20, 24, 26, 28, 32]
        base_gg = 28
        Cf = 0.60
        efficiency = 0.90
    elif fabric_type == "Rib":
        gg_options = [14, 16, 18, 20]
        base_gg = 18
        Cf = 0.82
        efficiency = 0.88
    else:
        gg_options = [20, 24, 28, 32]
        base_gg = 24
        Cf = 1.00
        efficiency = 0.86

    gg = st.selectbox("Gauge (GG)", gg_options)

    rib_type = None
    if fabric_type == "Rib":
        rib_type = st.selectbox("Rib Type", ["1x1", "2x2", "3x3"])

    st.subheader("Composition (%)")
    cotton = st.number_input("Cotton %", 0.0, 100.0)
    poly = st.number_input("Poly %", 0.0, 100.0)
    viscose = st.number_input("Viscose %", 0.0, 100.0)
    spandex = st.number_input("Spandex %", 0.0, 20.0)

    total = cotton + poly + viscose + spandex
    if total != 100:
        st.warning("Total must be 100%")
        st.stop()

    process = st.multiselect("Process", [
        "Compacting", "Brushing", "Raising", "Elastomeric Finish"
    ])

    color = st.selectbox("Color", ["Light", "Medium", "Dark"])

# -------- CALCULATION -------- #

if tex_input > 0:
    tex = tex_input
elif ne > 0:
    tex = 590.5 / ne
else:
    st.warning("Enter Ne or Tex")
    st.stop()

LL = gsm / (tex * Cf)
LL *= (1 - shrinkage / 100)
LL *= 0.12
LL *= (base_gg / gg)

# Rib correction
if rib_type == "2x2":
    LL /= 1.08
elif rib_type == "3x3":
    LL /= 1.15

# Composition effect
content_factor = (
    (cotton/100)*1.00 +
    (poly/100)*1.05 +
    (viscose/100)*1.08 +
    (spandex/100)*0.90
)
LL *= content_factor

# Spandex tightening
if spandex > 0:
    LL *= (1 - spandex * 0.005)

# Process correction
if "Compacting" in process:
    LL *= 1.08
if "Brushing" in process:
    LL *= 1.05
if "Raising" in process:
    LL *= 1.06
if "Elastomeric Finish" in process:
    LL *= 0.92

# Color correction
if color == "Medium":
    LL *= 1.02
elif color == "Dark":
    LL *= 1.05

# Clamp
LL = max(2.4, min(3.4, LL))

# Width calculation
grey_width = math.pi * dia * efficiency
finished_width = grey_width * (1 - shrinkage/100)

# -------- STATUS -------- #
if LL < 2.6:
    status = "TIGHT ⚠"
elif LL <= 3.0:
    status = "STD ✔"
else:
    status = "LOOSE ⚠"

# -------- RESULT PANEL -------- #
with col2:
    st.subheader("RESULT PANEL")

    st.metric("Loop Length", f"{round(LL,2)} mm")
    st.metric("Status", status)

    st.metric("Finished Width", f"{round(finished_width,1)} in")
    st.metric("Machine Dia", f"{round(dia,1)} in")

    st.divider()

    st.subheader("Suggestions")

    tex_cost = tex * 1.15
    ne_cost = 590.5 / tex_cost

    tex_quality = tex * 0.85
    ne_quality = 590.5 / tex_quality

    gg_down = gg - 2 if gg - 2 in gg_options else gg
    gg_up = gg + 2 if gg + 2 in gg_options else gg

    st.write(f"💰 Cost → {round(ne_cost,1)}Ne / {gg_down}GG")
    st.write(f"🎯 Quality → {round(ne_quality,1)}Ne / {gg_up}GG")

    if spandex > 0:
        denier = gsm * (spandex/100) * 1.2
        st.write(f"Spandex → {round(denier)} Denier")
