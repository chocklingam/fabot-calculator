import streamlit as st
import math

st.set_page_config(layout="wide")
st.title("FABOT – Tiruppur Industrial Knitting System")

# -------- LAYOUT -------- #
left, right = st.columns([1,1])

# -------- INPUT PANEL -------- #
with left:
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
        open_factor = 2.2
        tubular_factor = 1.1

    elif fabric_type == "Rib":
        gg_options = [14, 16, 18, 20]
        base_gg = 18
        Cf = 0.82
        open_factor = 2.05
        tubular_factor = 1.02

    else:
        gg_options = [20, 24, 28, 32]
        base_gg = 24
        Cf = 1.00
        open_factor = 2.25
        tubular_factor = 1.12

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

    # Finishing Mode
    if spandex > 0:
        default_mode = "Open Width"
    else:
        default_mode = "Tubular"

    finishing_mode = st.selectbox(
        "Finishing Mode",
        ["Tubular", "Open Width"],
        index=1 if default_mode == "Open Width" else 0
    )

    st.divider()
    st.subheader("Reverse Planning")

    target_width = st.number_input("Target Finished Width", min_value=0.0)

# -------- CALCULATION -------- #

if tex_input > 0:
    tex = tex_input
elif ne > 0:
    tex = 590.5 / ne
else:
    st.warning("Enter Ne or Tex")
    st.stop()

# Loop Length
LL = gsm / (tex * Cf)
LL *= (1 - shrinkage / 100)
LL *= 0.12
LL *= (base_gg / gg)

# Rib adjustment
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

# Process
if "Compacting" in process:
    LL *= 1.08
if "Brushing" in process:
    LL *= 1.05
if "Raising" in process:
    LL *= 1.06
if "Elastomeric Finish" in process:
    LL *= 0.92

# Color
if color == "Medium":
    LL *= 1.02
elif color == "Dark":
    LL *= 1.05

# Clamp
LL = max(2.4, min(3.4, LL))

# -------- WIDTH (FINAL INDUSTRIAL MODEL) -------- #

if finishing_mode == "Tubular":
    grey_width = dia * tubular_factor
    finished_width = grey_width * (1 - shrinkage/100)

else:
    grey_width = dia * open_factor
    finished_width = grey_width * (1 - shrinkage/100)
    finished_width *= 0.98  # tenter control

# -------- STATUS -------- #

if LL < 2.6:
    status = "TIGHT ⚠"
elif LL <= 3.0:
    status = "STD ✔"
else:
    status = "LOOSE ⚠"

# -------- RESULT PANEL -------- #

with right:
    st.subheader("RESULT PANEL")

    st.metric("Loop Length", f"{round(LL,2)} mm")
    st.metric("Status", status)

    st.metric("Finished Width", f"{round(finished_width,1)} in")
    st.metric("Grey Width", f"{round(grey_width,1)} in")

    st.metric("Finishing", finishing_mode)

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

    # Reverse planning
    if target_width > 0:
        if finishing_mode == "Tubular":
            req_grey = target_width / (1 - shrinkage/100)
            req_dia = req_grey / tubular_factor
        else:
            req_grey = target_width / ((1 - shrinkage/100) * 0.98)
            req_dia = req_grey / open_factor

        practical_dia = round(req_dia / 2) * 2

        st.divider()
        st.subheader("Reverse Planning")

        st.write(f"Required Dia: {round(req_dia,1)} in")
        st.success(f"Use Machine Dia: {practical_dia}\"")
