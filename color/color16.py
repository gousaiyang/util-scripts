from __future__ import unicode_literals

import platform
import sys

print('Platform: %s' % platform.platform())
print('Python version: %s' % sys.version.splitlines()[0].strip())

try:
    import colorama
except ImportError:
    print('Colorama is not installed.')
else:
    colorama.init()
    print('Colorama is installed.')

print('Printing 16 colors:')

colors = [
    (30, 'Black'),
    (31, 'Red'),
    (32, 'Green'),
    (33, 'Yellow'),
    (34, 'Blue'),
    (35, 'Magenta'),
    (36, 'Cyan'),
    (37, 'White'),
    (90, 'Bright Black'),
    (91, 'Bright Red'),
    (92, 'Bright Green'),
    (93, 'Bright Yellow'),
    (94, 'Bright Blue'),
    (95, 'Bright Magenta'),
    (96, 'Bright Cyan'),
    (97, 'Bright White')
]

for color_id, color_name in colors:
    try:
        print('\033[%dm\u25A0 Color %d: %s\033[0m' % (color_id, color_id, color_name))
    except UnicodeEncodeError:
        print('\033[%dmColor %d: %s\033[0m' % (color_id, color_id, color_name))
