# -*- comment-column: 80; fill-column: 132 -*-
import os, re, unicodedata, fontforge, sys
from types import SimpleNamespace

sys.path.append(os.path.realpath(os.path.dirname(__file__)) + "/../lib")
from parse_char.parse_char import parse_char

def table(field_names, rows):
    if type(field_names) == list and type(rows) == list:
        strs = []
        max_lengths = [max([len(field_name), *[ len(row[field_name]) for row in rows ]]) for field_name in field_names]
        field_tuples = list(zip(max_lengths, field_names))
        strs.append(" | ".join([("%-*s" % (tuple[0], tuple[1])) for tuple in field_tuples]))
        strs.append("-|-".join([("-" * tuple[0]) for tuple in field_tuples]))
        for row in rows:
            strs.append(" | ".join(["%-*s" % (tuple[0], row[tuple[1]]) for tuple in field_tuples]))
        return "\n".join(strs)
    raise Exception("invalid arguments")

def table_keys(rows):
    field_names = []
    for row in list(rows):
        for key in row.keys():
            if key not in field_names:
                field_names.append(key)
    return field_names

def table_dict(rows):
    field_names = table_keys(rows)
    return table(field_names, rows)

def flatten(values):
    result = []
    for item in values:
        if type(item) == list:
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

def tsv_value_escape(str):
    str = str.replace("\\", "\\\\")
    str = str.replace("\t", "\\t")
    str = str.replace("\r", "\\r")
    str = str.replace("\n", "\\n")
    return str

# excel dialect
def csv_value_escape(str):
    if '"' not in str and ',' not in str and '\r' not in str and '\n' not in str:
        return str
    str = str.replace('"', '""')
    return '"' + str + '"'

def camel_case(str):
    str = re.sub(r'^[^A-Za-z0-9]+', '', str)
    str = re.sub(r'[^A-Za-z0-9]+$', '', str)
    str = re.sub(r'\'+', '', str)
    words = re.split(r'[^A-Za-z0-9]+', str)
    words = [words[i].lower() if i == 0 else words[i][0].upper() + words[i][1:] for i in range(0, len(words))]
    return "".join(words)

MAX_VERBOSE_SILENT = 2

def open_font(filename, verbose=False, flags=()):
    if verbose is None:
        verbose = False
    else:
        verbose = int(verbose)
    try:
        if verbose:
            print("Opening %s" % filename)
        font = fontforge.open(filename, flags)
    except OSError as e:
        if e.args[0] != "Open failed":
            raise
        return
    return font

def u(codepoint):
    if codepoint < 0:
        return "%-8d" % codepoint
    return "U+%04X" % codepoint

def save_font(font, dest_filename, verbose=False):
    (_, ext) = os.path.splitext(dest_filename)
    if ext == '.sfd':
        if verbose:
            print("Saving %s" % dest_filename)
        font.save(dest_filename)
    else:
        if verbose:
            print("Generating %s" % dest_filename)
        font.generate(dest_filename)

def compute_dest_filename(source_filename, dest_filename, font_name=None):
    (source_dirname, source_basename) = os.path.split(source_filename)
    (source_basename_root, source_ext) = os.path.splitext(source_basename)
    if re.fullmatch(r'\.[^./]+', dest_filename):
        basename_root = font_name if font_name is not None else source_basename_root
        return os.path.join(source_filename, basename_root + dest_filename)
    if font_name is not None:
        if dest_filename.find('{}') >= 0:
            return dest_filename.replace("{}", font_name, 1)
        raise Exception("""\
When converting from font collection files, each destination filename must
either be an extension (e.g., '.ttf') or a filename containing at least one
occurrence of '{}' (e.g., '/home/xyz/{}.ttf')""")
    return dest_filename

is_silent = None

def get_fonts_in(filenames, close=True, verbose=0, ttc=True, open_font=True, names=False):
    if not open_font and not names:
        raise Exception("get_fonts_in without open_font or names does not make sense")
    global is_silent
    if is_silent is None:
        is_silent = verbose < 2
    for filename in filenames:
        fonts_in_file = fontforge.fontsInFile(filename)
        if (not ttc) and len(fonts_in_file) >= 2:
            raise Exception("get_fonts_in: .ttc files not supported when ttc=%s is specified" % repr(ttc))
        font_structs = []
        if len(fonts_in_file) < 2:
            font_structs = [SimpleNamespace(
                filename=filename,
                filename_open=filename,
                filename_noext=os.path.splitext(filename)[0],
                fontname=None,
                ttc=False,
            )]
        else:
            font_structs = [SimpleNamespace(
                filename=filename,
                filename_open="%s(%s)" % (filename, font_in_file),
                filename_noext="%s(%s)" % (os.path.splitext(filename)[0], font_in_file),
                fontname=font_in_file,
                ttc=True,
            ) for font_in_file in fonts_in_file]
        for font_struct in font_structs:
            if not open_font:
                yield font_struct
                continue
            try:
                print("Opening %s" % font_struct.filename_open)
                font = fontforge.open(font_struct.filename_open)
                print("Opened")
            except Exception as err:
                raise err
            if names:
                if font_struct.fontname is None:
                    font_struct.fontname = font.fontname
                font_struct.font = font
                yield font_struct
            else:
                yield font
            if close:
                font.close()

def rect(glyph, x1, x2, y1, y2):
    print("rect(%s, %d, %d, %d, %d)" % (glyph, x1, x2, y1, y2))
    pen = glyph.glyphPen(replace=False)
    pen.moveTo((x1, y1))
    pen.lineTo((x2, y1))
    pen.lineTo((x2, y2))
    pen.lineTo((x1, y2))
    pen.closePath()
    pen = None

def poly(glyph, pairs):
    pen = glyph.glyphPen(replace=False)
    x = pairs[0][0]
    y = pairs[0][1]
    pen.moveTo((x, y))
    for pair in pairs[1:]:
        if len(pair) > 2:
            if pair[0] == X:
                horizontal = True
            elif pair[0] == Y:
                horizontal = False
            else:
                raise Exception("tuple of more than 2 coordinates must start with X or Y")
            for i in range(1, len(pair)):
                if horizontal:
                    x = pair[i]
                else:
                    y = pair[i]
                pen.lineTo((x, y))
                horizontal = not horizontal
        elif pair[0] == X:
            x = pair[1]
            pen.lineTo((x, y))
        elif pair[0] == Y:
            y = pair[1]
            pen.lineTo((x, y))
        else:
            (x, y) = pair
            pen.lineTo((x, y))
    pen.closePath()
    pen = None

def clip(glyph, x1, y1, x2, y2):
    contour = fontforge.contour()
    contour.moveTo((x1, y1))
    contour.lineTo((x2, y1))
    contour.lineTo((x2, y2))
    contour.lineTo((x1, y2))
    contour.closed = True
    contour = None
    glyph.layers["Fore"] += clipContour
    glyph.intersect()

def GA(font, what):
    """Convenience function.

Returns an array containing a single item, that item being a FontForge
glyph object.

Used for `for glyph in GA("CHARACTER NAME")` constructs, e.g.,

    for glyph in GA("BOX DRAWINGS HEAVY TRIPLE DASH VERTICAL"):
        for i in range(0, 3):
            rect(glyph, x1_heavy, x2_heavy, dash_vert[3][i*2], dash_vert[3][i*2+1])
    for glyph in GA("BOX DRAWINGS LIGHT QUADRUPLE DASH HORIZONTAL"):
        for i in range(0, 4):
            rect(glyph, dash_horiz[4][i*2], dash_horiz[4][i*2+1], y1_light, y2_light)

for visual separation.
"""
    g = None
    if type(what) == str:
        if len(what) == 1:
            g = font.createChar(ord(what))
        else:
            g = font.createChar(ord(unicodedata.lookup(what)))
    elif type(what) == int:
        g = font.createChar(what)
    else:
        raise Exception("GA: invalid argument type")
    g.clear()
    return [g]

def u(codepoint, pad=False):
    result = None
    if codepoint < 0:
        result = "%d" % codepoint
    else:
        result = "U+%04X" % codepoint
    if pad:
        result = "%-8s" % result
    return result

# PARSE_CHAR
def parse_char_str(glyphname, default=Exception, aliases=None):
    return parse_char(glyphname, default=default, aliases=aliases)

def unicodedata_lookup(name, default=None):
    try:
        return unicodedata.lookup(name)
    except KeyError:
        if default is Exception:
            raise
        return default

def unicodedata_name(char, default=None):
    [codepoint, char] = parse_char_arg(char)
    try:
        return unicodedata.name(char)
    except (ValueError, TypeError):
        if default is Exception:
            raise
        return default

def unicodedata_category(char, default=None):
    [codepoint, char] = parse_char_arg(char)
    try:
        return unicodedata.category(char)
    except (ValueError, TypeError):
        if default is Exception:
            raise
        return default

def parse_codepoint_argument(param, default=Exception, as_type=int, orig_param=None, aliases=None):
    try:
        return parse_char(param, aliases=aliases)[2]
    except:
        if default is Exception:
            raise
        return default

def get_base_codepoint(glyph, default=-1):
    return fontforge.unicodeFromName(glyph.glyphname.split(".")[0])

def get_base_glyphname(glyph, default=None):
    return glyph.glyphname.split(".")[0]

def get_variant_name(glyph, default=None):
    if "." in glyph.glyphname:
        return glyph.glyphname.split(".", 1)[1]
