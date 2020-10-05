"""
This operator will select the faces which contain
the same data in the same channel as the one selected
"""

import bpy
from ..data.maps import all_maps, map_color_layer, map_is_color, map_channels


class SelectFacesWithSameData(bpy.types.Operator):
    """Select Faces with the same vertex colors data.
    Assumes all loops in a face share the same data
    and all selected faces share the same data"""
    bl_idname = "object.select_same_vertex_color_data"
    bl_label = "Select Faces With Same Data"
    bl_options = {'REGISTER', 'UNDO'}

    invert: bpy.props.BoolProperty(
        name="invert",
        default=False,
    )

    map: bpy.props.EnumProperty(
        name="Map",
        items=all_maps,
    )

    threshold: bpy.props.FloatProperty(
        name="Threshold",
        min=0,
        soft_max=1,
        max=5,
    )

    @classmethod
    def poll(cls, context):
        if not context.active_object \
                or context.active_object.type != 'MESH' \
                or len(context.active_object.data.polygons) < 1 \
                or context.mode != 'EDIT_MESH':
            return False
        return True

    def execute(self, context):
        mesh = context.active_object.data
        sfi = []
        # I don't know why but edit mesh bmesh is constantly crashing :
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
        for f in mesh.polygons:
            if f.select:
                sfi.append(f.index)

        bpy.ops.paint.vertex_paint_toggle()
        bpy.ops.paint.vertex_paint_toggle()
        color_layer = mesh.vertex_colors.get(map_color_layer[self.map])
        if not color_layer:
            print(
                f"No vertex color layer named {color_layer.name} on selected object")
            return {'FINISHED'}

        channel = map_channels[self.map]
        if map_is_color(self.map):
            color = color_layer.data[mesh.polygons[sfi[0]
                                                   ].loop_indices[0]].color[0:3]
            # TODO : Unselect edges and vertices.
            for f in mesh.polygons:
                same_color = True
                color_data = color_layer.data[f.loop_indices[0]].color[0:3]
                for i, channel in enumerate(color):
                    if abs(channel - color_data[i]) > self.threshold:
                        same_color = False
                        break
                f.select = not self.invert if same_color else self.invert
        else:
            color = color_layer.data[mesh.polygons[sfi[0]
                                                   ].loop_indices[0]].color[channel:channel + 1][0]
            # TODO : Unselect edges and vertices.
            for f in mesh.polygons:
                same = abs(color_layer.data[f.loop_indices[0]].color[channel:channel + 1][0] - color) > self.threshold
                f.select = self.invert if same else not self.invert
        bpy.ops.object.editmode_toggle()

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "invert")
        layout.prop(self, "map")
        layout.prop(self, "threshold", slider=True)
