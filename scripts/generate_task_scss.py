import os.path
import subprocess
import sys
import textwrap

import webcolors
from x256.x256 import to_rgb


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
            if value.find('#') > -1:
                value = value[0:value.find('#')+1]
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
    if color.startswith('bold'):
        color = color[5:]
    if color.startswith('bright'):
        color = color[7:]
    if color.startswith('underline'):
        color = color[10:]
    if color.startswith('color'):
        number = int(color[3:])
        r, g, b = to_rgb(number)
        return hex_rgb(r, g, b)
    if color.startswith('rgb'):
        r_, g_, b_ = color[3:]
        r, g, b = int(r_) * 40 + 55, int(g_) * 40 + 55, int(b_) * 40 + 55
        return hex_rgb(r, g, b)
    if color.startswith('gray'):
        level = int(color[4:])
        red, green, blue = [level * (255.0 / 23)] * 3
        return hex_rgb(red, green, blue)
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

    if value.find('#') > -1:
        value = value[0:value.find('#')]
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


def get_stylesheet(directives, bg, fg, modifier):
    base_styles = """
        .task-list {{
        \tbackground-color: {bg};
        \tcolor: {fg};
        }}
        .task.active {{
        \tbackground-color: {modifier}({bg}, 5%);
        }}
    """
    lines = textwrap.dedent(
        base_styles.format(
            fg=fg,
            bg=bg,
            modifier=modifier,
        )
    ).strip().split('\n')
    for selector, attributes in directives.items():
        lines.append('.task .%s {' % selector)
        for key, value in attributes.items():
            lines.append(
                '\t%s: %s;' % (
                    key,
                    value,
                )
            )
        lines.append('}')
        if 'background-color' in attributes:
            lines.append('.task.active .%s {' % selector)
            lines.append(
                '\tbackground-color: %s(%s, 5%%)' % (
                    modifier,
                    attributes['background-color']
                )
            )
            lines.append('}')
    return lines


def get_colors_and_active_modifier(filename):
    base_filename = os.path.basename(filename)
    if base_filename == 'solarized-light-256.theme':
        return '#DEDEDE', '#202020', 'lighten'
    return '#202020', '#DEDEDE', 'darken'


def get_styles(filename):
    directives = get_directives(filename)
    processed = process_directives(directives)
    bg, fg, modifier = get_colors_and_active_modifier(filename)
    return get_stylesheet(processed, bg, fg, modifier)


def generate_all_styles(path_to_styles, final_directory):
    staging_directory = final_directory.rstrip('/') + '.tmp'
    try:
        os.mkdir(staging_directory)
    except OSError:
        pass
    try:
        os.mkdir(final_directory)
    except OSError:
        pass

    for filename in os.listdir(path_to_styles):
        if os.path.splitext(filename)[1] != '.theme':
            continue
        staging_path = os.path.join(
            os.path.dirname(__file__),
            staging_directory,
            '%s.scss' % filename
        )
        final_path = os.path.join(
            os.path.dirname(__file__),
            final_directory,
            '%s.css' % filename
        )
        with open(staging_path, 'w') as output:
            output.write(
                '\n'.join(get_styles(os.path.join(path_to_styles, filename)))
            )
        subprocess.call(
            [
                'node-sass',
                staging_path,
                final_path
            ]
        )
        os.unlink(staging_path)
    os.rmdir(staging_directory)


if __name__ == '__main__':
    if os.path.isdir(sys.argv[1]):
        generate_all_styles(sys.argv[1], sys.argv[2])
    else:
        colors = get_styles(sys.argv[1])
        for color in colors:
            print color
