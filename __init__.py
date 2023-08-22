'''
    Copyright (C) 2023  Andrei Suvorau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Root Motion Transfer",
    "author": "Andrei Suvorau",
    "version": (1, 0, 0),
    "blender": (3, 00, 0),
    "location": "3D View > UI (Right Panel) > Tools",
    "description": ("Transfer root motion from armature to root bone"),
    "warning": "",
    "wiki_url": "https://github.com/suVrik/RootMotionTransfer/wiki",
    "tracker_url": "https://github.com/suVrik/RootMotionTransfer/issues" ,
    "category": "Animation"
}

import bpy
import mathutils
from math import radians

class RootMotionTransfer_PropertyGroup(bpy.types.PropertyGroup):
    keep_root_motion_location: bpy.props.BoolProperty(name = 'Keep location root motion', description = 'Keep location root motion', default = False)
    keep_root_motion_location_x: bpy.props.BoolProperty(name = 'Keep X location', description = 'Keep location root motion along X axis', default = True)
    keep_root_motion_location_y: bpy.props.BoolProperty(name = 'Keep Y location', description = 'Keep location root motion along Y axis', default = True)
    keep_root_motion_location_z: bpy.props.BoolProperty(name = 'Keep Z location', description = 'Keep location root motion along Z axis', default = True)

    keep_root_motion_rotation: bpy.props.BoolProperty(name = 'Keep rotation root motion', description = 'Keep rotation root motion', default = False)
    keep_root_motion_rotation_x: bpy.props.BoolProperty(name = 'Keep X rotation', description = 'Keep rotation root motion along X axis', default = True)
    keep_root_motion_rotation_y: bpy.props.BoolProperty(name = 'Keep Y rotation', description = 'Keep rotation root motion along Y axis', default = True)
    keep_root_motion_rotation_z: bpy.props.BoolProperty(name = 'Keep Z rotation', description = 'Keep rotation root motion along Z axis', default = True)

    armature_rotation: bpy.props.FloatVectorProperty(name = 'Armature Rotation', description = 'Armature rotation to preserve', default = (radians(90), 0, 0), subtype = 'EULER')
    
    armature_scale: bpy.props.FloatVectorProperty(name = 'Armature Scale', description = 'Armature scale to preserve', default = (0.01, 0.01, 0.01))


class RootMotionTransfer_OT_transfer(bpy.types.Operator):
    bl_label = 'Transfer root motion'
    bl_idname = 'rootmotiontransfer.transfer'
    
    def execute(self, context):
        selected_armature = bpy.context.active_object

        def apply_animated_transform_to_root_bone(armature):
            properties = bpy.context.scene.RootMotionTransfer

            root_bone_name = armature.data.bones[0].name

            if not root_bone_name in armature.pose.bones:
                print('Failed to identify a root bone')
                return False
            
            action = armature.animation_data.action
            first_frame = int(action.frame_range[0])
            last_frame = int(action.frame_range[1])
            
            root_bone_local_matrix = armature.data.bones[0].matrix_local
            
            root_bone_local_matrix_inverse = root_bone_local_matrix.copy()
            root_bone_local_matrix_inverse.invert_safe()
            
            root_bone_curves = []
            armature_curves = []
            
            for fcurve in action.fcurves:
                if fcurve.data_path.startswith(f'pose.bones["{root_bone_name}"]'):
                    root_bone_curves.append(fcurve)
                elif not fcurve.data_path.startswith('pose.bones['):
                    armature_curves.append(fcurve)
                    
            if (len(root_bone_curves) != 10 or
                    not (root_bone_curves[0].data_path.endswith('location') and root_bone_curves[0].array_index == 0) or
                    not (root_bone_curves[1].data_path.endswith('location') and root_bone_curves[1].array_index == 1) or
                    not (root_bone_curves[2].data_path.endswith('location') and root_bone_curves[2].array_index == 2) or
                    not (root_bone_curves[3].data_path.endswith('rotation_quaternion') and root_bone_curves[3].array_index == 0) or
                    not (root_bone_curves[4].data_path.endswith('rotation_quaternion') and root_bone_curves[4].array_index == 1) or
                    not (root_bone_curves[5].data_path.endswith('rotation_quaternion') and root_bone_curves[5].array_index == 2) or
                    not (root_bone_curves[6].data_path.endswith('rotation_quaternion') and root_bone_curves[6].array_index == 3) or
                    not (root_bone_curves[7].data_path.endswith('scale') and root_bone_curves[7].array_index == 0) or
                    not (root_bone_curves[8].data_path.endswith('scale') and root_bone_curves[8].array_index == 1) or
                    not (root_bone_curves[9].data_path.endswith('scale') and root_bone_curves[9].array_index == 2)):
                print('Either not all root bone curves are present or they use euler angles!')
                return False
            
            if (len(armature_curves) != 9 or
                    not (armature_curves[0].data_path.endswith('location') and armature_curves[0].array_index == 0) or
                    not (armature_curves[1].data_path.endswith('location') and armature_curves[1].array_index == 1) or
                    not (armature_curves[2].data_path.endswith('location') and armature_curves[2].array_index == 2) or
                    not (armature_curves[3].data_path.endswith('rotation_euler') and armature_curves[3].array_index == 0) or
                    not (armature_curves[4].data_path.endswith('rotation_euler') and armature_curves[4].array_index == 1) or
                    not (armature_curves[5].data_path.endswith('rotation_euler') and armature_curves[5].array_index == 2) or
                    not (armature_curves[6].data_path.endswith('scale') and armature_curves[6].array_index == 0) or
                    not (armature_curves[7].data_path.endswith('scale') and armature_curves[7].array_index == 1) or
                    not (armature_curves[8].data_path.endswith('scale') and armature_curves[8].array_index == 2)):
                print('Either not all armature curves are present or they use quaternions!')
                return False
            
            root_bone_matrices = []
            current_armature_matrices = []
            target_armature_matrices = []

            target_armature_location = mathutils.Vector((0, 0, 0))
            target_armature_rotation = mathutils.Euler((properties.armature_rotation[0], properties.armature_rotation[1], properties.armature_rotation[2]), 'XYZ')
            
            for frame in range(first_frame, last_frame + 1):
                root_bone_location = mathutils.Vector((root_bone_curves[0].evaluate(frame), root_bone_curves[1].evaluate(frame), root_bone_curves[2].evaluate(frame)))
                root_bone_rotation = mathutils.Quaternion((root_bone_curves[3].evaluate(frame), root_bone_curves[4].evaluate(frame), root_bone_curves[5].evaluate(frame), root_bone_curves[6].evaluate(frame)))
                root_bone_scale = mathutils.Vector((root_bone_curves[7].evaluate(frame), root_bone_curves[8].evaluate(frame), root_bone_curves[9].evaluate(frame)))
                
                root_bone_matrix = mathutils.Matrix.LocRotScale(root_bone_location, root_bone_rotation, root_bone_scale)
                root_bone_matrices.append(root_bone_matrix)
                
                current_armature_location = mathutils.Vector((armature_curves[0].evaluate(frame), armature_curves[1].evaluate(frame), armature_curves[2].evaluate(frame)))
                current_armature_rotation = mathutils.Euler((armature_curves[3].evaluate(frame), armature_curves[4].evaluate(frame), armature_curves[5].evaluate(frame)), 'XYZ')
                current_armature_scale = mathutils.Vector((armature_curves[6].evaluate(frame), armature_curves[7].evaluate(frame), armature_curves[8].evaluate(frame)))
                
                current_armature_matrix = mathutils.Matrix.LocRotScale(current_armature_location, current_armature_rotation, current_armature_scale)
                current_armature_matrices.append(current_armature_matrix)

                if properties.keep_root_motion_location:
                    if properties.keep_root_motion_location_x:
                        target_armature_location.x = current_armature_location.x
                    if properties.keep_root_motion_location_y:
                        target_armature_location.y = current_armature_location.y
                    if properties.keep_root_motion_location_z:
                        target_armature_location.z = current_armature_location.z

                if properties.keep_root_motion_rotation:
                    if properties.keep_root_motion_rotation_x:
                        target_armature_rotation.x = current_armature_rotation.x
                    if properties.keep_root_motion_rotation_y:
                        target_armature_rotation.y = current_armature_rotation.y
                    if properties.keep_root_motion_rotation_z:
                        target_armature_rotation.z = current_armature_rotation.z

                target_armature_scale = mathutils.Vector((properties.armature_scale[0], properties.armature_scale[1], properties.armature_scale[2]))

                target_armature_matrix = mathutils.Matrix.LocRotScale(target_armature_location, target_armature_rotation, target_armature_scale)
                target_armature_matrices.append(target_armature_matrix)
                
            index = 0
                
            for frame in range(first_frame, last_frame + 1):
                current_armature_matrix = current_armature_matrices[index]
                
                target_armature_matrix = target_armature_matrices[index]
                
                target_armature_matrix_inverse = target_armature_matrix.copy()
                target_armature_matrix_inverse.invert_safe()

                delta_armature_matrix = target_armature_matrix_inverse @ current_armature_matrix

                result = root_bone_local_matrix_inverse @ delta_armature_matrix @ root_bone_local_matrix @ root_bone_matrices[index]

                result_location, result_rotation, result_scale = result.decompose()
                
                root_bone_curves[0].keyframe_points.insert(frame, result_location.x)
                root_bone_curves[1].keyframe_points.insert(frame, result_location.y)
                root_bone_curves[2].keyframe_points.insert(frame, result_location.z)
                root_bone_curves[3].keyframe_points.insert(frame, result_rotation.w)
                root_bone_curves[4].keyframe_points.insert(frame, result_rotation.x)
                root_bone_curves[5].keyframe_points.insert(frame, result_rotation.y)
                root_bone_curves[6].keyframe_points.insert(frame, result_rotation.z)
                root_bone_curves[7].keyframe_points.insert(frame, result_scale.x)
                root_bone_curves[8].keyframe_points.insert(frame, result_scale.y)
                root_bone_curves[9].keyframe_points.insert(frame, result_scale.z)
                
                target_location, target_rotation, target_scale = target_armature_matrix.decompose()
                target_rotation = target_rotation.to_euler('XYZ')
                
                armature_curves[0].keyframe_points.insert(frame, target_location.x)
                armature_curves[1].keyframe_points.insert(frame, target_location.y)
                armature_curves[2].keyframe_points.insert(frame, target_location.z)
                armature_curves[3].keyframe_points.insert(frame, target_rotation.x)
                armature_curves[4].keyframe_points.insert(frame, target_rotation.y)
                armature_curves[5].keyframe_points.insert(frame, target_rotation.z)
                armature_curves[6].keyframe_points.insert(frame, target_scale.x)
                armature_curves[7].keyframe_points.insert(frame, target_scale.y)
                armature_curves[8].keyframe_points.insert(frame, target_scale.z)
                
                index = index + 1
                
            bpy.context.view_layer.update()
            
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
            
            return True

        if selected_armature and selected_armature.type == 'ARMATURE':
            if apply_animated_transform_to_root_bone(selected_armature):
                self.report({'INFO'}, 'Root motion successfully transfered.')
            else:
                self.report({'ERROR'}, 'Failed to propagate root motion.')
        else:
            self.report({'ERROR'}, 'No armature selected.')

        return {'FINISHED'}


class RootMotionTransfer_PT_panel(bpy.types.Panel):
    bl_label = 'Root Motion Transfer'
    bl_idname = 'RootMotionTransfer_PT_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'
 
    def draw(self, context):
        layout = self.layout

        properties = bpy.context.scene.RootMotionTransfer

        layout.prop(properties, 'keep_root_motion_location')
        if properties.keep_root_motion_location:
            layout.prop(properties, 'keep_root_motion_location_x')
            layout.prop(properties, 'keep_root_motion_location_y')
            layout.prop(properties, 'keep_root_motion_location_z')

        layout.prop(properties, 'keep_root_motion_rotation')
        if properties.keep_root_motion_rotation:
            layout.prop(properties, 'keep_root_motion_rotation_x')
            layout.prop(properties, 'keep_root_motion_rotation_y')
            layout.prop(properties, 'keep_root_motion_rotation_z')

        if not properties.keep_root_motion_rotation or not (properties.keep_root_motion_rotation_x and properties.keep_root_motion_rotation_y and properties.keep_root_motion_rotation_z):
            layout.label(text = 'Armature Rotation:')
            layout.prop(properties, 'armature_rotation', text = '')

        layout.label(text = 'Armature Scale:')
        layout.prop(properties, 'armature_scale', text = '')

        if bpy.context.active_object and bpy.context.active_object.type == 'ARMATURE':
            operator = layout.operator('rootmotiontransfer.transfer')


classes = [RootMotionTransfer_PT_panel, RootMotionTransfer_OT_transfer, RootMotionTransfer_PropertyGroup]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.RootMotionTransfer = bpy.props.PointerProperty(type = RootMotionTransfer_PropertyGroup)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
