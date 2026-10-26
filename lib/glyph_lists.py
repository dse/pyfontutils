__all__ = [
    "WGL4",
    "AGLFN",
    "AGL",
    "W1G",
    "CP437",
    "WGL4_PRIVATE_USE",
    "ZAPF_DINGBATS",
    "SECS",
    "GLYPH_LISTS",
]

from glyph_list_wgl4          import WGL4, WGL4_PRIVATE_USE
from glyph_list_w1g           import W1G
from glyph_list_aglfn         import AGLFN
from glyph_list_agl           import AGL
from glyph_list_cp437         import CP437
from glyph_list_zapf_dingbats import ZAPF_DINGBATS
from glyph_list_secs          import SECS
from glyph_list_mes_1         import MES_1
from glyph_list_mes_2         import MES_2
from glyph_list_mes_3b        import MES_3B
# from glyph_list_din_91379     import DIN_91379

GLYPH_LISTS = [
    {
        "name": "Windows Glyph List 4",
        "abbr": "WGL4",
        "list": WGL4
    },
    {
        "name": "World Glyph Set",
        "abbr": "W1G",
        "list": W1G
    },
    {
        "name": "Adobe Glyph List for New Fonts",
        "abbr": "AGLFN",
        "list": AGLFN
    },
    # {
    #     "name": "Adobe Glyph List",
    #     "abbr": "AGL",
    #     "list": AGL
    # },
    {
        "name": "ITC Zapf Dingbats",
        "abbr": "Zapf Dingbats",
        "list": ZAPF_DINGBATS
    },
    {
        "name": "Simple European Character Set",
        "abbr": "SECS",
        "list": SECS
    },
    {
        "name": "Multilingual European Subset 1",
        "abbr": "MES-1",
        "list": MES_1,
    },
    {
        "name": "Multilingual European Subset 2",
        "abbr": "MES-2",
        "list": MES_2,
    },
    # {
    #     "name": "Multilingual European Subset 3B",
    #     "abbr": "MES-3b",
    #     "list": MES_3B,
    # },
    # {
    #     "name": "DIN-91379",
    #     "abbr": "DIN-91379",
    #     "list": DIN_91379,
    # },
]
