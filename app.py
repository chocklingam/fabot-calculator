import streamlit as st

st.title("FABOT – Tiruppur Production Engine")

# ---------------- INPUTS ---------------- #

# Yarn
ne = st.number_input("Ne (0 if using Tex)", min_value=0.0)
tex_input = st.number_input("Tex (0 if using Ne)", min_value=0.0)

gsm = st.number_input("Target GSM", min_value=1.0)
shrinkage = st.number_input("Shrinkage %", min_value=0.0)

# Fabric Type
fabric_type = st.selectbox("Fabric Type", ["Single Jersey", "Rib", "Interlock"])

# Gauge logic
if fabric_type == "Single Jersey":
    gg_options = [20, 24, 26, 28, 32]
    base_gg = 28
elif fabric_type == "Rib":
    gg_options = [14, 16, 18, 20]
    base_gg = 18
else:
    gg_options = [20, 24, 28, 32]
    base_gg = 24

gg = st.selectbox("Machine Gauge (GG)", gg_options)

# Rib type
rib_type = None
if fabric_type == "Rib":
    rib_type = st.selectbox("Rib Type", ["1x1", "2x2", "3x3"])

# Composition
st.subheader("Composition (%)")

cotton = st.number_input("Cotton %", 0.0, 100.0)
poly = st.number_input("Polyester %", 0.0, 100.0)
viscose = st.number_input("Viscose %", 0.0, 100.0)
spandex = st.number_input("Spandex %", 0.0, 20.0)

total = cotton + poly + viscose + spandex

if total != 100:
    st.warning("Total composition must be 100%")
    st.stop()

# Process & Color
process = st.multiselect("Processes", [
    "Compacting", "Brushing", "Raising", "Elastomeric Finish"
])

color = st.selectbox("Color", ["Light", "Medium", "Dark"])

# ---------------- CALCULATION ---------------- #

# Tex conversion
if tex_input > 0:
    tex = tex_input
elif ne > 0:
    tex = 590.5 / ne
else:
    st.warning("Enter Ne or Tex")
    st.stop()

# Fabric constant
if fabric_type == "Single Jersey":
    Cf = 0.60
elif fabric_type == "Rib":
    Cf = 0.82
else:
    Cf = 1.00

# Base loop
LL = gsm / (tex * Cf)

# Shrinkage
LL *= (1 - shrinkage / 100)

# Scale to mm
LL *= 0.12

# Gauge correction
LL *= (base_gg / gg)

# Rib correction
if rib_type == "2x2":
    LL /= 1.08
elif rib_type == "3x3":
    LL /= 1.15

# Content correction
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

# Clamp realistic range
LL = max(2.4, min(3.4, LL))

# ---------------- OUTPUT ---------------- #

# Status
if LL < 2.6:
    status = "TIGHT ⚠"
elif LL <= 3.0:
    status = "STD ✔"
else:
    status = "LOOSE ⚠"

st.subheader("Quick Result")

if "STD" in status:
    st.success(f"LL: {round(LL,2)} mm | {status}")
elif "TIGHT" in status:
    st.error(f"LL: {round(LL,2)} mm | {status}")
else:
    st.warning(f"LL: {round(LL,2)} mm | {status}")

# ---------------- SUGGESTIONS ---------------- #

tex_cost = tex * 1.15
ne_cost = 590.5 / tex_cost

tex_quality = tex * 0.85
ne_quality = 590.5 / tex_quality

gg_down = gg - 2 if gg - 2 in gg_options else gg
gg_up = gg + 2 if gg + 2 in gg_options else gg

st.write("💰 Cost:", f"{round(ne_cost,1)}Ne / {gg_down}GG")
st.write("🎯 Quality:", f"{round(ne_quality,1)}Ne / {gg_up}GG")

# ---------------- SPANDEX DENIER ---------------- #

if spandex > 0:
    denier = gsm * (spandex/100) * 1.2
    st.write(f"Spandex: ~{round(denier)} Denier")
