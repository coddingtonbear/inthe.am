import sys

import webcolors


DEFAULT_FOREGROUND = '#BBBBBB'


def get_directives(filename):
    directives = {}
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith('#') or not line.strip():
                continue
            directive, value = line.split('=')
            if not directive.startswith('color.'):
                continue
            directives[directive] = value
    return directives


def hex_from_int(value):
    return hex(int(value))[2:].zfill(2)


def hex_rgb(r, g, b):
    return '#%s%s%s' % (
        hex_from_int(r),
        hex_from_int(g),
        hex_from_int(b),
    )


def get_color(color):
    if color.startswith('rgb'):
        r_, g_, b_ = color[3:]
        r, g, b = int(r_) * 40 + 55, int(g_) * 40 + 55, int(b_) * 40 + 55
        return hex_rgb(r, g, b)
    if color.startswith('gray'):
        level = int(color[4:])
        r, g, b = [255 - (level * (256.0 / 23))] * 3
        return hex_rgb(r, g, b)
    try:
        return webcolors.name_to_hex(color)
    except:
        pass
    raise ValueError('No known color for %s' % color)


def process_key(key):
    return key[6:].replace('.', '__')


def process_value(value):
    value = value.strip()

    fg = None
    bg = None
    style = {
    }

    if not value:
        return style

    value = value.split('on')
    if len(value) == 1:
        fg = value[0].strip()
    else:
        fg = value[0].strip()
        bg = value[1].strip()

    if fg:
        try:
            style['color'] = get_color(fg)
        except ValueError:
            pass
    if bg:
        try:
            style['background-color'] = get_color(bg)
        except ValueError:
            pass

    return style


def process_directives(directives):
    processed = {}
    for key, value in directives.items():
        processed[process_key(key)] = process_value(value)
    return processed


def get_stylesheet(directives):
    for selector, attributes in directives.items():
        print '.task .%s {' % selector
        for key, value in attributes.items():
            print '\t%s: %s;' % (
                key,
                value,
            )
        print '}'
        if 'background-color' in attributes:
            print '.task.active .%s {' % selector
            print '\tbackground-color: darken(%s, 10%%)' % (
                attributes['background-color']
            )
            print '}'


def get_styles(filename):
    directives = get_directives(filename)
    processed = process_directives(directives)
    get_stylesheet(processed)


if __name__ == '__main__':
    colors = get_styles(sys.argv[1])
