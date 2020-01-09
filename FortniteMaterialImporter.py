bl_info = {
    "name": "FortniteMaterialImporter",
    "description": "Creates the material for a mesh imported from Fortnite",
    "author": "Willem van der Doe",
    "version": (1, 0), 
    "blender": (2, 80, 0),
    "location": "Properties > Material > Fortnite Material",
    "category": "Material"
}

import os
import re
import bpy
from bpy.types import PropertyGroup
from bpy_extras.io_utils import ImportHelper

class FortniteMaterialSettingsTool(PropertyGroup):
    u: bpy.props.StringProperty(
        name = "u",
        description = "Path to the folder where the textures are",
        default = ""
    )

class FortniteMaterialPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Fortnite Material"
    bl_idname = "MATERIAL_PT_FortniteMaterial"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.prop(context.scene.FortniteMaterialSettings, "u", text="Folder")
        row.operator("material.folderselector", text="", icon='FILEBROWSER')
        
        row = layout.row()
        row.operator("material.newfortnitematerial", icon="MATERIAL")

class CreateFortniteMaterial(bpy.types.Operator):
    bl_label = "Create Fortnite Material"
    bl_idname = "material.newfortnitematerial"
    bl_description = "Create a Fortnite Material for the current object"
    
    def execute(self, context):
        
        obj = context.object

        # shade smooth
        for f in obj.data.polygons:
            f.use_smooth = True
        
        # remove current materials from object
        obj.data.materials.clear()
        
        # create new material
        m = bpy.data.materials.new(name="FortniteMaterial")
        obj.data.materials.append(m)
        m.use_nodes = True
        
        # get the nodes and links
        n = m.node_tree.nodes
        l = m.node_tree.links
        # get the Principled BSDF node
        p = n[1]
        
        # get textures
        u = context.scene.FortniteMaterialSettings.u
        t = [f for f in os.listdir(u)]
        
        tm = None
        td = None
        ts = None
        tn = None
        
        # get the M
        r = re.compile("(?i).*M.tga")
        tms = list(filter(r.match, t))
        if len(tms) > 0:
            if len(tms) > 1:
                print("Warning! Multiple M's found! Using the first one.")
            tm = tms[0]
            
            # create RGB Curves node and connect it to the shader
            curves = n.new(type="ShaderNodeRGBCurve")
            l.new(curves.outputs[0], p.inputs[0])
            
            # create Separate RGB node and connect it to the RGB Curves node
            separateRGBm = n.new(type="ShaderNodeSeparateRGB")
            l.new(separateRGBm.outputs[2], curves.inputs[0])
            
            # create Image Texture node and connect it to the Separate RGB node
            imageTextureM = n.new(type="ShaderNodeTexImage")
            im = bpy.data.images.load(os.path.join(u, tm))
            imageTextureM.image = im
            l.new(imageTextureM.outputs[0], separateRGBm.inputs[0])
        
        # get the D
        r = re.compile("(?i).*D.tga")
        tds = list(filter(r.match, t))
        if len(tds) > 0:
            if len(tds) > 1:
                print("Warning! Multiple D's found! Using the first one.")
            td = tds[0]
            
            # create Image Texture node
            imageTextureD = n.new(type="ShaderNodeTexImage")
            id = bpy.data.images.load(os.path.join(u, td))
            imageTextureD.image = id
                
            # check if M exists
            if tm is not None:
                # connect to the RGB Curves node
                l.new(imageTextureD.outputs[0], curves.inputs[1])
            else:
                # connect directly to the shader node
                l.new(imageTextureD.outputs[0], p.inputs[0])
        
        # get the S
        r = re.compile("(?i).*S.tga")
        tss = list(filter(r.match, t))
        if len(tss) > 0:
            if len(tss) > 1:
                print("Warning! Multiple S's found! Using the first one.")
            ts = tss[0]
            
            # create Separate RGB node and connect it to the shader
            separateRGBs = n.new(type="ShaderNodeSeparateRGB")
            l.new(separateRGBs.outputs[1], p.inputs[4])
            l.new(separateRGBs.outputs[2], p.inputs[7])
            
            # create Image Texture node and connect it to the Separate RGB node
            imageTextureS = n.new(type="ShaderNodeTexImage")
            iis = bpy.data.images.load(os.path.join(u, ts))
            iis.colorspace_settings.name = "Non-Color"
            imageTextureS.image = iis
            l.new(imageTextureS.outputs[0], separateRGBs.inputs[0])
            
        # get the N
        r = re.compile("(?i).*N.tga")
        tns = list(filter(r.match, t))
        if len(tns) > 0:
            if len(tns) > 1:
                print("Warning! Multiple N's found! Using the first one.")
            tn = tns[0]

            # create Normal Map node and connect it to the shader
            normalmap = n.new(type="ShaderNodeNormalMap")
            l.new(normalmap.outputs[0], p.inputs[19])
            
            # create Image Texture node and connect it to the shader
            imageTextureN = n.new(type="ShaderNodeTexImage")
            iin = bpy.data.images.load(os.path.join(u, tn))
            iin.colorspace_settings.name = "Non-Color"
            imageTextureN.image = iin
            l.new(imageTextureN.outputs[0], normalmap.inputs[1])
        
        return {"FINISHED"}
    
class FortniteMaterialFolderSelector(bpy.types.Operator, ImportHelper):
    bl_idname = "material.folderselector"
    bl_label = "select folder"

    def execute(self, context):
        context.scene.FortniteMaterialSettings.u = os.path.dirname(self.properties.filepath)
        return{'FINISHED'}

classes = [FortniteMaterialSettingsTool, FortniteMaterialPanel, CreateFortniteMaterial, FortniteMaterialFolderSelector]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.FortniteMaterialSettings = bpy.props.PointerProperty(
            type=FortniteMaterialSettingsTool)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.FortniteMaterialSettings

if __name__ == "__main__":
    register()
