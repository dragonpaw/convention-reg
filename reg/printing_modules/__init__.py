from reportlab.lib.units import inch
from reportlab.lib import colors

class BaseElement(object):
    '''Parent for various printable elements.'''
    def __init__(self, x, y, color='black'):
        self.x = x
        self.y = y
        self.color = color

    def color():
        doc = "Get/set the color, as needed for PDFs."
        def fget(self):
            return self._color
        def fset(self, value):
            self._color = colors.toColor(str(value))
        def fdel(self):
            del self._color
        return locals()
    color = property(**color())


class Text(BaseElement):
    '''Element representing text to be printed.

    Required:
        x, y: Start location.
        font: Name of the font to use. (Currently only supports default PDF fonts.)
        size: Size of the text. (in points)
        text: The text to render.
    Optional:
        color: Black by default.
        alignment: Centered by default. ('left', 'right' also options.)
    '''

    def __init__(self, x, y, font, size, text, color='black', alignment='center'):
        super(Text, self).__init__(x=x, y=y, color=color)
        self.font = font
        self.size = size
        self.text = str(text)
        self.alignment = alignment

    def render_to_canvas(self, canvas):
        canvas.setFillColor(self.color)
        canvas.setFont(self.font, self.size)

        if self.alignment == 'left':
            canvas.drawString(self.x, self.y, self.text)
        elif self.alignment == 'center':
            canvas.drawCentredString(self.x, self.y, self.text)
        elif self.alignment == 'right':
            canvas.drawRightString(self.x, self.y, self.text)
        else:
            raise ValueError(
                "Alignment not one of 'left', 'right' or 'center': {0}".format(
                    alignment
                )
            )


class Box(BaseElement):
    '''Element representing box to be printed.

    Required:
        x, y: Start location.
        height
        width:
    Optional:
        color: Black by default.
        fill: To fill the box or not. (Default: True)
        stroke: To outline the box or not. (Default False)
    '''
    def __init__(self, x, y, height, width, color='black', fill=True, stroke=False):
        super(Box, self).__init__(x=x, y=y, color=color)
        self.height = height
        self.width = width
        self.fill = fill
        self.stroke = stroke

    def render_to_canvas(self, canvas):
        canvas.setFillColor(self.color)
        canvas.rect(
            self.x,
            self.y,
            self.width,
            self.height,
            stroke=self.stroke,
            fill=self.fill
        )
