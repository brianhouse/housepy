#!/usr/bin/env python3

"""

Simple drawing with cairo

http://www.cairographics.org/samples/
http://www.tortall.net/mu/wiki/CairoTutorial

known bugs:
- flip does not work if relative=False

"""

"""

from housepy import drawing

ctx = drawing.Context(1000, 1000, margin=50, hsv=True)

ctx.line(0, 0, 1, 1, stroke=(0., 1., 1.), thickness=10)
ctx.line(0, 1, 1, 0, stroke=(0., 1., 1.), thickness=10)
ctx.arc(0.5, 0.5, 0.5, 0.5, stroke=(.55, 1., 1.), thickness=10)

ctx.output()

"""

import colorsys, math, time, subprocess, os
import cairocffi as cairo
from . import util

class Context(object):
    """The drawing context"""    
       
    def __init__(self, width=2000, height=500, background=(1., 1., 1., 1.), hsv=False, flip=True, relative=True, margin=0):
        self._width = float(width)
        self._height = float(height)
        self._hsv = hsv
        margin_x = margin / self.width
        margin_y = margin / self.height
        self._mx = (lambda x: x + margin_x) if not relative else (lambda x: (x * (1.0 - (2.0 * margin_x))) + margin_x)
        self._my = (lambda y: y + margin_y) if not relative else (lambda y: (y * (1.0 - (2.0 * margin_y))) + margin_y)
        self._surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self._ctx = cairo.Context(self._surface)
        self._ctx.set_source_rgba(*background)
        self._ctx.rectangle(0, 0, self._width, self._height)
        self._ctx.fill()
        self.relative = relative
        if self.relative:
            self._ctx.scale(self._width, self._height)
        else:
            self._ctx.scale(1.0, 1.0)
        self.flip = flip
        if self.flip:
            self._ctx.scale(1, -1)
            self._ctx.translate(0, -1)
        self._ctx.save()

    def _handle_color(self, args):
        if args is None:
            return None
        if type(args) == float or type(args) == int:
            args = [args] * 3
        color = [0.0, 0.0, 0.0, 1.0]
        for i, arg in enumerate(args):
            color[i] = arg
            if type(arg) == int:
                color[i] /= 255.0
        if self._hsv:
            color[0], color[1], color[2] = colorsys.hsv_to_rgb(*color[:3])
        return color[0], color[1], color[2], color[3]

    """Public Methods"""

    @property
    def width(self):
        """Return the width of the drawing context."""
        return self._width
        
    @property
    def height(self):
        """Return the height of the drawing context."""        
        return self._height    

    def line(self, x1, y1=None, x2=None, y2=None, stroke=(0.0, 0.0, 0.0, 1.0), thickness=1.0):
        """Draw a line from x1,y1 to x2,y2, or between all points (as x,y pairs) in a list."""        
        stroke = self._handle_color(stroke)
        self._ctx.set_source_rgba(*stroke)
        self._ctx.set_line_cap(cairo.LINE_CAP_SQUARE)        
        if type(x1) == tuple or type(x1) == list:
            self._ctx.move_to(self._mx(x1[0][0]), self._my(x1[0][1]))
            for point in x1[1:]:
                self._ctx.line_to(self._mx(point[0]), self._my(point[1]))
        else:
            self._ctx.move_to(self._mx(x1), self._my(y1))
            self._ctx.line_to(self._mx(x2), self._my(y2))
        if self.relative:
            self._ctx.scale(1.0 / self.width, 1.0 / self.height)
        self._ctx.set_line_width(thickness)
        self._ctx.stroke()
        self._ctx.restore()                
        self._ctx.save()

    def rect(self, x, y, width, height, stroke=(0.0, 0.0, 0.0, 1.0), thickness=1.0, fill=None):
        """Draw a rectangle"""        
        stroke = self._handle_color(stroke)
        fill = self._handle_color(fill)        
        self._ctx.set_source_rgba(*stroke)
        self._ctx.set_line_cap(cairo.LINE_CAP_SQUARE)        
        self._ctx.rectangle(self._mx(x), self._my(y), self._mx(x + width), self._my(y + height))
        if self.relative:
            self._ctx.scale(1.0 / self.width, 1.0 / self.height)
        self._ctx.set_line_width(thickness)
        if fill is not None:
            self._ctx.set_source_rgba(*fill)
            self._ctx.fill_preserve()        
        self._ctx.stroke()
        self._ctx.restore()                
        self._ctx.save()        

    def curve(self, x1, y1, xc, yc, x2, y2, stroke=(0.0, 0.0, 0.0, 1.0), thickness=1.0):
        """Draw a curve from x1,y1 to x2,y2 with control point xc, yc"""  
        x1 = self._mx(x1)
        y1 = self._my(y1)
        xc = self._mx(xc)
        yc = self._my(yc)
        x2 = self._mx(x2)
        y2 = self._my(y2)
        stroke = self._handle_color(stroke)
        self._ctx.set_source_rgba(*stroke)
        self._ctx.set_line_cap(cairo.LINE_CAP_SQUARE)        
        self._ctx.move_to(x1, y1)
        self._ctx.curve_to(xc, yc, xc, yc, x2, y2)
        if self.relative:
            self._ctx.scale(1.0 / self.width, 1.0 / self.height)
        self._ctx.set_line_width(thickness)
        self._ctx.stroke()
        self._ctx.restore()                
        self._ctx.save()  

    def plot(self, signal, stroke=(0.0, 0.0, 0.0, 1.0), thickness=1.0):
        self.line([(float(i) / len(signal), sample) for (i, sample) in enumerate(signal)], stroke=stroke, thickness=thickness)        

    def arc(self, center_x, center_y, radius_x=None, radius_y=None, start=0, end=360, stroke=(0.0, 0.0, 0.0, 1.0), thickness=1.0, fill=None):
        """ Draw an arc / ellipse / circle / pieslice. 'start' and 'end' are angles in degrees; 0 is 3:00 and degrees move clockwise.
            Specify both radius_x and radius_y to make ellipses; fill to make a pie slice.
        """        
        stroke = self._handle_color(stroke)
        fill = self._handle_color(fill)
        if radius_x is None and radius_y is None:
            raise ValueError
        elif radius_x is None:
            radius_x = radius_y * (self.height / self.width)
        elif radius_y is None:
            radius_y = radius_x * (self.width / self.height)

        if self.flip:
            tmp = 360 - start
            start = 360 - end
            end = tmp

        center_x = self._mx(center_x)
        center_y = self._my(center_y)

        self._ctx.translate(center_x, center_y)  
        self._ctx.scale(radius_x, radius_y)
        self._ctx.arc(0.0, 0.0, 1.0, start, math.radians(end))

        if self.relative:
            self._ctx.scale(1.0 / self.width, 1.0 / self.height)
        self._ctx.set_line_width(thickness)
        if fill is not None:
            self._ctx.set_source_rgba(*fill)
            self._ctx.fill_preserve()
        self._ctx.set_source_rgba(*stroke)
        self._ctx.stroke()            
        self._ctx.restore()                
        self._ctx.save()


    def label(self, x, y, text, stroke=(0., 0., 0., 1.), font="Monaco", size=12):
        x = self._mx(x)
        y = self._my(y)        
        stroke = self._handle_color(stroke)
        self._ctx.set_source_rgba(*stroke)
        self._ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self._ctx.set_font_size(size)
        if self.relative: 
            self._ctx.scale(1.0 / self.width, 1.0 / self.height)    
            x *= self.width
            y *= self.height            
        if self.flip:
            self._ctx.scale(1, -1)
            self._ctx.translate(0, -self.height)
            y = self.height - y
        self._ctx.move_to(x, y) 
        self._ctx.show_text(text)   
        self._ctx.restore()                
        self._ctx.save()


    def image(self, filename, x=0, y=None):
        if y is None:
            if self.relative:
                y = 1 if self.flip else 0
            else:
                y = self.height if self.flip else 0
        image = cairo.ImageSurface.create_from_png(filename)
        if self.relative: 
            self._ctx.scale(1.0 / self.width, 1.0 / self.height)    
            x *= self.width
            y *= self.height            
        if self.flip:
            self._ctx.scale(1, -1)
            self._ctx.translate(0, -self.height)
            y = self.height - y        
        self._ctx.set_source_surface(image, x, y)
        self._ctx.paint()        
        self._ctx.restore()                
        self._ctx.save()


    def output(self, filename=None, open_file=True):
        self._ctx.stroke() # commit to surface
        if filename is None or '.' not in filename:
            if filename is None:
                filename = '' 
            else:
                if not os.path.isdir(filename):
                    os.makedirs(filename)
            filename = os.path.abspath(os.path.join(filename, "%s.png" % util.timestamp()))
        self._surface.write_to_png(filename) # write to file
        if open_file:
            subprocess.call(["open", filename])

