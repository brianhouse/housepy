#!/usr/bin/env python
"""
    Requires AVBin: http://avbin.github.io/AVbin/Download.html
    python 3.X video playback stalls for some reason, this will run in python 2.7
    For best results, convert to JPEG / WAV and deinterlace

"""

import time, pyglet, json, sys
from pyglet.window import key
from pyglet.gl import *
from . import dispatcher, log


def draw_rect(x, y, width, height, color=(1., 1., 1., 1.)):
    glColor4f(*color)
    glBegin(GL_POLYGON) # GL_LINE_LOOP
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()
    glColor4f(1., 1., 1., 1.)


class Control(pyglet.event.EventDispatcher):

    def __init__(self, parent):
        super(Control, self).__init__()
        self.parent = parent
        self.x = 0
        self.y = 0
        self.width = 10
        self.height = 10

    def hit_test(self, x, y):
        return (self.x < x < self.x + self.width and self.y < y < self.y + self.height)

    def capture_events(self):
        self.parent.push_handlers(self)

    def release_events(self):
        self.parent.remove_handlers(self)  


class Button(Control):

    def __init__(self):
        Control.__init__(self)
        self.charged = False

    def draw(self):
        if self.charged:
            draw_rect(self.x, self.y, self.width, self.height, (1., 0., 0., 1.))
        else:
            draw_rect(self.x, self.y, self.width, self.height)
        self.draw_label()

    def on_mouse_press(self, x, y, button, modifiers):
        self.capture_events()
        self.charged = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.charged = self.hit_test(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.release_events()
        if self.hit_test(x, y):
            self.dispatch_event('on_press')
        self.charged = False

Button.register_event_type('on_press')


class Slider(Control):

    THUMB_WIDTH = 6
    THUMB_HEIGHT = 10
    GROOVE_HEIGHT = 2

    def draw(self):
        center_y = self.y + self.height / 2
        draw_rect(self.x, center_y - self.GROOVE_HEIGHT / 2, self.width, self.GROOVE_HEIGHT)
        pos = self.x + self.value * self.width / (self.max - self.min)
        draw_rect(pos - self.THUMB_WIDTH / 2, center_y - self.THUMB_HEIGHT / 2, self.THUMB_WIDTH, self.THUMB_HEIGHT)

    def coordinate_to_value(self, x):
        return float(x - self.x) / self.width * (self.max - self.min) + self.min

    def on_mouse_press(self, x, y, button, modifiers):
        value = self.coordinate_to_value(x)
        self.capture_events()
        self.dispatch_event('on_begin_scroll')
        self.dispatch_event('on_change', value)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        value = min(max(self.coordinate_to_value(x), self.min), self.max)
        self.dispatch_event('on_change', value)
    
    def on_mouse_release(self, x, y, button, modifiers):
        self.release_events()
        self.dispatch_event('on_end_scroll')

Slider.register_event_type('on_begin_scroll')
Slider.register_event_type('on_end_scroll')
Slider.register_event_type('on_change')


class VideoPlayer(pyglet.window.Window, dispatcher.Dispatcher):

    GUI_PADDING = 4    
    GUI_BUTTON_HEIGHT = 16    

    def __init__(self, filename, seek=True):
        pyglet.window.Window.__init__(self, caption=filename, resizable=False)
        dispatcher.Dispatcher.__init__(self)
        log.info("VideoPlayer %s" % filename)
        self.player = pyglet.media.Player()
        source = pyglet.media.load(filename)
        self.player.queue(source)
        self.player.push_handlers(self)
        self.player.eos_action = self.player.EOS_PAUSE
        self.player.set_handler("on_eos", self.on_eos)        
        self.set_default_video_size()
        self.set_visible(True)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)        
        self.slider = Slider(self)
        self.slider.x = self.GUI_PADDING
        self.slider.y = self.GUI_PADDING * 2 + self.GUI_BUTTON_HEIGHT
        self.slider.on_begin_scroll = lambda: self.player.pause()
        # self.slider.on_end_scroll = lambda: self.player.play()
        self.slider.on_change = lambda value: self.player.seek(value)    
        self.gui_update_source()                
        self.controls = []
        if seek:
            self.controls.append(self.slider)

    def play(self):
        self.player.play()       
        pyglet.app.run()         

    def get_video_size(self):
        if not self.player.source or not self.player.source.video_format:
            return 0, 0
        video_format = self.player.source.video_format
        width = video_format.width
        height = video_format.height
        if video_format.sample_aspect > 1:
            width *= video_format.sample_aspect
        elif video_format.sample_aspect < 1:
            height /= video_format.sample_aspect
        return width, height

    def set_default_video_size(self):
        width, height = self.get_video_size()
        self.set_size(width, height)

    def gui_update_source(self):
        if self.player.source:
            source = self.player.source
            self.slider.min = 0.
            self.slider.max = source.duration

    def on_resize(self, width, height):
        super(VideoPlayer, self).on_resize(width, height)
        self.slider.width = width - self.GUI_PADDING * 2        
        video_width, video_height = self.get_video_size()
        display_aspect = width / float(height)
        video_aspect = video_width / float(video_height)
        if video_aspect > display_aspect:
            self.video_width = width
            self.video_height = width / video_aspect
        else:
            self.video_height = height
            self.video_width = height * video_aspect
        self.video_x = (width - self.video_width) / 2
        self.video_y = (height - self.video_height) / 2

    def on_mouse_press(self, x, y, button, modifiers):
        for control in self.controls:
            if control.hit_test(x, y):
                control.on_mouse_press(x, y, button, modifiers)
            else:
                self.fire('click', (self.player.time, x, y, modifiers))

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.dispatch_event('on_close')
        elif symbol == key.SPACE:
            self.on_play_pause()        
        elif symbol == key.LEFT or symbol == key.RIGHT:
            if self.player.playing:
                self.player.pause()
            v = 1. / 30. # it will just drop keypresses if v < fps
            self.player.seek(self.player.time + (v if symbol == key.RIGHT else -1 * v))
        else:
            try:
                self.fire("%s_release" % chr(symbol), self.player.time)
                self.fire('key', (self.player.time, chr(symbol)))
            except ValueError:
                pass

    def on_key_release(self, symbol, modifiers):
        try:
            self.fire(chr(symbol), self.player.time)
            self.fire('key_release', (self.player.time, chr(symbol)))
        except ValueError:
            pass

    def on_play_pause(self):
        if self.player.playing:
            self.player.pause()
        else:
            if self.player.time >= self.player.source.duration:
                self.player.seek(0)
            self.player.play()                

    def on_eos(self):
        log.info("VideoPlayer.on_eos")
        self.on_close()
        pyglet.app.exit()

    def on_close(self):
        log.info("VideoPlayer.on_close")
        self.player.pause()
        self.close()

    def on_draw(self):
        self.clear()
        if self.player.source.duration - self.player.time < 0.5:    # problem with hanging videos, so cutting half a second...
            self.on_eos()
        if self.player.source and self.player.source.video_format:
            self.player.get_texture().blit(self.video_x, self.video_y, width=self.video_width, height=self.video_height)
        self.slider.value = self.player.time
        for control in self.controls:
            control.draw()
        self.fire('draw', self.player.time)

    def draw_rect(self, x, y, width, height, color=None):
        draw_rect(x, y, width, height, color)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[filename]")
    else:
        filename = sys.argv[1]
        video_player = VideoPlayer(filename)    
        video_player.play()

