import tkinter

class Plotter():

    instance = None

    def __init__(self):
        self.master = tkinter.Tk()
        self.width, self.height = 500, 500
        self.margin = 20
        self.w = tkinter.Canvas(self.master, width=self.width + self.margin*2, height=self.height + self.margin*2)
        self.w.pack()
        self.w.create_rectangle(self.margin - 1, self.margin - 1, self.width + self.margin + 1, self.height + self.margin + 1)

    @classmethod
    def plot(cls, bp_f, color="red"):                
        if cls.instance is None:
            cls.instance = Plotter()
        if callable(bp_f):
            points = [(i + cls.instance.margin, ((1.0 - bp_f(float(i) / cls.instance.width)) * cls.instance.height) + cls.instance.margin) for i in range(int(cls.instance.width))]
        else:
            points = [((i / len(bp_f)) * cls.instance.width + cls.instance.margin, ((1.0 - bp_f[i]) * cls.instance.height) + cls.instance.margin) for i in range(len(bp_f))]            
        cls.instance.w.create_line(points, fill=color, width=2.0)

    @classmethod
    def show_plots(cls):
        cls.instance.master.update()

def plot(bp_f, color="red"):
    Plotter.plot(bp_f, color)

def show_plots():
    Plotter.show_plots()