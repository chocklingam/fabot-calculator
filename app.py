import streamlit as st

st.title("FABOT – Tiruppur Production Loop Length Engine")

# ---------------- INPUTS ---------------- #

# Yarn input
ne = st.number_input("Enter Ne (leave 0 if using Tex)", min_value=0.0)
tex_input = st.number_input("Enter Tex (leave 0 if using Ne)", min_value=0.0)

gsm = st.number_input("Target GSM", min_value=1.0)
shrinkage = st.number_input("Shrinkage %", min_value=0.0)

# Fabric selection
fabric_type = st.selectbox("Fabric Type", ["Single Jersey", "Rib", "Interlock"])

# Gauge options
if fabric_type == "Single Jersey":
    gg_options = [20, 24, 26, 28, 32]
    base_gg = 28
elif fabric_type == "Rib":
    gg_options = [14, 16, 18, 20]
    base_gg = 18
elif fabric_type == "Interlock":
    gg_options = [20, 24, 28, 32]
    base_gg = 24

gg = st.selectbox("Machine Gauge (GG)", gg_options)

# Blend
blend = st.selectbox("Yarn Type", [
    "100% Cotton", "PC", "CVC", "Polyester", "Elastane Blend"
])

# Process
process = st.multiselect("Processes", [
    "Bio Wash", "Compacting", "Brushing",
    "Raising", "Laminating", "Elastomeric Finish"
])

# Color
color = st.selectbox("Color Shade", ["Light", "Medium", "Dark"])

# ---------------- CALCULATION ---------------- #

# Convert to Tex
if tex_input > 0:
    tex = tex_input
elif ne > 0:
    tex = 590.5 / ne
else:
    tex = 0

if tex > 0:

    # Base loop model (Tiruppur calibrated)
    base_LL = gsm / (tex * 0.6)

    # Shrinkage correction
    LL = base_LL * (1 - (shrinkage / 100))

    # Scale to machine loop range
    LL = LL * 0.12

    # Gauge correction
    gg_factor = base_gg / gg
    LL *= gg_factor

    # Fabric correction
    if fabric_type == "Rib":
        LL *= 0.92
    elif fabric_type == "Interlock":
        LL *= 0.88

    # Blend correction
    if blend == "Polyester":
        LL *= 1.05
    elif blend == "Elastane Blend":
        LL *= 0.90

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

    # Clamp to realistic Tiruppur range
    LL = max(2.4, min(3.4, LL))

    # ---------------- OUTPUT ---------------- #

    st.subheader("Results")

    st.success(f"Machine Loop Length: {round(LL,2)} mm")

    # Range indicator
    if LL < 2.6:
        st.error("Tight Fabric (High GSM risk)")
    elif 2.6 <= LL <= 3.0:
        st.success("Standard Tiruppur Range")
    else:
        st.warning("Loose Fabric (Low GSM risk)")

    # ---------------- SUGGESTIONS ---------------- #

    st.subheader("Optimization Suggestions")

    # Cost option
    tex_cost = tex * 1.15
    ne_cost = 590.5 / tex_cost

    # Quality option
    tex_quality = tex * 0.85
    ne_quality = 590.5 / tex_quality

    # Gauge suggestions
    gg_down = gg - 2 if gg - 2 in gg_options else gg
    gg_up = gg + 2 if gg + 2 in gg_options else gg

    st.write("💰 Cost Saving Option:")
    st.write(f"→ Use approx Ne: {round(ne_cost,1)} | GG: {gg_down}")

    st.write("🎯 Quality / Uniformity Option:")
    st.write(f"→ Use approx Ne: {round(ne_quality,1)} | GG: {gg_up}")

else:
    st.warning("Enter either Ne or Tex")
