import re, fontforge, unicodedata

def parse_char(param, default=None, aliases=None):
    orig_param = param

    def default_value_or_error():
        if default == (-1,):
            return (-1, "", -1, "", None)
        elif default == (None,):
            return (None, None, None, None, None)
        elif default is Exception:
            raise ValueError("invalid character parameter: %s" % repr(orig_param))
        else:
            return default

    if type(param) is float:
        if param != round(param):
            return default_value_or_error()
        param = round(param)

    if type(param) is int:
        if param not in range(0, 0x110000):
            return default_value_or_error()
        codepoint = param
        glyphname = fontforge.nameFromUnicode(param)
        return (codepoint, glyphname, codepoint, glyphname, None)

    if type(param) is not str:
        raise TypeError("invalid parameter type: %s", repr(type(param)))

    variant = None
    if "." in param:
        (param, variant) = param.split(".", 1)
    elif "--" in param:
        (param, variant) = param.split("--", 1)

    base_codepoint = None
    if len(param) == 1:
        base_codepoint = ord(param)
    elif match := re.fullmatch(r'(?:u\+|0?x)([0-9a-f]+)', param, flags=re.I):
        base_codepoint = int(match[1], 16)
    elif (char := unicodedata_lookup(param, default=None)) is not None:
        base_codepoint = ord(char)
    elif (cp := fontforge.unicodeFromName(param)) >= 0:
        base_codepoint = cp
    elif type(aliases) is dict and param in aliases:
        base_codepoint = aliases[param]
    else:
        return default_value_or_error()

    if base_codepoint not in range(0, 0x100000):
        return default_value_or_error()

    base_glyphname = fontforge.nameFromUnicode(base_codepoint)
    if variant is None:
        return (base_codepoint, base_glyphname, base_codepoint, base_glyphname, None)
    return (-1, base_glyphname + "." + variant, base_codepoint, base_glyphname, variant)

def unicodedata_lookup(param, default=None):
    try:
        return unicodedata.lookup(param)
    except KeyError:
        if default is Exception:
            raise
        return default

def test_types_of_input():
    assert(parse_char("PILE OF POO")                     == (0x1f4a9, "u1F4A9", 0x1f4a9, "u1F4A9", None))
    assert(parse_char("Pile Of Poo")                     == (0x1f4a9, "u1F4A9", 0x1f4a9, "u1F4A9", None))
    assert(parse_char("u1F4A9")                          == (0x1f4a9, "u1F4A9", 0x1f4a9, "u1F4A9", None))
    assert(parse_char("U+1F4A9")                         == (0x1f4a9, "u1F4A9", 0x1f4a9, "u1F4A9", None))
    assert(parse_char("\U0001F4A9")                      == (0x1f4a9, "u1F4A9", 0x1f4a9, "u1F4A9", None))
    assert(parse_char(0x1f4a9)                           == (0x1f4a9, "u1F4A9", 0x1f4a9, "u1F4A9", None))
    assert(parse_char(128169)                            == (0x1f4a9, "u1F4A9", 0x1f4a9, "u1F4A9", None))
    assert(parse_char(128169.0)                          == (0x1f4a9, "u1F4A9", 0x1f4a9, "u1F4A9", None))

    assert(parse_char("SNOWMAN")                         == (0x2603, "uni2603", 0x2603, "uni2603", None))
    assert(parse_char("snowman")                         == (0x2603, "uni2603", 0x2603, "uni2603", None))
    assert(parse_char("uni2603")                         == (0x2603, "uni2603", 0x2603, "uni2603", None))
    assert(parse_char("U+2603")                          == (0x2603, "uni2603", 0x2603, "uni2603", None))
    assert(parse_char("\u2603")                          == (0x2603, "uni2603", 0x2603, "uni2603", None))
    assert(parse_char(0x2603)                            == (0x2603, "uni2603", 0x2603, "uni2603", None))
    assert(parse_char(9731)                              == (0x2603, "uni2603", 0x2603, "uni2603", None))
    assert(parse_char(9731.0)                            == (0x2603, "uni2603", 0x2603, "uni2603", None))

    assert(parse_char("INVERTED EXCLAMATION MARK")       == (0x00a1, "exclamdown", 0x00a1, "exclamdown", None))
    assert(parse_char("inverted exclamation mark")       == (0x00a1, "exclamdown", 0x00a1, "exclamdown", None))
    assert(parse_char("exclamdown")                      == (0x00a1, "exclamdown", 0x00a1, "exclamdown", None))
    assert(parse_char("uni00a1")                         == (0x00a1, "exclamdown", 0x00a1, "exclamdown", None))
    assert(parse_char("U+00a1")                          == (0x00a1, "exclamdown", 0x00a1, "exclamdown", None))
    assert(parse_char("\u00a1")                          == (0x00a1, "exclamdown", 0x00a1, "exclamdown", None))
    assert(parse_char(0x00a1)                            == (0x00a1, "exclamdown", 0x00a1, "exclamdown", None))
    assert(parse_char(161)                               == (0x00a1, "exclamdown", 0x00a1, "exclamdown", None))
    assert(parse_char(161.0)                             == (0x00a1, "exclamdown", 0x00a1, "exclamdown", None))

def test_variants():
    assert(parse_char("PILE OF POO.vari")                == (-1, "u1F4A9.vari", 0x1f4a9, "u1F4A9", "vari"))
    assert(parse_char("Pile Of Poo.vari")                == (-1, "u1F4A9.vari", 0x1f4a9, "u1F4A9", "vari"))
    assert(parse_char("u1F4A9.vari")                     == (-1, "u1F4A9.vari", 0x1f4a9, "u1F4A9", "vari"))
    assert(parse_char("U+1F4A9.vari")                    == (-1, "u1F4A9.vari", 0x1f4a9, "u1F4A9", "vari"))
    assert(parse_char("\U0001F4A9.vari")                 == (-1, "u1F4A9.vari", 0x1f4a9, "u1F4A9", "vari"))
    assert(parse_char("SNOWMAN.vari")                    == (-1, "uni2603.vari", 0x2603, "uni2603", "vari"))
    assert(parse_char("snowman.vari")                    == (-1, "uni2603.vari", 0x2603, "uni2603", "vari"))
    assert(parse_char("uni2603.vari")                    == (-1, "uni2603.vari", 0x2603, "uni2603", "vari"))
    assert(parse_char("U+2603.vari")                     == (-1, "uni2603.vari", 0x2603, "uni2603", "vari"))
    assert(parse_char("\u2603.vari")                     == (-1, "uni2603.vari", 0x2603, "uni2603", "vari"))

    assert(parse_char("PILE OF POO--vari")               == (-1, "u1F4A9.vari", 0x1f4a9, "u1F4A9", "vari"))
    assert(parse_char("Pile Of Poo--vari")               == (-1, "u1F4A9.vari", 0x1f4a9, "u1F4A9", "vari"))
    assert(parse_char("u1F4A9--vari")                    == (-1, "u1F4A9.vari", 0x1f4a9, "u1F4A9", "vari"))
    assert(parse_char("U+1F4A9--vari")                   == (-1, "u1F4A9.vari", 0x1f4a9, "u1F4A9", "vari"))
    assert(parse_char("\U0001F4A9--vari")                == (-1, "u1F4A9.vari", 0x1f4a9, "u1F4A9", "vari"))
    assert(parse_char("SNOWMAN--vari")                   == (-1, "uni2603.vari", 0x2603, "uni2603", "vari"))
    assert(parse_char("snowman--vari")                   == (-1, "uni2603.vari", 0x2603, "uni2603", "vari"))
    assert(parse_char("uni2603--vari")                   == (-1, "uni2603.vari", 0x2603, "uni2603", "vari"))
    assert(parse_char("U+2603--vari")                    == (-1, "uni2603.vari", 0x2603, "uni2603", "vari"))
    assert(parse_char("\u2603--vari")                    == (-1, "uni2603.vari", 0x2603, "uni2603", "vari"))

def test_failures():
    assert(parse_char(128169.3, default=-1)              == -1)
    assert(parse_char(9731.3, default=-1)                == -1)
    assert(parse_char(-1, default=-1)                    == -1)
    assert(parse_char(0x110000, default=-1)              == -1)
    assert(parse_char("PILE OF POOP", default=-1)        == -1)
    assert(parse_char("PILE OF POOP.vari", default=-1)   == -1)

def test_out_of_range():
    assert(parse_char("U+110000", default=-1)            == -1)
    assert(parse_char(0x110000, default=(-1,))           == (-1, "", -1, "", None))
    assert(parse_char(0x110000, default=(None,))         == (None, None, None, None, None))
    assert(parse_char(0x110000, default=None)            == None)
    assert(parse_char(0x110000, default="None")          == "None")

def test_types_of_default_return_values():
    assert(parse_char(-1, default=(-1,))                 == (-1, "", -1, "", None))
    assert(parse_char(-1, default=(None,))               == (None, None, None, None, None))
    assert(parse_char(-1, default=None)                  == None)
    assert(parse_char(-1, default="None")                == "None")
    assert(parse_char("PILE OF POOP", default=(-1,))     == (-1, "", -1, "", None))
    assert(parse_char("PILE OF POOP", default=(None,))   == (None, None, None, None, None))
    assert(parse_char("PILE OF POOP", default=None)      == None)
    assert(parse_char("PILE OF POOP", default="None")    == "None")

def test_exceptions():
    try:
        value = parse_char("PILE OF POOP", default=Exception)
    except ValueError as e:
        assert(str(e) == "invalid character parameter: 'PILE OF POOP'")
    try:
        value = parse_char(-1, default=Exception)
    except ValueError as e:
        assert(str(e) == "invalid character parameter: -1")

def test_aliases():
    aliases = {
        0x21f4a9: 0x1f4a9,
        "PILE OF POOP": 0x1f4a9,
        0x212603: "SNOWMAN",
        "SNOWDUDE": "SNOWMAN",
    }

    assert(parse_char("SNOWDUDE", aliases=aliases)       == (0x2603, "uni2603", 0x2603, "uni2603", None))
    assert(parse_char("SNOWDUDE.vari", aliases=aliases)  == (-1, "uni2603.vari", 0x2603, "uni2603", "vari"))
    assert(parse_char("SNOWDUDE--vari", aliases=aliases) == (-1, "uni2603.vari", 0x2603, "uni2603", "vari"))
    assert(parse_char("PILE OF POOP", aliases=aliases)       == (0x1f4a9, "u1F4A9", 0x1f4a9, "u1F4A9", None))
    assert(parse_char("PILE OF POOP.vari", aliases=aliases)  == (-1, "u1F4A9.vari", 0x1f4a9, "u1F4A9", "vari"))
    assert(parse_char("PILE OF POOP--vari", aliases=aliases) == (-1, "u1F4A9.vari", 0x1f4a9, "u1F4A9", "vari"))

if __name__ == "__main__":
    test_types_of_input()
    test_variants()
    test_failures()
    test_types_of_default_return_values()
    test_out_of_range()
    test_exceptions()
    # test_aliases()
    print("OK")
