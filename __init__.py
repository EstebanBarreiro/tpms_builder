import sys
import os
import bpy
import mathutils
import numpy as np

# Intentar importar skimage.measure
try:
    from skimage import measure
except ImportError:
    user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
    if user_site not in sys.path:
        sys.path.append(user_site)
    try:
        from skimage import measure
    except ImportError:
        measure = None

# ------------------------------------------------------------------------
# Generador Geométrico BCC
# ------------------------------------------------------------------------
def generate_bcc_geometric_mesh(bounds_min, bounds_max, k_freq):
    dx = bounds_max[0] - bounds_min[0]
    dy = bounds_max[1] - bounds_min[1]
    dz = bounds_max[2] - bounds_min[2]
    
    nx = max(2, int(k_freq * (dx / max(dx, dy, dz)) * 4))
    ny = max(2, int(k_freq * (dy / max(dx, dy, dz)) * 4))
    nz = max(2, int(k_freq * (dz / max(dx, dy, dz)) * 4))

    x_vals = np.linspace(bounds_min[0], bounds_max[0], nx)
    y_vals = np.linspace(bounds_min[1], bounds_max[1], ny)
    z_vals = np.linspace(bounds_min[2], bounds_max[2], nz)

    vertices = []
    edges = []
    vert_map = {}

    def get_or_add_vert(coord):
        key = (round(coord[0], 4), round(coord[1], 4), round(coord[2], 4))
        if key not in vert_map:
            vert_map[key] = len(vertices)
            vertices.append(coord)
        return vert_map[key]

    for i in range(nx - 1):
        for j in range(ny - 1):
            for k in range(nz - 1):
                p000 = (x_vals[i], y_vals[j], z_vals[k])
                p100 = (x_vals[i+1], y_vals[j], z_vals[k])
                p010 = (x_vals[i], y_vals[j+1], z_vals[k])
                p110 = (x_vals[i+1], y_vals[j+1], z_vals[k])
                p001 = (x_vals[i], y_vals[j], z_vals[k+1])
                p101 = (x_vals[i+1], y_vals[j], z_vals[k+1])
                p011 = (x_vals[i], y_vals[j+1], z_vals[k+1])
                p111 = (x_vals[i+1], y_vals[j+1], z_vals[k+1])

                center = (
                    (x_vals[i] + x_vals[i+1]) / 2.0,
                    (y_vals[j] + y_vals[j+1]) / 2.0,
                    (z_vals[k] + z_vals[k+1]) / 2.0
                )

                idx_c = get_or_add_vert(center)
                corners = [p000, p100, p010, p110, p001, p101, p011, p111]

                for corner in corners:
                    idx_corner = get_or_add_vert(corner)
                    edges.append((idx_c, idx_corner))

    return vertices, edges

# ------------------------------------------------------------------------
# Generación TPMS Tradicional
# ------------------------------------------------------------------------
def generate_tpms_surface(tpms_type, resolution, thickness, k_freq, n_sectors, gradient_factor, bounds_min, bounds_max, obj_origin):
    if measure is None:
        raise ImportError("La librería 'scikit-image' no está instalada.")

    res = resolution
    x = np.linspace(bounds_min[0], bounds_max[0], res)
    y = np.linspace(bounds_min[1], bounds_max[1], res)
    z = np.linspace(bounds_min[2], bounds_max[2], res)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    z_min, z_max = bounds_min[2], bounds_max[2]
    z_norm = (z_max - Z) / (z_max - z_min + 1e-6)
    effective_thickness = thickness * (1.0 + gradient_factor * (z_norm - 0.5))
    effective_thickness = np.maximum(effective_thickness, 0.005)

    if tpms_type == 'GYROID':
        X_c = X - obj_origin[0]
        Y_c = Y - obj_origin[1]
        R = np.sqrt(X_c**2 + Y_c**2)
        THETA = np.arctan2(Y_c, X_c)

        F = (np.sin(k_freq * R) * np.cos(n_sectors * THETA) + 
             np.sin(n_sectors * THETA) * np.cos(k_freq * Z) + 
             np.sin(k_freq * Z) * np.cos(k_freq * R))

    elif tpms_type == 'PRIMITIVE':
        F = np.cos(k_freq * X) + np.cos(k_freq * Y) + np.cos(k_freq * Z)

    elif tpms_type == 'DIAMOND':
        F = (np.cos(k_freq * X) * np.cos(k_freq * Y) * np.cos(k_freq * Z) - 
             np.sin(k_freq * X) * np.sin(k_freq * Y) * np.sin(k_freq * Z))

    volume = np.abs(F) - effective_thickness
    padded_volume = np.pad(volume, pad_width=1, mode='constant', constant_values=1.0)
    
    verts, faces, normals, values = measure.marching_cubes(padded_volume, level=0.0)
    verts -= 1.0

    verts_scaled = np.zeros_like(verts)
    verts_scaled[:, 0] = bounds_min[0] + (verts[:, 0] / (res - 1)) * (bounds_max[0] - bounds_min[0])
    verts_scaled[:, 1] = bounds_min[1] + (verts[:, 1] / (res - 1)) * (bounds_max[1] - bounds_min[1])
    verts_scaled[:, 2] = bounds_min[2] + (verts[:, 2] / (res - 1)) * (bounds_max[2] - bounds_min[2])

    return verts_scaled.tolist(), faces.tolist()

# ------------------------------------------------------------------------
# Operador Principal
# ------------------------------------------------------------------------
class MESH_OT_generate_tpms_bounded(bpy.types.Operator):
    """Genera la estructura seleccionada aplicando la pila completa de modificadores"""
    bl_idname = "mesh.generate_tpms_bounded"
    bl_label = "Generar Estructura Manifold"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.tpms_builder_props
        target_obj = context.active_object

        if not target_obj or target_obj.type != 'MESH':
            self.report({'ERROR'}, "Selecciona un objeto 3D activo.")
            return {'CANCELLED'}

        bbox = [target_obj.matrix_world @ mathutils.Vector(corner) for corner in target_obj.bound_box]
        bounds_min = [min([v[i] for v in bbox]) for i in range(3)]
        bounds_max = [max([v[i] for v in bbox]) for i in range(3)]
        obj_origin = target_obj.location

        try:
            if props.tpms_type == 'BCC_STRUT':
                effective_k = props.preview_k_freq if props.use_preview_mode else props.k_freq
                
                verts, edges = generate_bcc_geometric_mesh(bounds_min, bounds_max, effective_k)
                mesh = bpy.data.meshes.new(f"BCC_Wire_{target_obj.name}")
                tpms_obj = bpy.data.objects.new(mesh.name, mesh)
                context.collection.objects.link(tpms_obj)
                mesh.from_pydata(verts, edges, [])
                mesh.update()

                skin_mod = tpms_obj.modifiers.new(name="TPMS_Strut_Volume", type='SKIN')
                subsurf_mod = tpms_obj.modifiers.new(name="TPMS_Smooth", type='SUBSURF')
                subsurf_mod.levels = 1

                bool_mod = tpms_obj.modifiers.new(name="TPMS_Containment", type='BOOLEAN')
                bool_mod.operation = 'INTERSECT'
                bool_mod.object = target_obj
                bool_mod.solver = props.boolean_solver

                context.view_layer.update()

                z_min, z_max = bounds_min[2], bounds_max[2]
                z_range = z_max - z_min + 1e-6

                if mesh.skin_vertices:
                    skin_layer = mesh.skin_vertices[0].data
                    for v in mesh.vertices:
                        z_norm = (z_max - v.co.z) / z_range
                        eff_radius = props.thickness * (1.0 + props.gradient_factor * (z_norm - 0.5))
                        eff_radius = max(eff_radius, 0.005)
                        skin_layer[v.index].radius = (eff_radius, eff_radius)

            else:
                actual_res = props.preview_resolution if props.use_preview_mode else props.resolution
                verts, faces = generate_tpms_surface(
                    props.tpms_type, actual_res, props.thickness, 
                    props.k_freq, props.n_sectors, props.gradient_factor,
                    bounds_min, bounds_max, obj_origin
                )
                mesh = bpy.data.meshes.new(f"{props.tpms_type}_{target_obj.name}")
                tpms_obj = bpy.data.objects.new(mesh.name, mesh)
                context.collection.objects.link(tpms_obj)
                mesh.from_pydata(verts, [], faces)
                mesh.update()

                bool_mod = tpms_obj.modifiers.new(name="TPMS_Containment", type='BOOLEAN')
                bool_mod.operation = 'INTERSECT'
                bool_mod.object = target_obj
                bool_mod.solver = props.boolean_solver

            for o in context.selected_objects:
                o.select_set(False)
            
            tpms_obj.select_set(True)
            context.view_layer.objects.active = tpms_obj

            self.report({'INFO'}, f"Estructura {props.tpms_type} generada correctamente con Solver {props.boolean_solver}.")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error al generar la estructura: {str(e)}")
            return {'CANCELLED'}

# ------------------------------------------------------------------------
# Propiedades y Panel UI
# ------------------------------------------------------------------------
class TPMSBuilderProperties(bpy.types.PropertyGroup):
    tpms_type: bpy.props.EnumProperty(
        name="Estructura / Patrón",
        description="Selecciona la geometría base",
        items=[
            ('BCC_STRUT', "Body-Centered Cubic (BCC)", "Estructura de puntales geométricos cilíndricos continuos"),
            ('GYROID', "Gyroid Radial", "Superficie mínima Gyroid en coordenadas cilíndricas"),
            ('PRIMITIVE', "Schwarz Primitive", "Superficie mínima Schwarz Primitive cartesiana"),
            ('DIAMOND', "Schwarz Diamond", "Superficie mínima Schwarz Diamond cartesiana"),
        ],
        default='BCC_STRUT'
    )
    boolean_solver: bpy.props.EnumProperty(
        name="Algoritmo Booleano",
        description="Solver utilizado para el corte con el contenedor (Float es más rápido en Blender 5.2)",
        items=[
            ('FLOAT', "Float (Rápido / Estable)", "Solucionador rápido ideal para mallas complejas"),
            ('EXACT', "Exact (Preciso)", "Solucionador estricto para geometrías simples"),
        ],
        default='FLOAT'
    )
    use_preview_mode: bpy.props.BoolProperty(
        name="Modo Previsualización (LOD)",
        description="Reduce la densidad/resolución para trabajar rápido antes de la versión final",
        default=False
    )
    preview_k_freq: bpy.props.FloatProperty(
        name="Densidad LOD (BCC)",
        default=1.5, min=0.5, max=5.0
    )
    preview_resolution: bpy.props.IntProperty(
        name="Res. Previsualización (TPMS)",
        default=32, min=16, max=64
    )
    resolution: bpy.props.IntProperty(
        name="Resolución Final",
        default=80, min=20, max=250
    )
    thickness: bpy.props.FloatProperty(
        name="Radio / Grosor Base",
        default=0.08, min=0.005, max=0.5, precision=3
    )
    k_freq: bpy.props.FloatProperty(
        name="Frecuencia / Densidad (k)",
        default=3.0, min=0.5, max=15.0
    )
    gradient_factor: bpy.props.FloatProperty(
        name="Gradiente de Porosidad",
        default=0.0, min=-1.0, max=1.0, precision=2
    )
    n_sectors: bpy.props.IntProperty(
        name="Sectores Radiales (N)",
        default=6, min=1, max=32
    )

class VIEW3D_PT_tpms_builder_panel(bpy.types.Panel):
    bl_label = "TPMS Builder"
    bl_idname = "VIEW3D_PT_tpms_builder_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TPMS Builder'

    def draw(self, context):
        layout = self.layout
        props = context.scene.tpms_builder_props
        active_obj = context.active_object

        box_target = layout.box()
        if active_obj:
            box_target.label(text=f"Modelo Activo: {active_obj.name}", icon='MESH_DATA')
        else:
            box_target.label(text="Selecciona un objeto 3D", icon='ERROR')

        box_tpms = layout.box()
        box_tpms.label(text="Configuración Geométrica", icon='MESH_GRID')
        box_tpms.prop(props, "tpms_type")
        box_tpms.prop(props, "thickness")
        box_tpms.prop(props, "k_freq")
        box_tpms.prop(props, "gradient_factor")

        if props.tpms_type == 'GYROID':
            box_tpms.prop(props, "n_sectors")

        box_perf = layout.box()
        box_perf.label(text="Rendimiento y Algoritmo", icon='MODIFIER')
        box_perf.prop(props, "boolean_solver")
        box_perf.prop(props, "use_preview_mode")
        
        if props.use_preview_mode:
            if props.tpms_type == 'BCC_STRUT':
                box_perf.prop(props, "preview_k_freq")
            else:
                box_perf.prop(props, "preview_resolution")
        else:
            if props.tpms_type != 'BCC_STRUT':
                box_perf.prop(props, "resolution")

        layout.separator()
        layout.operator("mesh.generate_tpms_bounded", icon='MOD_BOOLEAN')

# ------------------------------------------------------------------------
# Registro y Desregistro Estándar de Blender
# ------------------------------------------------------------------------
classes = (
    MESH_OT_generate_tpms_bounded,
    TPMSBuilderProperties,
    VIEW3D_PT_tpms_builder_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.tpms_builder_props = bpy.props.PointerProperty(type=TPMSBuilderProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.tpms_builder_props

if __name__ == "__main__":
    register()
