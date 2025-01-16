import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Union, Literal
import numpy as np
import os
import operator
from timber_nds.design import (
    check_for_all_elements,
    filter_and_export_results,
    WoodElementCalculator
)
from timber_nds.calculation import (
    RectangularSectionProperties,
    import_robot_bar_forces,
    create_robot_bar_forces_as_objects,
)

from timber_nds.settings import (
    WoodMaterial,
    RectangularSection,
    MemberDefinition,
    Forces,
    TensionAdjustmentFactors,
    BendingAdjustmentFactors,
    ShearAdjustmentFactors,
    CompressionAdjustmentFactors,
    PerpendicularAdjustmentFactors,
    ElasticModulusAdjustmentFactors,
)


def plot_rectangular_section(section: RectangularSection, color: str):
    if not isinstance(section, RectangularSection):
        raise TypeError("The section argument must be a RectangularSection object.")
    if section.depth <= 0 or section.width <= 0:
        raise ValueError("Section dimensions must be positive values.")

    fig, ax = plt.subplots()
    rect = patches.Rectangle((0, 0), section.width, section.depth, linewidth=1, edgecolor="black", facecolor=color)
    ax.add_patch(rect)

    ax.set_xlim(-0.1 * section.width, 1.1 * section.width)
    ax.set_ylim(-0.1 * section.depth, 1.1 * section.depth)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Width")
    ax.set_ylabel("Depth")
    ax.set_title(f"Rectangular Section: {section.name}")

    st.pyplot(fig)


def main():
    st.sidebar.header("Wood Elements Design")

    if "material" not in st.session_state:
        st.session_state.material = None
    if "sections" not in st.session_state:
        st.session_state.sections = []
    if "elements" not in st.session_state:
        st.session_state.elements = []
    if "forces_data" not in st.session_state:
        st.session_state.forces_data = []
    if "results_df" not in st.session_state:
        st.session_state.results_df = pd.DataFrame()
    if "adjustment_factors" not in st.session_state:
        st.session_state.adjustment_factors = {
            "tension": TensionAdjustmentFactors(),
            "bending_yy": BendingAdjustmentFactors(),
            "bending_zz": BendingAdjustmentFactors(),
            "shear": ShearAdjustmentFactors(),
            "compression_yy": CompressionAdjustmentFactors(),
            "compression_zz": CompressionAdjustmentFactors(),
            "compression_perp": PerpendicularAdjustmentFactors(),
            "elastic_modulus": ElasticModulusAdjustmentFactors(),
        }
    if "saved_factors" not in st.session_state:
        st.session_state.saved_factors = {
            "tension": None,
            "bending_yy": None,
            "bending_zz": None,
            "shear": None,
            "compression_yy": None,
            "compression_zz": None,
            "compression_perp": None,
            "elastic_modulus": None,
        }
    if "uploaded_file_path" not in st.session_state:
        st.session_state.uploaded_file_path = None

    tabs = ["Element", "Adjustment Factors", "Forces", "Calculate", "Download"]
    selected_tab = st.sidebar.radio("Select Tab", tabs)

    if selected_tab == "Element":
        st.sidebar.subheader("Material")
        material_name = st.sidebar.text_input("Material Name", "Teca G1")
        specific_gravity = st.sidebar.number_input("Specific Gravity", 0.1, 1.0, 0.58)
        fibre_saturation_point = st.sidebar.number_input("Fiber Saturation Point (%)", 0.1, 50.0, 30.0)
        tension_strength = st.sidebar.number_input("Tension Strength (kgf/cm2)", 0.1, 1000.0, 84.0)
        bending_strength = st.sidebar.number_input("Bending Strength (kgf/cm2)", 0.1, 1000.0, 212.0)
        shear_strength = st.sidebar.number_input("Shear Strength (kgf/cm2)", 0.1, 500.0, 94.9)
        compression_parallel_strength = st.sidebar.number_input("Compression Parallel Strength (kgf/cm2)", 0.1,
                                                                500.0, 81.4)
        compression_perpendicular_strength = st.sidebar.number_input(
            "Compression Perpendicular Strength (kgf/cm2)", 0.1, 500.0, 8.54
        )
        elastic_modulus = st.sidebar.number_input("Elastic Modulus (kgf/cm2)", 0.1, 500000.0, 127000.0)
        color = st.sidebar.color_picker("Material Color", "#8B4513")

        if st.sidebar.button("Save Material"):
            wood_material = WoodMaterial(
                name=material_name,
                specific_gravity=specific_gravity,
                fibre_saturation_point=fibre_saturation_point,
                tension_strength=tension_strength,
                bending_strength=bending_strength,
                shear_strength=shear_strength,
                compression_perpendicular_strength=compression_perpendicular_strength,
                compression_parallel_strength=compression_parallel_strength,
                elastic_modulus=elastic_modulus,
                color=color,
            )
            st.session_state.material = wood_material
            st.sidebar.success(f"Material '{material_name}' saved!")

        if st.session_state.material:
            st.sidebar.subheader("Current Material:")
            st.sidebar.text(f"- Name: {st.session_state.material.name}")

        st.sidebar.subheader("Section")
        section_name = st.sidebar.text_input("Section Name", "3 x 3")
        width = st.sidebar.number_input("Width (cm)", 1.0, 500.0, 6.4)
        depth = st.sidebar.number_input("Depth (cm)", 1.0, 500.0, 6.4)

        if st.sidebar.button("Add Section"):
            rectangular_section = RectangularSection(name=section_name, depth=depth, width=width)
            st.session_state.sections.append(rectangular_section)
            st.sidebar.success(f"Section '{section_name}' added!")

        st.sidebar.subheader("Added Sections:")
        for section in st.session_state.sections:
            st.sidebar.text(f"- {section.name} (Depth: {section.depth} cm, Width: {section.width} cm)")

        st.header("Rectangular Section Visualization")
        if st.session_state.sections and st.session_state.material:
            plot_rectangular_section(st.session_state.sections[-1], st.session_state.material.color)

        st.sidebar.subheader("Element")
        element_name = st.sidebar.text_input("Element Name", "Column 1")
        length = st.sidebar.number_input("Length (cm)", 10.0, 1000.0, 300.0)
        effective_length_factor_yy = st.sidebar.number_input("Effective Length Factor YY", 0.1, 2.0, 1.0)
        effective_length_factor_zz = st.sidebar.number_input("Effective Length Factor ZZ", 0.1, 2.0, 1.0)

        member_definition = MemberDefinition(
            name=element_name,
            length=length,
            effective_length_factor_yy=effective_length_factor_yy,
            effective_length_factor_zz=effective_length_factor_zz,
        )

        if st.sidebar.button("Add Element"):
            st.session_state.elements.append(member_definition)
            st.sidebar.success(f"Element '{element_name}' added!")

        st.sidebar.subheader("Added Elements:")
        for element in st.session_state.elements:
            st.sidebar.text(f"- {element.name} (Length: {element.length} cm)")

    elif selected_tab == "Adjustment Factors":
        st.sidebar.subheader("Adjustment Factors")

        factor_types = [
            "tension", "bending_yy", "bending_zz", "shear",
            "compression_yy", "compression_zz", "compression_perp", "elastic_modulus"
        ]

        default_factors = {
            "tension": {
                "due_moisture": 1.0,
                "due_temperature": 1.0,
                "due_size": 1.0,
                "due_incising": 1.0,
                "due_format_conversion": 2.70,
                "due_resistance_reduction": 0.80,
                "due_time_effect": 1.0
            },
            "bending_yy": {
                "due_moisture": 1.0,
                "due_temperature": 1.0,
                "due_beam_stability": 1.0,
                "due_size": 1.0,
                "due_flat_use": 1.0,
                "due_incising": 1.0,
                "due_repetitive_member": 1.0,
                "due_format_conversion": 2.54,
                "due_resistance_reduction": 0.85,
                "due_time_effect": 1.0
            },
            "bending_zz": {
                "due_moisture": 1.0,
                "due_temperature": 1.0,
                "due_beam_stability": 1.0,
                "due_size": 1.0,
                "due_flat_use": 1.0,
                "due_incising": 1.0,
                "due_repetitive_member": 1.0,
                "due_format_conversion": 2.54,
                "due_resistance_reduction": 0.85,
                "due_time_effect": 1.0
            },
            "shear": {
                "due_moisture": 1.0,
                "due_temperature": 1.0,
                "due_incising": 1.0,
                "due_format_conversion": 2.88,
                "due_resistance_reduction": 0.75,
                "due_time_effect": 1.0
            },
            "compression_yy": {
                "due_moisture": 1.0,
                "due_temperature": 1.0,
                "due_size": 1.0,
                "due_incising": 1.0,
                "due_column_stability": 1.0,
                "due_format_conversion": 2.40,
                "due_resistance_reduction": 0.90,
                "due_time_effect": 1.0
            },
            "compression_zz": {
                "due_moisture": 1.0,
                "due_temperature": 1.0,
                "due_size": 1.0,
                "due_incising": 1.0,
                "due_column_stability": 1.0,
                "due_format_conversion": 2.40,
                "due_resistance_reduction": 0.90,
                "due_time_effect": 1.0
            },
            "compression_perp": {
                "due_moisture": 1.0,
                "due_temperature": 1.0,
                "due_incising": 1.0,
                "due_bearing_area": 1.0,
                "due_format_conversion": 1.67,
                "due_resistance_reduction": 0.90,
                "due_time_effect": 1.0
            },
            "elastic_modulus": {
                "due_moisture": 1.0,
                "due_temperature": 1.0,
                "due_incising": 1.0,
                "due_format_conversion": 1.76,
                "due_resistance_reduction": 0.85
            },
        }

        for factor_type in factor_types:
            st.sidebar.write(f"{factor_type.replace('_', ' ').title()}:")
            if st.session_state.saved_factors[factor_type]:
                for field in st.session_state.saved_factors[factor_type].__dataclass_fields__:
                    default_value = getattr(st.session_state.saved_factors[factor_type], field)
                    setattr(
                        st.session_state.adjustment_factors[factor_type],
                        field,
                        st.sidebar.number_input(f"{field.replace('_', ' ').title()}", value=default_value,
                                                key=f"{factor_type}_{field}")
                    )
            else:
                for field in st.session_state.adjustment_factors[factor_type].__dataclass_fields__:
                    default_value = default_factors[factor_type].get(field, 1.0)
                    setattr(
                        st.session_state.adjustment_factors[factor_type],
                        field,
                        st.sidebar.number_input(f"{field.replace('_', ' ').title()}", value=default_value,
                                                key=f"{factor_type}_{field}")
                    )

        if st.sidebar.button("Save Adjustment Factors"):
            for factor_type in factor_types:
                st.session_state.saved_factors[factor_type] = st.session_state.adjustment_factors[factor_type]
            st.sidebar.success("Adjustment factors saved!")

    elif selected_tab == "Forces":
        st.sidebar.subheader("Forces")
        uploaded_file = st.sidebar.file_uploader("Upload Forces CSV", type=["csv"])
        if uploaded_file is not None:
            try:
                st.session_state.uploaded_file_path = uploaded_file.name
                df = import_robot_bar_forces(uploaded_file)
                if df is not None:
                    forces_list = create_robot_bar_forces_as_objects(df)
                    st.session_state.forces_data = forces_list
                    st.sidebar.success("Forces loaded from CSV!")
                else:
                    st.sidebar.error(
                        "Error loading forces from CSV. Please check the file format.")
            except Exception as e:
                st.sidebar.error(f"Error loading CSV: {e}")

        st.sidebar.subheader("Loaded Forces:")
        if st.session_state.forces_data:
            for forces in st.session_state.forces_data:
                st.sidebar.text(
                    f"- Name: {forces.name}, Axial: {forces.axial}, Shear Y: {forces.shear_y}, Shear Z: {forces.shear_z}, Moment XX: {forces.moment_xx}, Moment YY: {forces.moment_yy}, Moment ZZ: {forces.moment_zz}"
                )

    elif selected_tab == "Calculate":
        st.header("Results")
        st.subheader("Complete results")

        if st.sidebar.button("Calculate"):
            st.write("")

            if not st.session_state.material:
                st.error("Please define a material before continuing.")
            elif 'forces_data' in st.session_state and st.session_state.forces_data and 'elements' in st.session_state and st.session_state.elements and 'sections' in st.session_state and st.session_state.sections:
                tension_factors = st.session_state.adjustment_factors["tension"]
                bending_factors_yy = st.session_state.adjustment_factors["bending_yy"]
                bending_factors_zz = st.session_state.adjustment_factors["bending_zz"]
                shear_factors = st.session_state.adjustment_factors["shear"]
                compression_factors_yy = st.session_state.adjustment_factors["compression_yy"]
                compression_factors_zz = st.session_state.adjustment_factors["compression_zz"]
                compression_perp_factors = st.session_state.adjustment_factors["compression_perp"]
                elastic_modulus_factors = st.session_state.adjustment_factors["elastic_modulus"]

                try:
                    st.session_state.results_df = check_for_all_elements(
                        list_sections=st.session_state.sections,
                        list_elements=st.session_state.elements,
                        list_forces=st.session_state.forces_data,
                        material=st.session_state.material,
                        tension_factors=tension_factors,
                        bending_factors_yy=bending_factors_yy,
                        bending_factors_zz=bending_factors_zz,
                        shear_factors=shear_factors,
                        compression_factors_yy=compression_factors_yy,
                        compression_factors_zz=compression_factors_zz,
                        compression_perp_factors=compression_perp_factors,
                        elastic_modulus_factors=elastic_modulus_factors,
                    )
                    st.write("", st.session_state.results_df)
                except Exception as e:
                    st.error(f"An error occurred during calculation: {e}")
            else:
                st.error("Please ensure forces, elements, and sections are defined.")

        if not st.session_state.results_df.empty:
            st.subheader("Filtered Results")
            forces_tab, strength_tab, dcr_tab = st.tabs(["Forces", "Strength", "DCR"])

            with forces_tab:
                st.subheader("Forces Data")
                df = pd.DataFrame(st.session_state.forces_data)
                if not df.empty:
                    df.insert(0, 'force', df['name'])
                    dcr_max_values = []
                    for index, row in st.session_state.results_df.iterrows():
                        dcr_max_value = max(row.get(key, 0) for key in [
                            "tension (dcr)", "biaxial bending (dcr)",
                            "shear y (dcr)", "shear z (dcr)",
                            "compression (dcr)", "bending and compression (dcr)"
                        ])
                        dcr_max_values.append(dcr_max_value)

                    df['dcr_max'] = dcr_max_values
                    st.dataframe(
                        df[["force", "dcr_max", "axial", "shear_y", "shear_z", "moment_xx", "moment_yy", "moment_zz"]])

            with strength_tab:
                st.subheader("Section Strength")

                all_capacities = []
                for index, row in st.session_state.results_df.iterrows():

                    element = next((element for element in st.session_state.elements if element.name == row['member']),
                                   None)
                    section = next((section for section in st.session_state.sections if section.name == row['section']),
                                   None)
                    force = next((force for force in st.session_state.forces_data if force.name == row['force']), None)
                    material = st.session_state.material

                    if element and section and force and material:
                        section_properties = RectangularSectionProperties(width=section.width, depth=section.depth)

                        wood_calculator = WoodElementCalculator(
                            tension_factors=st.session_state.adjustment_factors["tension"],
                            bending_factors_yy=st.session_state.adjustment_factors["bending_yy"],
                            bending_factors_zz=st.session_state.adjustment_factors["bending_zz"],
                            shear_factors=st.session_state.adjustment_factors["shear"],
                            compression_factors_yy=st.session_state.adjustment_factors["compression_yy"],
                            compression_factors_zz=st.session_state.adjustment_factors["compression_zz"],
                            compression_perp_factors=st.session_state.adjustment_factors["compression_perp"],
                            elastic_modulus_factors=st.session_state.adjustment_factors["elastic_modulus"],
                            material_properties=material,
                            section_properties=section_properties,
                        )

                        tension_capacity = wood_calculator.tension_strength()
                        bending_capacity_yy = wood_calculator.bending_strength("yy")
                        bending_capacity_zz = wood_calculator.bending_strength("zz")
                        shear_capacity = wood_calculator.shear_strength()
                        compression_capacity_yy = wood_calculator.compression_strength("yy")
                        compression_capacity_zz = wood_calculator.compression_strength("zz")
                        compression_perp_capacity = wood_calculator.compression_perp_strength()

                        dcr_max_value = max(row.get(key, 0) for key in [
                            "tension (dcr)", "biaxial bending (dcr)",
                            "shear y (dcr)", "shear z (dcr)",
                            "compression (dcr)", "bending and compression (dcr)"
                        ])

                        capacity_data = {
                            "member": row["member"],
                            "section": row["section"],
                            "force": row["force"],
                            "tension_capacity": tension_capacity,
                            "bending_yy_capacity": bending_capacity_yy,
                            "bending_zz_capacity": bending_capacity_zz,
                            "shear_capacity": shear_capacity,
                            "compression_yy_capacity": compression_capacity_yy,
                            "compression_zz_capacity": compression_capacity_zz,
                            "compression_perp_capacity": compression_perp_capacity,
                            "dcr_max": dcr_max_value
                        }
                        all_capacities.append(capacity_data)

                capacities_df = pd.DataFrame(all_capacities)
                if not capacities_df.empty:
                    st.dataframe(capacities_df[["member", "section", "force", "dcr_max", "tension_capacity",
                                                "bending_yy_capacity", "bending_zz_capacity", "shear_capacity",
                                                "compression_yy_capacity", "compression_zz_capacity"]])

            with dcr_tab:
                st.subheader("Demand-Capacity Ratio (DCR)")
                dcr_columns = ["member", "section", "force"] + [col for col in st.session_state.results_df.columns if
                                                                "(dcr)" in col]
                df = st.session_state.results_df[dcr_columns]
                if not df.empty:
                    dcr_max_values = []
                    for index, row in st.session_state.results_df.iterrows():
                        dcr_max_value = max(row.get(key, 0) for key in [
                            "tension (dcr)", "shear y (dcr)", "shear z (dcr)",
                            "compression (dcr)", "biaxial bending (dcr)", "bending and compression (dcr)"
                        ])
                        dcr_max_values.append(dcr_max_value)

                    df['dcr_max'] = dcr_max_values

                    columns_to_display = ["member", "section", "force", "dcr_max"]

                    for col in df.columns:
                        if "(dcr)" in col and "compression perpendicular (dcr)" not in col:
                            columns_to_display.append(col)

                    st.dataframe(df[columns_to_display])
        else:
            st.write("No calculation results available.")

        if st.session_state.material:
            st.subheader("Input data")
            with st.expander("Press to check input data", expanded=False):
                st.subheader("Material")
                st.write(f"**Name:** {st.session_state.material.name}")
                st.write(f"**Specific Gravity:** {st.session_state.material.specific_gravity}")
                st.write(f"**Fiber Saturation Point:** {st.session_state.material.fibre_saturation_point}%")
                st.write(f"**Tension Strength:** {st.session_state.material.tension_strength} kgf/cm2")
                st.write(f"**Bending Strength:** {st.session_state.material.bending_strength} kgf/cm2")
                st.write(f"**Shear Strength:** {st.session_state.material.shear_strength} kgf/cm2")
                st.write(
                    f"**Compression Parallel Strength:** {st.session_state.material.compression_parallel_strength} kgf/cm2")
                st.write(
                    f"**Compression Perpendicular Strength:** {st.session_state.material.compression_perpendicular_strength} kgf/cm2")
                st.write(f"**Elastic Modulus:** {st.session_state.material.elastic_modulus} kgf/cm2")

                st.subheader("Adjustment Factors")
                for factor_type, factors in st.session_state.adjustment_factors.items():
                    st.write(f"**{factor_type.replace('_', ' ').title()}:**")
                    for field in factors.__dataclass_fields__:
                        value = getattr(factors, field)
                        st.write(f"- {field.replace('_', ' ').title()}: {value}")

                st.subheader("Sections")
                for section in st.session_state.sections:
                    st.write(f"- **{section.name}:** Depth: {section.depth} cm, Width: {section.width} cm")

                st.subheader("Elements")
                for element in st.session_state.elements:
                    st.write(f"- **{element.name}:** Length: {element.length} cm")

    elif selected_tab == "Download":
        if not st.session_state.results_df.empty:
            st.download_button(
                label="Download Results as CSV",
                data=st.session_state.results_df.to_csv(index=False, sep=';').encode('utf-8'),
                file_name="results.csv",
                mime="text/csv",
            )
        else:
            st.write("No results available to download.")


if __name__ == "__main__":
    main()
