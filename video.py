#!/usr/bin/env python
"""
    requires AVBin: http://avbin.github.io/AVbin/Download.html
    python3 video playback stalls for some reason
    for best video, convert to JPEG, WAV and deinterlace

"""

import time, pyglet, json, sys
from pyglet.window import key
from . import dispatcher

class VideoPlayer(pyglet.window.Window, dispatcher.Dispatcher):

    def __init__(self, filename):
        pyglet.window.Window.__init__(self, caption=filename, resizable=False)
        dispatcher.Dispatcher.__init__(self)
        self.player = pyglet.media.Player()
        source = pyglet.media.load(filename)
        self.player.queue(source)
        self.player.push_handlers(self)
        self.player.eos_action = self.player.EOS_PAUSE
        self.set_default_video_size()
        self.set_visible(True)

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

    def on_resize(self, width, height):
        super(VideoPlayer, self).on_resize(width, height)
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

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.dispatch_event('on_close')
        else:
            try:
                self.fire(chr(symbol), self.player.time)
                self.fire('key', (chr(symbol), self.player.time))
            except ValueError:
                pass

    def on_close(self):
        self.player.pause()
        self.close()

    def on_draw(self):
        self.clear()
        if self.player.source and self.player.source.video_format:
            self.player.get_texture().blit(self.video_x, self.video_y, width=self.video_width, height=self.video_height)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[filename]")
    else:
        filename = sys.argv[1]
        video_player = VideoPlayer(filename)    
        video_player.play()

