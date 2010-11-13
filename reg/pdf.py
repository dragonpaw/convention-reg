from reportlab.lib.units import inch

# w = width, h = height, fonts come from PDF spec.
# alignments can be 'left', 'right' or 'center'.
pos = {
    'affiliation': {
        'x': 0.03*inch,
        'y': 1.66*inch,
        'w': 3.45*inch,
        'h': 0.3*inch,
        'text_x': 1.75*inch,
        'text_y': 1.75*inch,
        'font': 'Helvetica-Bold',
        'font_size': 14,
        'alignment': 'center',
    },
    'age': {
        'x': 0.03*inch,
        'y': 0.03*inch,
        'w': 0.2*inch,
        'h': 1.93*inch,
        'text_x': 0.35/2.0*inch,
        'text_y': 1.75*inch,
        'font': 'Helvetica-Bold',
        'font_size': 20,
        'alignment': 'center',
    },
    'name1': {
        'x': 1.75*inch,
        'y': .81*inch,
        'font': 'Helvetica-Bold',
        'font_size': 18,
        'alignment': 'left',
    },
    'name2': {
        'x': 1.75*inch,
        'y': 0.5*inch,
        'font': 'Helvetica',
        'font_size': 8,
        'alignment': 'left',
    },
    'city_state': {
        'x': 1.75*inch,
        'y': 0.37*inch,
        'font': 'Helvetica',
        'font_size': 10,
        'alignment': 'left',
    },
    'number': {
        'x': 3.4*inch,
        'y': 1.75*inch,
        'font': 'Helvetica-Bold',
        'font_size': 12,
        'alignment': 'right',
    },
    'type_code': {
        'x': 0.3*inch,
        'y': 0.15*inch,
        'font': 'Helvetica-Bold',
        'font_size': 20,
        'alignment': 'center',
    }
}

# Controls positions of each badge on the page
start = {
    1:  (0.75*inch, 8.51*inch),
    2:  (4.25*inch, 8.51*inch),
    3:  (0.75*inch, 6.51*inch),
    4:  (4.25*inch, 6.51*inch),
    5:  (0.75*inch, 4.51*inch),
    6:  (4.25*inch, 4.51*inch),
    7:  (0.75*inch, 2.51*inch),
    8:  (4.25*inch, 2.51*inch),
    9:  (0.75*inch, 0.51*inch),
    10: (4.25*inch, 0.51*inch),
}
