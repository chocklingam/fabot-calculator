import streamlit as st
import math

st.title("FABOT Loop Length Calculator")

ne = st.number_input("Enter Ne (leave 0 if using Tex)", min_value=0.0)
tex_input = st.number_input("Enter Tex (leave 0 if using Ne)", min_value=0.0)
gsm = st.number_input("Enter GSM Target", min_value=1.0)
shrinkage = st.number_input("Enter Shrinkage %", min_value=0.0)

if tex_input > 0:
    tex = tex_input
elif ne > 0:
    tex = 590.5 / ne
else:
    tex = 0

if tex > 0:
    S = shrinkage / 100
    SF = 1 / ((1 - S) ** 2)
    stitch_density = 120

    loop_length = (gsm * 1000) / (tex * stitch_density * SF)
    tightness_factor = math.sqrt(tex) / loop_length

    st.subheader("Results")
    st.write(f"Tex: {round(tex,2)}")
    st.write(f"Shrinkage Factor: {round(SF,3)}")
    st.write(f"Loop Length: {round(loop_length,2)} mm")
    st.write(f"Tightness Factor (K): {round(tightness_factor,2)}")
else:
    st.warning("Enter either Ne or Tex")