========================================================================
TPMS Builder - Installation & User Guide
========================================================================

Author: Esteban Barreiro (Developed with assistance from Google Gemini)
Version: 1.2.0
Compatibility: Blender 5.2 LTS (or higher)

------------------------------------------------------------------------
GENERAL DESCRIPTION
------------------------------------------------------------------------
TPMS Builder is a custom procedural tool designed to generate complex 
geometric lattices and Triply Periodic Minimal Surfaces (TPMS). It enables 
automatic wrapping and fitting of 100% manifold structures onto any active 
3D target mesh, optimized for additive manufacturing and 3D printing.

This add-on was created inspired by Matthew Shomper's open-source work on 
fields (f13lds) and his procedural methodology within Blender.

------------------------------------------------------------------------
PREREQUISITES
------------------------------------------------------------------------
1. Blender 5.2 LTS (or higher).
2. 'scikit-image' library installed within Blender's Python environment 
   (required for the Marching Cubes algorithm in TPMS structures).

------------------------------------------------------------------------
INSTALLATION INSTRUCTIONS
------------------------------------------------------------------------
1. Download the add-on `.zip` package.
2. Open Blender and go to Edit > Preferences > Add-ons.
3. Click the 'Install...' button (or upper dropdown menu in recent versions) 
   and select the downloaded `.zip` file.
4. Enable the checkbox next to "Add Mesh: F13LD TPMS Builder".
5. Open the 3D Viewport and press the 'N' key to expand the Sidebar. 
   You will find the interface under the 'F13LD TPMS' tab.

------------------------------------------------------------------------
CORE FEATURES
------------------------------------------------------------------------
* Dual-Engine Architecture:
  - BCC (Body-Centered Cubic): Pure geometric strut lattice generation 
    using Skin and Subsurf modifiers.
  - Volumetric TPMS: Scalar field generation for Gyroid, Schwarz Primitive, 
    and Schwarz Diamond iso-surfaces.

* Adaptive Radial Gyroid:
  Cylindrical coordinate transformation centered dynamically at the active 
  object's origin, allowing lattices to naturally conform to curved geometries.

* Procedural Porosity Gradient:
  Continuous modulation of strut radius and wall thickness along the Z-axis 
  (top-to-bottom) for precise weight and strength tuning.

* Preview / LOD Mode:
  Low-resolution draft system for ultra-fast parameter iteration before 
  executing final high-density calculations.

* Boolean Solver Selector:
  Switch between 'Float' (Fast / Reliable, ideal for Skin meshes) and 
  'Exact' (Precise) directly from the UI panel.

------------------------------------------------------------------------
USAGE NOTES
------------------------------------------------------------------------
- Always select an active MESH object prior to hitting "Generate Structure".
- For complex geometry or Skin-derived meshes (BCC), keeping the Boolean 
  Solver set to 'Float' is highly recommended to avoid calculation failures.
- Toggle the 'Boolean Algorithm' between 'Manifold/Exact' if necessary.
- Adjust your object's pivot point (origin) to change the center point of the 
  radial pattern when using 'Gyroid Radial'.
========================================================================