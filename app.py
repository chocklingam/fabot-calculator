import streamlit as st
import math

st.title("FABOT - Tiruppur Loop Length Calculator")

# Inputs
ne = st.number_input("Enter Ne (leave 0 if using Tex)", min_value=0.0)
tex_input = st.number_input("Enter Tex (leave 0 if using Ne)", min_value=0.0)
gsm = st.number_input("Enter GSM Target", min_value=1.0)
shrinkage = st.number_input("Enter Shrinkage %", min_value=0.0)

# Tiruppur Conversion Factor
conversion_factor = st.slider("Conversion Factor (Tiruppur)", 2.2, 3.0, 2.6)

# Convert to Tex
if tex_input > 0:
    tex = tex_input
elif ne > 0:
    tex = 590.5 / ne
else:
    tex = 0

# Calculation
if tex > 0:
    S = shrinkage / 100
    SF = 1 / ((1 - S) ** 2)
    stitch_density = 120

    # Theoretical loop length
    LL_theoretical = (gsm * 1000) / (tex * stitch_density * SF)

    # Machine loop length (Tiruppur)
    LL_machine = LL_theoretical / conversion_factor

    # Tightness factor
    K = math.sqrt(tex) / LL_machine

    st.subheader("Results")

    st.success(f"Machine Loop Length: {round(LL_machine,2)} mm")
    st.info(f"Theoretical Loop Length: {round(LL_theoretical,2)} mm")
    st.write(f"Tightness Factor (K): {round(K,2)}")

    # Practical indicator
    if LL_machine < 2.6:
        st.error("Tight Fabric (High GSM Risk)")
    elif 2.6 <= LL_machine <= 3.0:
        st.success("Standard Tiruppur Range")
    else:
        st.warning("Loose Fabric (Low GSM Risk)")

else:
    st.warning("Enter either Ne or Tex")
