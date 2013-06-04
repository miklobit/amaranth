# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Amaranth Toolset",
    "author": "Pablo Vazquez",
    "version": (0, 3, 2),
    "blender": (2, 7, 0),
    "location": "Scene Properties > Amaranth Toolset Panel",
    "description": "A collection of tools and settings to improve productivity",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Scene"}


import bpy
from bpy.types import Operator
from mathutils import Vector

# FEATURE: Refresh Scene!
class SCENE_OT_refresh(Operator):
    """Refresh the current scene"""
    bl_idname = "scene.refresh"
    bl_label = "Refresh!"
    
    def execute(self, context):
        scene = context.scene
        if scene.use_scene_refresh:    
            # Changing the frame is usually the best way to go
            bpy.context.scene.frame_current = bpy.context.scene.frame_current
            self.report({"INFO"}, "Scene Refreshed!")
            
        return {'FINISHED'}

def button_refresh(self, context):

    scene = context.scene
    if scene.use_scene_refresh:
        self.layout.separator()
        self.layout.operator(
            SCENE_OT_refresh.bl_idname,
            text="Refresh!",
            icon='FILE_REFRESH')
# // FEATURE: Refresh Scene!

# FEATURE: Save & Reload
def save_reload(self, context, path):

    if path:
        bpy.ops.wm.save_mainfile()
        self.report({'INFO'}, "Saved & Reloaded")
        bpy.ops.wm.open_mainfile("EXEC_DEFAULT", filepath=path)
    else:
        bpy.ops.wm.save_as_mainfile("INVOKE_AREA")

class FILE_OT_save_reload(Operator):
    """Save and Reload the current blend file"""
    bl_idname = "wm.save_reload"
    bl_label = "Save & Reload"

    def execute(self, context):

        scene = context.scene
        if scene.use_file_save_reload:
            path = bpy.data.filepath
            save_reload(self, context, path)
    
        return {'FINISHED'}

def button_save_reload(self, context):

    scene = context.scene
    if scene.use_file_save_reload:
        self.layout.separator()
        self.layout.operator(
            FILE_OT_save_reload.bl_idname,
            text="Save & Reload",
            icon='FILE_REFRESH')
# // FEATURE: Save & Reload

# FEATURE: Current Frame
def button_frame_current(self, context):

    scene = context.scene
    if scene.use_frame_current:
        self.layout.separator()
        self.layout.prop(
            scene, "frame_current",
            text="Set Current Frame")
# // FEATURE: Current Frame

# FEATURE: Timeline Time + Frames Left
def label_timeline_extra_info(self, context):

    layout = self.layout
    scene = context.scene
    if scene.use_timeline_extra_info:
        row = layout.row(align=True)
        row.label(text="%s / %s" % (bpy.utils.smpte_from_frame(scene.frame_current - scene.frame_start),
                        bpy.utils.smpte_from_frame(scene.frame_end - scene.frame_start)), icon="TIME")

        if (scene.frame_current > scene.frame_end):
            row.label(text="%s Frames Too Much" % (scene.frame_end - scene.frame_current))
        else:
            row.label(text="%s Frames Left" % (scene.frame_end - scene.frame_current))

# // FEATURE: Timeline Time + Frames Left

# FEATURE: Directory Current Blend
class FILE_OT_directory_current_blend(Operator):
    """Go to the directory of the currently open blend file"""
    bl_idname = "file.directory_current_blend"
    bl_label = "Current Blend's Folder"

    def execute(self, context):
        bpy.ops.file.select_bookmark(dir='//')
        return {'FINISHED'}

def button_directory_current_blend(self, context):

    if bpy.data.filepath:
        self.layout.operator(
            FILE_OT_directory_current_blend.bl_idname,
            text="Current Blend's Folder",
            icon='APPEND_BLEND')
# // FEATURE: Directory Current Blend

# FEATURE: Node Templates
class NODE_OT_AddTemplateVignette(Operator):
    bl_idname = "node.template_add_vignette"
    bl_label = "Add Vignette"
    bl_description = "Add a vignette effect"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None

    # used as reference the setup scene script from master nazgul
    def _setupNodes(self, context):
        scene = context.scene
        space = context.space_data
        tree = scene.node_tree

        bpy.ops.node.select_all(action='DESELECT')

        ellipse = tree.nodes.new(type='CompositorNodeEllipseMask')
        ellipse.width = 0.8
        ellipse.height = 0.4
        blur = tree.nodes.new(type='CompositorNodeBlur')
        blur.use_relative = True
        blur.factor_x = 30
        blur.factor_y = 50
        ramp = tree.nodes.new(type='CompositorNodeValToRGB')
        ramp.color_ramp.interpolation = 'B_SPLINE'
        ramp.color_ramp.elements[1].color = (0.6, 0.6, 0.6, 1)

        overlay = tree.nodes.new(type='CompositorNodeMixRGB')
        overlay.blend_type = 'OVERLAY'
        overlay.inputs[0].default_value = 0.8
        overlay.inputs[1].default_value = (0.5, 0.5, 0.5, 1)

        tree.links.new(ellipse.outputs["Mask"],blur.inputs["Image"])
        tree.links.new(blur.outputs["Image"],ramp.inputs[0])
        tree.links.new(ramp.outputs["Image"],overlay.inputs[2])

        if tree.nodes.active:
            blur.location = tree.nodes.active.location
            blur.location += Vector((330.0, -250.0))
        else:
            blur.location += Vector((space.cursor_location[0], space.cursor_location[1]))

        ellipse.location = blur.location
        ellipse.location += Vector((-300.0, 0))

        ramp.location = blur.location
        ramp.location += Vector((175.0, 0))

        overlay.location = ramp.location
        overlay.location += Vector((240.0, 275.0))

        for node in {ellipse, blur, ramp, overlay}:
            node.select = True
            node.show_preview = False

        bpy.ops.node.join()

        frame = ellipse.parent
        frame.label = 'Vignette'
        frame.use_custom_color = True
        frame.color = (0.783538, 0.0241576, 0.0802198)
        
        overlay.parent = None
        overlay.label = 'Vignette Overlay'

    def execute(self, context):
        self._setupNodes(context)

        return {'FINISHED'}

# Node Templates Menu
class NODE_MT_amaranth_templates(bpy.types.Menu):
    bl_idname = 'NODE_MT_amaranth_templates'
    bl_space_type = 'NODE_EDITOR'
    bl_label = "Templates"
    bl_description = "List of Amaranth Templates"

    def draw(self, context):
        layout = self.layout
        layout.operator(
            NODE_OT_AddTemplateVignette.bl_idname,
            text="Vignette",
            icon='COLOR')

def node_templates_pulldown(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.scale_x = 1.3
    row.menu("NODE_MT_amaranth_templates",
        icon="RADIO")
# // FEATURE: Node Templates

def node_stats(self,context):

    nodes = context.scene.node_tree.nodes
    nodes_total = len(nodes.keys())
    nodes_selected = 0
    for n in nodes:
        if n.select:
            nodes_selected = nodes_selected + 1

    layout = self.layout
    row = layout.row(align=True)
    row.label(text="Nodes: %s/%s" % (nodes_selected, str(nodes_total)))

# FEATURE: OB/MA ID panel in Node Editor
class NODE_PT_indices(bpy.types.Panel):
    '''Object / Material Indices Panel'''
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'Object / Material Indices'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        node = context.active_node
        return node and node.type == 'ID_MASK'

    def draw(self, context):
        layout = self.layout

        objects = bpy.data.objects
        materials = bpy.data.materials
        node = context.active_node

        show_ob_id = False
        show_ma_id = False
        matching_ids = False

        if context.active_object:
            ob_act = context.active_object
        else:
            ob_act = False

        for ob in objects:
            if ob and ob.pass_index > 0:
                show_ob_id = True
        for ma in materials:
            if ma and ma.pass_index > 0:
                show_ma_id = True
        row = layout.row(align=True)  
        row.prop(node, 'index', text="Mask Index")
        row.prop(node, 'use_matching_indices', text="Only Matching IDs")
        
        layout.separator()

        if not show_ob_id and not show_ma_id:
            layout.label(text="No objects or materials indices so far.", icon="INFO")

        if show_ob_id:
            split = layout.split()
            col = split.column()
            col.label(text="Object Name")
            split.label(text="ID Number")
            row = layout.row()
            for ob in objects:
                icon = "OUTLINER_DATA_" + ob.type
                if ob.library:
                    icon = "LIBRARY_DATA_DIRECT"
                elif ob.is_library_indirect:
                    icon = "LIBRARY_DATA_INDIRECT"

                if ob and node.use_matching_indices \
                      and ob.pass_index == node.index \
                      and ob.pass_index != 0:
                    matching_ids = True
                    row.label(
                      text="[{}]".format(ob.name)
                          if ob_act and ob.name == ob_act.name else ob.name,
                      icon=icon)
                    row.label(text="%s" % ob.pass_index)
                    row = layout.row()

                elif ob and not node.use_matching_indices \
                        and ob.pass_index > 0:

                    matching_ids = True
                    row.label(
                      text="[{}]".format(ob.name)
                          if ob_act and ob.name == ob_act.name else ob.name,
                      icon=icon)
                    row.label(text="%s" % ob.pass_index)
                    row = layout.row()

            if node.use_matching_indices and not matching_ids:
                row.label(text="No objects with ID %s" % node.index, icon="INFO")

            layout.separator()

        if show_ma_id:
            split = layout.split()
            col = split.column()
            col.label(text="Material Name")
            split.label(text="ID Number")
            row = layout.row()

            for ma in materials:
                icon = "BLANK1"
                if ma.use_nodes:
                    icon = "NODETREE"
                elif ma.library:
                    icon = "LIBRARY_DATA_DIRECT"
                    if ma.is_library_indirect:
                        icon = "LIBRARY_DATA_INDIRECT"

                if ma and node.use_matching_indices \
                      and ma.pass_index == node.index \
                      and ma.pass_index != 0:
                    matching_ids = True
                    row.label(text="%s" % ma.name, icon=icon)
                    row.label(text="%s" % ma.pass_index)
                    row = layout.row()

                elif ma and not node.use_matching_indices \
                        and ma.pass_index > 0:

                    matching_ids = True
                    row.label(text="%s" % ma.name, icon=icon)
                    row.label(text="%s" % ma.pass_index)
                    row = layout.row()

            if node.use_matching_indices and not matching_ids:
                row.label(text="No materials with ID %s" % node.index, icon="INFO")


# // FEATURE: OB/MA ID panel in Node Editor

# UI: Amaranth Options Panel
class AmaranthToolsetPanel(bpy.types.Panel):
    '''Amaranth Toolset Panel'''
    bl_label = 'Amaranth Toolset'
    bl_options = {'DEFAULT_CLOSED'}
    bl_idname = 'SCENE_PT_amaranth_toolset'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text='Active Features', icon='SOLO_ON')

        row = layout.row()
        box = row.box()
        box.prop(scene, 'use_scene_refresh',
                 text= 'Refresh Scene',
                 icon='FILE_REFRESH')
        sub = box.row()
        sub.active = scene.use_scene_refresh
        sub.label(text="Specials Menu [W], or hit F5")

        # --
        row = layout.row()
        box = row.box()
        box.prop(scene, 'use_file_save_reload',
                 text= 'Save & Reload File',
                 icon='LOAD_FACTORY')
        sub = box.row()
        sub.active = scene.use_file_save_reload
        sub.label(text="File menu > Save & Reload, or Ctrl + Shift + W")

        # --
        row = layout.row()
        box = row.box()
        box.prop(scene, 'use_frame_current',
                 text= 'Current Frame Slider',
                 icon='PREVIEW_RANGE')
        sub = box.row()
        sub.active = scene.use_frame_current
        sub.label(text="Specials Menu [W]")

        # --
        row = layout.row()
        box = row.box()
        box.prop(scene, 'use_timeline_extra_info',
                 text= 'Timeline Extra Info',
                 icon='TIME')
        sub = box.row()
        sub.active = scene.use_timeline_extra_info
        sub.label(text="Timeline Header")

addon_keymaps = []

kmi_defs = (
    ('wm.call_menu', 'W', False, False, False, (('name', NODE_MT_amaranth_templates.bl_idname),)),
)

def register():
    # UI: Register the panel
    bpy.utils.register_class(AmaranthToolsetPanel)
    bpy.types.Scene.use_frame_current = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.use_scene_refresh = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.use_file_save_reload = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.use_timeline_extra_info = bpy.props.BoolProperty(default=True)

    bpy.utils.register_class(SCENE_OT_refresh) # Refresh
    bpy.types.VIEW3D_MT_object_specials.append(button_refresh)
    
    bpy.utils.register_class(FILE_OT_save_reload) # Save Reload
    bpy.types.INFO_MT_file.append(button_save_reload)

    bpy.types.VIEW3D_MT_object_specials.append(button_frame_current) # Current Frame
    bpy.types.TIME_HT_header.append(label_timeline_extra_info) # Timeline Extra Info

    bpy.utils.register_class(NODE_OT_AddTemplateVignette) # Node Templates
    bpy.utils.register_class(NODE_MT_amaranth_templates)
    bpy.types.NODE_HT_header.append(node_templates_pulldown)
    bpy.types.NODE_HT_header.append(node_stats)

    bpy.utils.register_class(FILE_OT_directory_current_blend) # Node Templates
    bpy.types.FILEBROWSER_HT_header.append(button_directory_current_blend)

    bpy.utils.register_class(NODE_PT_indices) # OB/MA Indices Panel
    bpy.types.Node.use_matching_indices = bpy.props.BoolProperty(default=True,
                                            description="If disabled, display all available indices")

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Window')
        kmi = km.keymap_items.new('scene.refresh', 'F5', 'PRESS', shift=False, ctrl=False)
        kmi = km.keymap_items.new('wm.save_reload', 'W', 'PRESS', shift=True, ctrl=True)

        kmi = km.keymap_items.new('wm.context_toggle_enum', 'Z', 'PRESS', shift=True, alt=True)
        kmi.properties.data_path = 'space_data.viewport_shade'
        kmi.properties.value_1 = 'SOLID'
        kmi.properties.value_2 = 'RENDERED'

        addon_keymaps.append((km, kmi))

    # copypasted from the awesome node efficiency tools, future hotkeys proof!
    km = kc.keymaps.new(name='Node Editor', space_type="NODE_EDITOR")
    for (identifier, key, CTRL, SHIFT, ALT, props) in kmi_defs:
        kmi = km.keymap_items.new(identifier, key, 'PRESS', ctrl=CTRL, shift=SHIFT, alt=ALT)
        if props:
            for prop, value in props:
                setattr(kmi.properties, prop, value)
        addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(AmaranthToolsetPanel)

    bpy.utils.unregister_class(SCENE_OT_refresh)
    bpy.types.VIEW3D_MT_object_specials.remove(button_refresh)
    bpy.utils.unregister_class(FILE_OT_save_reload)
    bpy.types.INFO_MT_file.remove(button_save_reload)
    bpy.types.VIEW3D_MT_object_specials.remove(button_frame_current)
    bpy.types.TIME_HT_header.remove(label_timeline_extra_info)

    bpy.utils.unregister_class(NODE_MT_amaranth_templates)
    bpy.types.NODE_HT_header.remove(node_templates_pulldown)
    bpy.utils.unregister_class(NODE_OT_AddTemplateVignette)
    bpy.types.NODE_HT_header.remove(node_stats)

    bpy.types.FILEBROWSER_HT_header.remove(button_directory_current_blend)

    bpy.utils.unregister_class(NODE_PT_indices)
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
