# wood_design
A Streamlit app for structural timber design according to the NDS (National Design Specification), powered by the `timber_nds` Python package.

## Limitations

This app has several limitations that users should be aware of:

**Member Geometry:** Currently, this app only supports the analysis of rectangular timber members. Once the geometry of a member or section has been included, it cannot be removed.

* **Combined Compression:** The app does not check net compression stresses in members under combined bending and tension.

* **Geometric Modifications:** The app assumes members are solid, without holes, notches, or other geometric modifications (except incisions, if applicable). Users must account for such modifications.

* **Bearing:** The app does not explicitly check for bearing stresses from horizontal forces. Shear force is used as an approximation of support reaction; users should verify this assumption and apply corrections as needed.

* **Second-Order Effects:** The app does not include second-order effects in compression-bending calculations.

* **Buckling:** Users are responsible for including buckling effects through appropriate adjustment factors.

* **Units:** Input and output values are in centimeters (cm) for length and kilograms-force (kgf) for force.

## Important Notes
* **Local Axes:** `x` is longitudinal, `y` is horizontal within the cross-section, and `z` is vertical within the cross-section.

* **Global Axes:** `x` and `y` are horizontal, and `z` is vertical.

* **User Responsibility:** Due to these limitations, users must understand the app's assumptions and verify all output for suitability in their structural design.

* **Future Improvements:** We are actively working to improve the app and address these limitations in future updates.

## How to Use
**Example:** Simply navigate using the app's sidebar and provide the requested information. The default parameters and the provided example CSV file (columns.csv) can be used to execute an example of the app workflow.

## License
This app and the underlying `timber_nds` package are licensed under the [MIT License].

