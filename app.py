import streamlit as st
import numpy as np
import timber_nds.essentials as te
import timber_nds.calculation as tc
from timber_nds.design import WoodElementCalculator

st.title("Wood Element Calculator")

# Input Parameters
st.sidebar.header("Input Parameters")

# Material
material_name = st.sidebar.selectbox("Material", ["GL24h", "GL28h", "GL32h"])

# Section
width = st.sidebar.number_input("Width (cm)", value=10.0)
depth = st.sidebar.number_input("Depth (cm)", value=20.0)

# Length
length = st.sidebar.number_input("Length (m)", value=3.0)
k_yy = st.sidebar.number_input("Factor k_yy", value=1.0)
k_zz = st.sidebar.number_input("Factor k_zz", value=1.0)

# Adjustment Factors
with st.sidebar.expander("Resistance Factors"):
    factor_tension_moisture = st.number_input("Tension - Moisture", value=1.0)
    factor_bending_moisture = st.number_input("Bending - Moisture", value=1.0)

# Material Properties
material_properties_dict = {
    "GL24h": te.WoodMaterial("GL24h", 0.50, 200.0, 240.0, 240.0, 40.0, 25.0, 240.0, 110000.0, "light brown"),
    "GL28h": te.WoodMaterial("GL28h", 0.55, 200.0, 280.0, 280.0, 45.0, 28.0, 280.0, 115000.0, "brown"),
    "GL32h": te.WoodMaterial("GL32h", 0.60, 200.0, 320.0, 320.0, 50.0, 32.0, 320.0, 120000.0, "dark brown"),
}

material_properties = material_properties_dict[material_name]

# Calculations
section_properties = tc.RectangularSectionProperties(width, depth)

tension_factors = te.TensionAdjustmentFactors(factor_tension_moisture, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
bending_factors_yy = te.BendingAdjustmentFactors(factor_bending_moisture, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
bending_factors_zz = te.BendingAdjustmentFactors(factor_bending_moisture, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
shear_factors = te.ShearAdjustmentFactors(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
compression_factors_yy = te.CompressionAdjustmentFactors(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
compression_factors_zz = te.CompressionAdjustmentFactors(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
compression_perp_factors = te.PerpendicularAdjustmentFactors(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
elastic_modulus_factors = te.ElasticModulusAdjustmentFactors(1.0, 1.0, 1.0, 1.0)

calculator = WoodElementCalculator(
    tension_factors,
    bending_factors_yy,
    bending_factors_zz,
    shear_factors,
    compression_factors_yy,
    compression_factors_zz,
    compression_perp_factors,
    elastic_modulus_factors,
    material_properties,
    section_properties,
)

# Results
st.header("Results")

st.write(f"Tension Strength: {calculator.section_tension_strength():.2f} kgf")
st.write(f"Bending Strength (yy): {calculator.section_bending_strength('yy')/100:.2f} kgf m")
st.write(f"Bending Strength (zz): {calculator.section_bending_strength('zz')/100:.2f} kgf m")
st.write(f"Shear Strength: {calculator.section_shear_strength():.2f} kgf")
st.write(f"Compression Strength (yy): {calculator.section_compression_strength('yy'):.2f} kgf")
st.write(f"Compression Strength (zz): {calculator.section_compression_strength('zz'):.2f} kgf")
st.write(f"Compression Perpendicular Strength: {calculator.section_compression_perp_strength():.2f} kgf")


