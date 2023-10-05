import bpy
import random
import time
import argparse
import mathutils
import os

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--material', default='random', help='Material color in hex, without #. If not set, randomized.')
parser.add_argument('-ln', '--north', default='random', help='Light color in hex, without #. If not set, randomized.')
parser.add_argument('-le', '--east', default='random', help='Light color in hex, without #. If not set, randomized.')
parser.add_argument('-ls', '--south', default='random', help='Light color in hex, without #. If not set, randomized.')
parser.add_argument('-lw', '--west', default='random', help='Light color in hex, without #. If not set, randomized.')
parser.add_argument('-r', '--rotate', default='random', help='Camera rotation in degrees. If not set, randomized.')
parser.add_argument('--seed', default='random', help='Seed (integer). If not set, randomized.')
parser.add_argument('-f', '--file', default='wallpaper', help='Output filename prefix.')
args = vars(parser.parse_args())

#
def get_random_color_component():
    return random.randrange(0,70) / 100

def hex_to_rgb(hex, has_alpha = False):
    rgb = []
    for i in (0,2,4):
        decimal = int(hex[i:i+2], 16)
        rgb.append(decimal/256)
    if has_alpha:
        rgb.append(1)
    print(rgb)
    return tuple(rgb)

# Open file
bpy.ops.wm.open_mainfile(filepath="blender-wallpaper.blend")

# Change seed
if args['seed'] == 'random':
    bpy.data.node_groups['Geometry Nodes'].nodes['Integer'].integer = random.randrange( -2147483648, 2147483647 )
else:
    bpy.data.node_groups['Geometry Nodes'].nodes['Integer'].integer = int(args['seed'])

# Change material base color
if args['material'] == 'random':
    material_color = ( get_random_color_component(), get_random_color_component(), get_random_color_component(), 1 )
else:
    material_color = hex_to_rgb( args['material'], True )

bpy.data.materials['Material'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = material_color

# Change light colors
lights = { 'north': 'LightN', 'east': 'LightE', 'south': 'LightS', 'west': 'LightW' }
for direction, light in lights.items():
    if( args[direction] == 'random' ):
        bpy.data.lights[light].color = ( get_random_color_component(), get_random_color_component(), get_random_color_component() )
    else:
        bpy.data.lights[light].color = hex_to_rgb( args[direction] )
    bpy.data.lights[light].energy = random.randrange( 1000, 3500 )

# Rotate camera
if args['rotate'] == 'random':
    rotation = random.randrange(1,360)
else:
    rotation = int(args['rotate'])

rot_euler = mathutils.Euler((0,0,rotation))
bpy.data.objects['Camera'].rotation_euler[2] = rot_euler.z

# Render
if args['seed'] == 'random':
    filename = args['file']
else:
    filename = args['file'] + '-' + args['seed']

bpy.context.scene.render.filepath = os.getcwd() + '/' + filename + '-' + str( time.time() )
bpy.ops.render.render(write_still = 1)
