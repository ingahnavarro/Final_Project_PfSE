import streamlit as st
from dataclasses import dataclass
import timber_nds.essentials as te
import timber_nds.calculation as tc
from timber_nds.design import WoodElementCalculator
import matplotlib.pyplot as plt
import numpy as np

st.title("Calculadora de Elementos de Madera")


# --- Data Classes (same as before) ---
@dataclass
class WoodMaterial:
    name: str
    specific_gravity: float
    fibre_saturation_point: float
    tension_strength: float
    bending_strength: float
    shear_strength: float
    compression_perpendicular_strength: float
    compression_parallel_strength: float
    elastic_modulus: float
    color: str


@dataclass
class RectangularSection:
    name: str
    depth: float  # in cm
    width: float  # in cm


@dataclass
class MemberDefinition:
    name: str
    length: float  # in cm
    effective_length_factor_yy: float
    effective_length_factor_zz: float


@dataclass
class TensionAdjustmentFactors:
    due_moisture: float
    due_temperature: float
    due_size: float
    due_incising: float
    due_format_conversion: float
    due_resistance_reduction: float
    due_time_effect: float


@dataclass
class BendingAdjustmentFactors:
    due_moisture: float
    due_temperature: float
    due_beam_stability: float
    due_size: float
    due_flat_use: float
    due_incising: float
    due_repetitive_member: float
    due_format_conversion: float
    due_resistance_reduction: float
    due_time_effect: float


@dataclass
class ShearAdjustmentFactors:
    due_moisture: float
    due_temperature: float
    due_incising: float
    due_format_conversion: float
    due_resistance_reduction: float
    due_time_effect: float


@dataclass
class CompressionAdjustmentFactors:
    due_moisture: float
    due_temperature: float
    due_size: float
    due_incising: float
    due_column_stability: float
    due_format_conversion: float
    due_resistance_reduction: float
    due_time_effect: float


@dataclass
class PerpendicularAdjustmentFactors:
    due_moisture: float
    due_temperature: float
    due_beam_stability: float
    due_size: float
    due_flat_use: float
    due_incising: float
    due_repetitive_member: float
    due_column_stability: float
    due_buckling_stiffness: float
    due_bearing_area: float
    due_format_conversion: float
    due_resistance_reduction: float
    due_time_effect: float


@dataclass
class ElasticModulusAdjustmentFactors:
    due_moisture: float
    due_temperature: float
    due_incising: float
    due_format_conversion: float


@dataclass
class Forces:
    axial_force: float  # in kgf
    shear_y: float  # in kgf
    shear_z: float  # in kgf
    moment_xx: float  # in kgf*m
    moment_yy: float  # in kgf*m
    moment_zz: float  # in kgf*m


# --- Sidebar for Input Parameters ---
st.sidebar.title("Parámetros de Entrada")
main_tabs = st.sidebar.tabs(["Propiedades", "Factores", "Fuerzas"])

with main_tabs[0]:  # Propiedades Tab
    st.header("Propiedades del Material")
    material_name = st.text_input("Nombre del Material", value="Madera Genérica", key='material_name')
    specific_gravity = st.number_input("Peso Específico", value=0.6, key='specific_gravity')
    fibre_saturation_point = st.number_input("Punts de Saturación de Fibra", value=0.25, key='fibre_saturation_point')
    tension_strength = st.number_input("Resistencia a la Tracción (kgf/cm²)", value=100.0, key='tension_strength')
    bending_strength = st.number_input("Resistencia a la Flexión (kgf/cm²)", value=150.0, key='bending_strength')
    shear_strength = st.number_input("Resistencia al Corte (kgf/cm²)", value=25.0, key='shear_strength')
    compression_perpendicular_strength = st.number_input("Resistencia a la Compresión Perpendicular (kgf/cm²)",
                                                         value=30.0,
                                                         key='comp_perp_strength')
    compression_parallel_strength = st.number_input("Resistencia a la Compresión Paralela (kgf/cm²)", value=120.0,
                                                    key='comp_para_strength')
    elastic_modulus = st.number_input("Módulo de Elasticidad (kgf/cm²)", value=100000.0, key='elastic_modulus')
    color = st.text_input("Color", value="Marrón", key='color')

    st.header("Propiedades de la Sección")
    section_name = st.text_input("Nombre de la Sección", value="Sección Rectangular", key='section_name')
    depth = st.number_input("Altura (cm)", value=20.0, key='depth')
    width = st.number_input("Ancho (cm)", value=10.0, key='width')

    st.header("Propiedades del Miembro")
    member_name = st.text_input("Nombre del Miembro", value="Viga Principal", key='member_name')
    length = st.number_input("Longitud (cm)", value=300.0, key='length')
    k_yy = st.number_input("Factor k_yy", value=1.0, key='k_yy')
    k_zz = st.number_input("Factor k_zz", value=1.0, key='k_zz')

with main_tabs[1]:  # Factores Tab
    st.subheader("Ajuste a la Tracción")
    factor_tension_moisture = st.number_input("Humedad", value=1.0, key='tension_moisture')
    factor_tension_temperature = st.number_input("Temperatura", value=1.0, key='tension_temperature')
    factor_tension_size = st.number_input("Tamaño", value=1.0, key='tension_size')
    factor_tension_incising = st.number_input("Incisión", value=1.0, key='tension_incising')
    factor_tension_format_conversion = st.number_input("Conversión de Formato", value=1.0, key='tension_format')
    factor_tension_resistance_reduction = st.number_input("Reducción de Resistencia", value=1.0,
                                                          key='tension_resistance')
    factor_tension_time_effect = st.number_input("Efecto del Tiempo", value=1.0, key='tension_time')

    st.subheader("Ajuste a la Flexión (yy)")
    factor_bending_yy_moisture = st.number_input("Humedad", value=1.0, key='bending_yy_moisture')
    factor_bending_yy_temperature = st.number_input("Temperatura", value=1.0, key='bending_yy_temperature')
    factor_bending_yy_beam_stability = st.number_input("Estabilidad de la Viga", value=1.0, key='bending_yy_stability')
    factor_bending_yy_size = st.number_input("Tamaño", value=1.0, key='bending_yy_size')
    factor_bending_yy_flat_use = st.number_input("Uso Plano", value=1.0, key='bending_yy_flat')
    factor_bending_yy_incising = st.number_input("Incisión", value=1.0, key='bending_yy_incising')
    factor_bending_yy_repetitive_member = st.number_input("Miembro Repetitivo", value=1.0, key='bending_yy_repetitive')
    factor_bending_yy_format_conversion = st.number_input("Conversión de Formato", value=1.0, key='bending_yy_format')
    factor_bending_yy_resistance_reduction = st.number_input("Reducción de Resistencia", value=1.0,
                                                             key='bending_yy_resistance')
    factor_bending_yy_time_effect = st.number_input("Efecto del Tiempo", value=1.0, key='bending_yy_time')

    st.subheader("Ajuste a la Flexión (zz)")
    factor_bending_zz_moisture = st.number_input("Humedad", value=1.0, key='bending_zz_moisture')
    factor_bending_zz_temperature = st.number_input("Temperatura", value=1.0, key='bending_zz_temperature')
    factor_bending_zz_beam_stability = st.number_input("Estabilidad de la Viga", value=1.0, key='bending_zz_stability')
    factor_bending_zz_size = st.number_input("Tamaño", value=1.0, key='bending_zz_size')
    factor_bending_zz_flat_use = st.number_input("Uso Plano", value=1.0, key='bending_zz_flat')
    factor_bending_zz_incising = st.number_input("Incisión", value=1.0, key='bending_zz_incising')
    factor_bending_zz_repetitive_member = st.number_input("Miembro Repetitivo", value=1.0, key='bending_zz_repetitive')
    factor_bending_zz_format_conversion = st.number_input("Conversión de Formato", value=1.0, key='bending_zz_format')
    factor_bending_zz_resistance_reduction = st.number_input("Reducción de Resistencia", value=1.0,
                                                             key='bending_zz_resistance')
    factor_bending_zz_time_effect = st.number_input("Efecto del Tiempo", value=1.0, key='bending_zz_time')

    st.subheader("Ajuste al Corte")
    factor_shear_moisture = st.number_input("Humedad", value=1.0, key='shear_moisture')
    factor_shear_temperature = st.number_input("Temperatura", value=1.0, key='shear_temperature')
    factor_shear_incising = st.number_input("Incisión", value=1.0, key='shear_incising')
    factor_shear_format_conversion = st.number_input("Conversión de Formato", value=1.0, key='shear_format')
    factor_shear_resistance_reduction = st.number_input("Reducción de Resistencia", value=1.0, key='shear_resistance')
    factor_shear_time_effect = st.number_input("Efecto del Tiempo", value=1.0, key='shear_time')

    st.subheader("Ajuste a la Compresión (yy)")
    factor_compression_yy_moisture = st.number_input("Humedad", value=1.0, key='compression_yy_moisture')
    factor_compression_yy_temperature = st.number_input("Temperatura", value=1.0, key='compression_yy_temperature')
    factor_compression_yy_size = st.number_input("Tamaño", value=1.0, key='compression_yy_size')
    factor_compression_yy_incising = st.number_input("Incisión", value=1.0, key='compression_yy_incising')
    factor_compression_yy_column_stability = st.number_input("Estabilidad de la Columna", value=1.0,
                                                             key='compression_yy_stability')
    factor_compression_yy_format_conversion = st.number_input("Conversión de Formato", value=1.0,
                                                              key='compression_yy_format')
    factor_compression_yy_resistance_reduction = st.number_input("Reducción de Resistencia", value=1.0,
                                                                 key='compression_yy_resistance')
    factor_compression_yy_time_effect = st.number_input("Efecto del Tiempo", value=1.0, key='compression_yy_time')

    st.subheader("Ajuste a la Compresión (zz)")
    factor_compression_zz_moisture = st.number_input("Humedad", value=1.0, key='compression_zz_moisture')
    factor_compression_zz_temperature = st.number_input("Temperatura", value=1.0, key='compression_zz_temperature')
    factor_compression_zz_size = st.number_input("Tamaño", value=1.0, key='compression_zz_size')
    factor_compression_zz_incising = st.number_input("Incisión", value=1.0, key='compression_zz_incising')
    factor_compression_zz_column_stability = st.number_input("Estabilidad de la Columna", value=1.0,
                                                             key='compression_zz_stability')
    factor_compression_zz_format_conversion = st.number_input("Conversión de Formato", value=1.0,
                                                              key='compression_zz_format')
    factor_compression_zz_resistance_reduction = st.number_input("Reducción de Resistencia", value=1.0,
                                                                 key='compression_zz_resistance')
    factor_compression_zz_time_effect = st.number_input("Efecto del Tiempo", value=1.0, key='compression_zz_time')

    st.subheader("Ajuste a la Compresión Perpendicular")
    factor_compression_perp_moisture = st.number_input("Humedad", value=1.0, key='compression_perp_moisture')
    factor_compression_perp_temperature = st.number_input("Temperatura", value=1.0, key='compression_perp_temperature')
    factor_compression_perp_beam_stability = st.number_input("Estabilidad de la Viga", value=1.0,
                                                             key='compression_perp_stability')
    factor_compression_perp_size = st.number_input("Tamaño", value=1.0, key='compression_perp_size')
    factor_compression_perp_flat_use = st.number_input("Uso Plano", value=1.0, key='compression_perp_flat')
    factor_compression_perp_incising = st.number_input("Incisión", value=1.0, key='compression_perp_incising')
    factor_compression_perp_repetitive_member = st.number_input("Miembro Repetitivo", value=1.0,
                                                                key='compression_perp_repetitive')
    factor_compression_perp_column_stability = st.number_input("Estabilidad de la Columna", value=1.0,
                                                               key='compression_perp_column_stability')
    factor_compression_perp_buckling_stiffness = st.number_input("Rigidez al Pandeo", value=1.0,
                                                                 key='compression_perp_buckling')
    factor_compression_perp_bearing_area = st.number_input("Área de Apoyo", value=1.0, key='compression_perp_bearing')
    factor_compression_perp_format_conversion = st.number_input("Conversión de Formato", value=1.0,
                                                                key='compression_perp_format')
    factor_compression_perp_resistance_reduction = st.number_input("Reducción de Resistencia", value=1.0,
                                                                   key='compression_perp_resistance')
    factor_compression_perp_time_effect = st.number_input("Efecto del Tiempo", value=1.0, key='compression_perp_time')

    st.subheader("Ajuste del Módulo de Elasticidad")
    factor_elastic_moisture = st.number_input("Humedad", value=1.0, key='elastic_moisture')
    factor_elastic_temperature = st.number_input("Temperatura", value=1.0, key='elastic_temperature')
    factor_elastic_incising = st.number_input("Incisión", value=1.0, key='elastic_incising')
    factor_elastic_format_conversion = st.number_input("Conversión de Formato", value=1.0, key='elastic_format')

with main_tabs[2]:  # Fuerzas Tab
    st.subheader("Fuerzas Aplicadas")
    axial_force = st.number_input("Fuerza Axial (kgf)", value=0.0, key='axial_force')
    shear_y = st.number_input("Corte en Y (kgf)", value=0.0, key='shear_y')
    shear_z = st.number_input("Corte en Z (kgf)", value=0.0, key='shear_z')
    moment_xx = st.number_input("Momento en X-X (kgf*m)", value=0.0, key='moment_xx')
    moment_yy = st.number_input("Momento en Y-Y (kgf*m)", value=0.0, key='moment_yy')
    moment_zz = st.number_input("Momento en Z-Z (kgf*m)", value=0.0, key='moment_zz')

# --- Create Dataclass Instances ---
material = WoodMaterial(
    material_name, specific_gravity, fibre_saturation_point, tension_strength,
    bending_strength, shear_strength, compression_perpendicular_strength,
    compression_parallel_strength, elastic_modulus, color
)
section = RectangularSection(section_name, depth, width)
member = MemberDefinition(member_name, length, k_yy, k_zz)

tension_factors = TensionAdjustmentFactors(
    factor_tension_moisture, factor_tension_temperature, factor_tension_size,
    factor_tension_incising, factor_tension_format_conversion,
    factor_tension_resistance_reduction, factor_tension_time_effect
)

bending_factors_yy = BendingAdjustmentFactors(
    factor_bending_yy_moisture, factor_bending_yy_temperature, factor_bending_yy_beam_stability,
    factor_bending_yy_size, factor_bending_yy_flat_use, factor_bending_yy_incising,
    factor_bending_yy_repetitive_member, factor_bending_yy_format_conversion,
    factor_bending_yy_resistance_reduction, factor_bending_yy_time_effect
)

bending_factors_zz = BendingAdjustmentFactors(
    factor_bending_zz_moisture, factor_bending_zz_temperature, factor_bending_zz_beam_stability,
    factor_bending_zz_size, factor_bending_zz_flat_use, factor_bending_zz_incising,
    factor_bending_zz_repetitive_member, factor_bending_zz_format_conversion,
    factor_bending_zz_resistance_reduction, factor_bending_zz_time_effect
)

shear_factors = ShearAdjustmentFactors(
    factor_shear_moisture, factor_shear_temperature, factor_shear_incising,
    factor_shear_format_conversion, factor_shear_resistance_reduction,
    factor_shear_time_effect
)

compression_factors_yy = CompressionAdjustmentFactors(
    factor_compression_yy_moisture, factor_compression_yy_temperature,
    factor_compression_yy_size, factor_compression_yy_incising,
    factor_compression_yy_column_stability, factor_compression_yy_format_conversion,
    factor_compression_yy_resistance_reduction, factor_compression_yy_time_effect
)

compression_factors_zz = CompressionAdjustmentFactors(
    factor_compression_zz_moisture, factor_compression_zz_temperature,
    factor_compression_zz_size, factor_compression_zz_incising,
    factor_compression_zz_column_stability, factor_compression_zz_format_conversion,
    factor_compression_zz_resistance_reduction, factor_compression_zz_time_effect
)

compression_perp_factors = PerpendicularAdjustmentFactors(
    factor_compression_perp_moisture, factor_compression_perp_temperature,
    factor_compression_perp_beam_stability, factor_compression_perp_size,
    factor_compression_perp_flat_use, factor_compression_perp_incising,
    factor_compression_perp_repetitive_member,
    factor_compression_perp_column_stability,
    factor_compression_perp_buckling_stiffness, factor_compression_perp_bearing_area,
    factor_compression_perp_format_conversion,
    factor_compression_perp_resistance_reduction,
    factor_compression_perp_time_effect
)

elastic_modulus_factors = ElasticModulusAdjustmentFactors(
    factor_elastic_moisture, factor_elastic_temperature, factor_elastic_incising,
    factor_elastic_format_conversion
)

forces = Forces(
    axial_force, shear_y, shear_z, moment_xx, moment_yy, moment_zz
)

# Convert section dimensions from cm to m for calculations
section_properties = tc.RectangularSectionProperties(section.width / 100, section.depth / 100)

# Wood Element Calculator Instance
calculator = WoodElementCalculator(
    tension_factors, bending_factors_yy, bending_factors_zz, shear_factors,
    compression_factors_yy, compression_factors_zz, compression_perp_factors,
    elastic_modulus_factors, material, section_properties
)

# --- Cross-Section Visualization ---
st.header("Visualización de la Sección Transversal")

fig, ax = plt.subplots(figsize=(4, 2))
ax.set_xlim(0, section.width)
ax.set_ylim(0, section.depth)
ax.add_patch(plt.Rectangle((0, 0), section.width, section.depth, fc='burlywood', ec='black'))

# Add wood grain
num_lines = 50
grain_colors = ['darkgoldenrod', 'peru']
for j, grain_color in enumerate(grain_colors):
    for i in range(num_lines):
        y = np.linspace(0, section.depth, num_lines + 2)[i + 1]

        # Calculate start and end points for rotated line
        x0 = 0
        y0 = y
        x1 = section.width
        y1 = y

        angle_degrees = 5
        angle_radians = np.deg2rad(angle_degrees)

        # Rotate both end points
        x0_rotated = (x0 * np.cos(angle_radians) - y0 * np.sin(angle_radians))
        y0_rotated = (x0 * np.sin(angle_radians) + y0 * np.cos(angle_radians))

        x1_rotated = (x1 * np.cos(angle_radians) - y1 * np.sin(angle_radians))
        y1_rotated = (x1 * np.sin(angle_radians) + y1 * np.cos(angle_radians))

        # Calculate center
        center_x = section.width / 2
        center_y = section.depth / 2

        # Rotate around the center of the rectangle
        x0_rotated_center = 2 * (x0 - 2 * center_x) * np.cos(angle_radians) - 2 * (y0 - 2 * center_y) * np.sin(
            angle_radians) + center_x
        y0_rotated_center = 2 * (x0 - center_x) * np.sin(angle_radians) + 2 * (y0 - center_y) * np.cos(
            angle_radians) + center_y

        x1_rotated_center = 2 * (x1 - center_x) * np.cos(angle_radians) - 2 * (y1 - center_y) * np.sin(
            angle_radians) + center_x
        y1_rotated_center = 2 * (x1 - center_x) * np.sin(angle_radians) + 2 * (y1 - center_y) * np.cos(
            angle_radians) + center_y

        # Offset the lines slightly to avoid overlap
        offset = (j * 2)  # Adjust the offset as needed

        ax.plot([x0_rotated_center + offset, x1_rotated_center + offset],
                [y0_rotated_center + offset, y1_rotated_center + offset], color=grain_color,
                linewidth=0.25)

ax.set_aspect('equal', adjustable='box')
ax.set_xlabel("Ancho (cm)")
ax.set_ylabel("Altura (cm)")
ax.set_title("Sección")
st.pyplot(fig)

# --- Results ---
st.header("Resultados")
try:
    st.write(f"Resistencia a la Tracción: {calculator.section_tension_strength():.2f} kgf")
    st.write(f"Resistencia a la Flexión (yy): {calculator.section_bending_strength('yy'):.2f} kgf*m")
    st.write(f"Resistencia a la Flexión (zz): {calculator.section_bending_strength('zz'):.2f} kgf*m")
    st.write(f"Resistencia al Corte: {calculator.section_shear_strength():.2f} kgf")
    st.write(f"Resistencia a la Compresión (yy): {calculator.section_compression_strength('yy'):.2f} kgf")
    st.write(f"Resistencia a la Compresión (zz): {calculator.section_compression_strength('zz'):.2f} kgf")
    st.write(f"Resistencia a la Compresión Perpendicular: {calculator.section_compression_perp_strength():.2f} kgf")

except (ZeroDivisionError, TypeError, ValueError) as e:
    st.error(f"Error en el cálculo: {e}")
