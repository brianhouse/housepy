#!/usr/bin/env python3

"""

Simple drawing with cairo

still need:
arc (with ellipse), rect, text

margin

http://www.cairographics.org/samples/
http://www.tortall.net/mu/wiki/CairoTutorial


"""

import cairo, colorsys, math, time, subprocess

class Context(object):
    """The drawing context"""    
       
    def __init__(self, width=2000, height=500, background=(1., 1., 1., 1.), hsv=False, flip=True, relative=True, margin=0):
        if margin != 0:
            raise NotImplementedError
        self._width = float(width)
        self._height = float(height)
        self._hsv = hsv
        self._surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self._ctx = cairo.Context(self._surface)
        self._ctx.set_source_rgba(*background)
        self._ctx.rectangle(0, 0, self._width, self._height)
        self._ctx.fill()
        if relative:
            self._ctx.scale(self._width, self._height)
        else:
            self._ctx.scale(1.0, 1.0)
        if flip:
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
            self._ctx.move_to(*x1[0])
            for point in x1[1:]:
                self._ctx.line_to(*point)
        else:
            self._ctx.move_to(x1, y1)
            self._ctx.line_to(x2, y2)
        self._ctx.scale(1.0 / self._width, 1.0 / self._height)
        self._ctx.set_line_width(thickness)
        self._ctx.stroke()
        self._ctx.restore()                
        self._ctx.save()

    def curve(self, x1, y1, xc, yc, x2, y2, stroke=(0.0, 0.0, 0.0, 1.0), thickness=1.0):
        """Draw a curve from x1,y1 to x2,y2 with control point xc, yc"""  
        stroke = self._handle_color(stroke)
        self._ctx.set_source_rgba(*stroke)
        self._ctx.set_line_cap(cairo.LINE_CAP_SQUARE)        
        self._ctx.move_to(x1, y1)
        self._ctx.curve_to(xc, yc, xc, yc, x2, y2)
        self._ctx.scale(1.0 / self._width, 1.0 / self._height)
        self._ctx.set_line_width(thickness)
        self._ctx.stroke()
        self._ctx.restore()                
        self._ctx.save()  

    def plot(self, signal, stroke=(0.0, 0.0, 0.0, 1.0), thickness=1.0):
        self.line([(float(i) / len(signal), sample) for (i, sample) in enumerate(signal)], stroke=stroke, thickness=thickness)        

    def arc(self, center_x, center_y, radius_x, radius_y=None, start=0, end=360, stroke=(0.0, 0.0, 0.0, 1.0), thickness=1.0, fill=None):
        """ Draw an arc / ellipse / circle / pieslice. 'start' and 'end' are angles in degrees; 0 is 3:00 and degrees move clockwise.
            Specify both radius_x and radius_y to make ellipses; fill to make a pie slice.
        """        
        stroke = self._handle_color(stroke)
        fill = self._handle_color(fill)
        if radius_y is None:
            radius_y = radius_x
        # print(radius_x)
        # print(radius_y)
        # if fill:    
        #     fill = self._handle_color(fill)
        #     brush = aggdraw.Brush(fill[:3], fill[3]) 
        # coords = (self._horiz(center_x - radius_x), self._vert(center_y - radius_y), self._horiz(center_x + radius_x), self._vert(center_y + radius_y))                         
        # if self._flip:
        #     coords = coords[0], coords[3], coords[2], coords[1]
        # else:                
        #     tmp = 360 - start
        #     start = 360 - end
        #     end = tmp


        # circle only
        self._ctx.arc(center_x, center_y, radius_x, 0, 2*math.pi)

        # if start == 0 and end == 360:
        #     self._ctx.ellipse(coords, pen, brush)        
        # elif fill:
        #     self._ctx.pieslice(coords, start, end, pen, brush)
        # else:    
        #     self._ctx.arc(coords, start, end, pen)            

        self._ctx.scale(1.0 / self._width, 1.0 / self._height)
        self._ctx.set_line_width(thickness)
        if fill is not None:
            self._ctx.set_source_rgba(*fill)
            self._ctx.fill_preserve()
        self._ctx.set_source_rgba(*stroke)
        self._ctx.stroke()            
        self._ctx.restore()                
        self._ctx.save()

        # need fill

        # 
        # self._verify_context()
        # stroke = self._handle_color(stroke)
        # pen = aggdraw.Pen(stroke[:3], thickness, stroke[3])
        # if type(x1) == tuple or type(x1) == list:
        #     points = []
        #     for point in x1:
        #         points.extend((self._horiz(point[0]), self._vert(point[1])))
        #     self._ctx.line(points, pen)
        # else:            
        #     self._ctx.line((self._horiz(x1), self._vert(y1), self._horiz(x2), self._vert(y2)), pen)
        # self._valid = False


    def output(self, filename=None):
        self._ctx.stroke() # commit to surface
        if filename is None or '.' not in filename:
            if filename is None:
                filename = '' 
            elif filename[-1] != "/":
                filename = "%s/" % filename
            filename = "%s%s.png" % (filename, int(time.time() * 1000))
        self._surface.write_to_png(filename) # write to file
        subprocess.call(["open", filename])

