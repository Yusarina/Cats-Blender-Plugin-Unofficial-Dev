# -*- coding: utf-8 -*-
# SUPPORT_UNTIL: 3.3 LTS

from bpy.types import Header


class MMDViewHeader:
    bl_idname = 'mmd_tools_local_local_HT_view_header'
    bl_space_type = 'VIEW_3D'

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                context.active_object.type == 'ARMATURE' and
                context.active_object.mode == 'POSE')

    def draw(self, context):
        if self.poll(context):
            self.layout.operator('mmd_tools_local_local.flip_pose', text='', icon='ARROW_LEFTRIGHT')
