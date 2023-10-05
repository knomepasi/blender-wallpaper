import gi
import sys
import random
import os
import time
import re

from multiprocessing import Process

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk, Gdk, GdkPixbuf

opts = {}

class BlenderWallpaperGUI(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='fi.knome.blender-wallpaper-gui')
        GLib.set_application_name('Blender Wallpaper GUI')

    def do_activate(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('blender-wallpaper-gui.glade')

        handlers = {
            'randomizeAll': self.randomize_all,
            'randomizeElement': self.randomize_element,
            'renderImage': self.render_image,
        }
        self.builder.connect_signals(handlers)

        self.randomize_all(None)

        win = self.builder.get_object('window_main')
        win.set_application(app)
        win.present()
        win.show_all()

    # Handlers
    def randomize_all(self, element):
        self.randomize_element(self.builder.get_object('plane'))
        self.randomize_element(self.builder.get_object('light_north'))
        self.randomize_element(self.builder.get_object('light_east'))
        self.randomize_element(self.builder.get_object('light_south'))
        self.randomize_element(self.builder.get_object('light_west'))

    def randomize_element(self, element):
        children = element.get_children()
        for c in children:
            if c.get_name() == 'GtkColorButton':
                c.set_rgba(self._random_rgba())
            elif c.get_name() == 'GtkSpinButton':
                c.set_value(self._random_energy())
        return

    def render_image(self, button):
        # TODO: Show spinner
        import bpy
        import mathutils

        rendered = self.builder.get_object('rendered_image')
        rendered.set_from_icon_name('process-working-symbolic', 24)

        # Open file
        bpy.ops.wm.open_mainfile(filepath="blender-wallpaper.blend")

        # Set seed
        seed = re.sub(r"\D", "", self.builder.get_object('seed').get_text())
        if len(seed) < 1:
            seed = int(time.time())
        else:
            seed = int(seed)

        bpy.data.node_groups['Geometry Nodes'].nodes['Integer'].integer = seed

        # Set material color
        color = self.builder.get_object('color_plane').get_rgba()
        bpy.data.materials['Material'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = tuple(color)

        # Set light colors and energies
        lights = { 'light_north': 'LightN', 'light_east': 'LightE', 'light_south': 'LightS', 'light_west': 'LightW' }
        for element, light in lights.items():
            color = self.builder.get_object( 'color_' + element ).get_rgba()
            bpy.data.lights[light].color = tuple(color)[:-1]
            energy = self.builder.get_object( 'energy_' + element ).get_value()
            bpy.data.lights[light].energy = int(energy) * 50

        # Set camera rotation
        rotation = self.builder.get_object('rotation').get_value()
        rot_euler = mathutils.Euler((0,0,rotation))
        bpy.data.objects['Camera'].rotation_euler[2] = rot_euler.z

        # TODO: Set camera distance
        distance = self.builder.get_object('distance').get_value()
        bpy.data.objects['Camera'].location[2] = int(distance)

        # Render
        filename = os.getcwd() + '/wallpaper.png'
        bpy.context.scene.render.filepath = filename
        img = bpy.ops.render.render(write_still=1)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        pixbuf = pixbuf.scale_simple(720, 450, GdkPixbuf.InterpType.BILINEAR)
        rendered.set_from_pixbuf(pixbuf)

        # Hide spinner, show image
        bpy.ops.wm.quit_blender()

    #
    def _random_rgba(self):
        return Gdk.RGBA(random.random(), random.random(), random.random(), 1)

    def _random_energy(self):
        return random.randrange(0, 20) * 5

app = BlenderWallpaperGUI()
sys.exit(app.run(sys.argv))
