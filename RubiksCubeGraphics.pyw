from __future__ import division
import CubeLib

import math

from Tkinter import *
import tkMessageBox
import tkFileDialog
from tkSimpleDialog import askstring

SQ = math.sqrt(1/2)

class GraphicalCube(Frame):
    def __init__(self, parent, cube = None, dl = 20, **kargs):
        Frame.__init__(self, parent, bg="#FFFFFF", **kargs)
        self.dl = dl
        self._recording = False
        self._record_list = []
        if cube is not None:
            self._cube = cube
        else:
            self._cube = CubeLib.Cube(1) # Dummy cube waiting for updating
            return
        self.construct_cube()

    def record(self):
        del self._record_list[:]
        self._recording = True
    def _record(self, type_of_turn, *args):
        self._record_list.append((type_of_turn, args))
    def snap_record(self):
        return tuple(self._record_list)
    def stop_recording(self):
        self._recording = False
    def run(self, record):
        import time
        for turn in record:
            if turn[0] == 's':
                self._turn_factory(*(turn[1]))()
            elif turn[0] == 'a':
                self._turn_all_factory(*(turn[1]))()
            else:
                print "well, that's strange:"
                print repr(turn)
            time.sleep(0.1)
            self.update()
    class _Square(object):
        def __init__(self, canvas, canvas_polygon_id, cube, cube_coords,
                     cube_face):
            self._canvas = canvas
            self._cpi = canvas_polygon_id
            self._cube = cube
            self._x, self._y, self._z = cube_coords
            self._face = cube_face
            self.update_square()
        def update_square(self):
            self._canvas.itemconfig(self._cpi,
              fill = self._cube._cublets[self._x][self._y][self._z].
                                    _sides_colors[self._face]
            )
        def highlight(self, color):
            self._canvas.tag_raise(self._cpi)
            self._canvas.itemconfig(self._cpi, outline=color)
    def construct_cube(self):
        cube = self._cube
        self._squares = set()
        self._turn_buttons = {}

        dl = self.dl      # Default Length (ie. non-warped)
        th = dl * (13/20) # Top Height (height of squares on top)
        txs = -dl/2       # Top x-skew
        rw = -txs         # Right Width (width of squares on right)
        rys = -th         # Right y-skew
        isx = dl*1.5 + cube._size*(-txs)
                          # Initial Start X
        isy = dl*1.5      # Initial Start Y

        # CONSTRUCT CANVAS
        canvas = Canvas(self,  width = dl*3 + dl*cube._size + rw*cube._size,
                              height = dl*3 + th*cube._size + dl*cube._size,
                        # bg="#FFFFFF")
                        )
        # CONSTRUCT TOP
        self._create_face(canvas,
                          start_x=isx, start_y=isy,
                          width=dl, height=th,
                          x_skew=txs, y_skew=0,
                          cube_face=CubeLib.TOP)
        # CONSTRUCT FRONT
        self._create_face(canvas,
                          start_x = isx+(txs*cube._size),
                          start_y = isy+(th*cube._size),
                          width=dl, height=dl,
                          x_skew=0, y_skew=0,
                          cube_face=CubeLib.FRONT)
        # CONSTRUCT RIGHT
        self._create_face(canvas,
                          start_x = isx+(dl*cube._size)+(txs*cube._size),
                          start_y = isy+(th*cube._size),
                          width=rw, height=dl,
                          x_skew=0, y_skew=rys,
                          cube_face=CubeLib.RIGHT)

        b_r = dl*(3/20)*math.sqrt(2) # button radius

        # Turns back face; buttons located on upper-left.
        self._create_turn_buttons(canvas,
                                  start_x = isx + txs/2 - th/2,
                                  start_y = isy + th/2  + txs/2,
                                  x_step = txs, y_step = th,
                                  b_radius = b_r,
                                  dimension = CubeLib.DEPTH,
                                  cube_face = CubeLib.BACK,
                                  big_x = -th/2, big_y = txs/2)
        # Turns right face; buttons located on top
        self._create_turn_buttons(canvas,
                                  start_x = isx + dl/2,
                                  start_y = isy - dl/2,
                                  x_step = dl, y_step = 0,
                                  b_radius = b_r,
                                  dimension = CubeLib.HORIZONTAL,
                                  cube_face = CubeLib.RIGHT,
                                  big_x = 0, big_y = -dl/2)
        # Turns down face; buttons located on right
        self._create_turn_buttons(canvas,
                                  start_x = isx + dl*cube._size + dl/2,
                                  start_y = isy + dl*cube._size - dl/2,
                                  x_step = 0, y_step = -dl,
                                  b_radius = b_r,
                                  dimension = CubeLib.VERTICAL,
                                  cube_face = CubeLib.DOWN,
                                  big_x = dl/2, big_y = 0)
        # Turns front face; buttons located on lower-right
        self._create_turn_buttons(canvas,
                                  start_x = isx + dl*cube._size - rw/2 - rys/2,
                                  start_y = isy + dl*cube._size - rys/2 + rw/2,
                                  x_step = -rw, y_step = -rys,
                                  b_radius = b_r,
                                  dimension = CubeLib.DEPTH,
                                  cube_face = CubeLib.FRONT,
                                  big_x = -rys/2, big_y = rw/2)
        # Turns left face; buttons located on bottom
        self._create_turn_buttons(canvas,
                                  start_x = isx + txs*cube._size + dl/2,
                                  start_y = isy + (th+dl)*cube._size + dl/2,
                                  x_step = dl, y_step = 0,
                                  b_radius = b_r,
                                  dimension = CubeLib.HORIZONTAL,
                                  cube_face = CubeLib.LEFT,
                                  big_x = 0, big_y = dl/2)
        # Turns top face; buttons located on left
        self._create_turn_buttons(canvas,
                                  start_x = isx + txs*cube._size - dl/2,
                                  start_y = isy + (th+dl)*cube._size - dl/2,
                                  x_step = 0, y_step = -dl,
                                  b_radius = b_r,
                                  dimension = CubeLib.VERTICAL,
                                  cube_face = CubeLib.TOP,
                                  big_x = -dl/2, big_y = 0)

        canvas.grid()
        self._canvas = canvas

    _cube_coords = {
        CubeLib.FRONT : lambda x, y, size: (size-1, x, size-y-1),
        CubeLib.RIGHT : lambda x, y, size: (size-x-1, size-1, size-y-1),
        CubeLib.TOP   : lambda x, y, size: (y, x, size-1)
    }
    def _create_face(self, canvas,
                           start_x, start_y,
                           width, height,
                           x_skew, y_skew,
                           cube_face):
        cube = self._cube
        size = cube._size
        cube_coords_func = self._cube_coords[cube_face]
        for x in range(size):
            for y in range(size):
                ident = self._create_square(
                    canvas = canvas,
                    x = start_x + (x*width) + (y*x_skew),
                    y = start_y + (y*height) + (x*y_skew),
                    width = width, height = height,
                    x_skew = x_skew, y_skew = y_skew, fill = '#FFFFFF')
                cube_coords = cube_coords_func(x, y, size)
                self._squares.add(self._Square(
                    canvas, ident, cube, cube_coords, cube_face
                    ))
    def _create_square(self, canvas, x, y, width, height, x_skew, y_skew, fill):
        """
        Creates a square given x, y in upper-right-hand corner, width, height,
        the amount by which to skew the x coordinates, and the amount by which
        to skew the y coordinates (skews can be positive or negative).
        """
        return canvas.create_polygon(
            x,              y,
            x+width,        y+y_skew,
            x+width+x_skew, y+height+y_skew,
            x+x_skew,       y+height,
            fill = fill,
            outline = '#000000')

    def _create_turn_buttons(self, canvas, start_x, start_y, x_step, y_step,
                             b_radius, dimension, cube_face, big_x, big_y):
        x, y = start_x, start_y
        for level in range(self._cube._size):
            ident = self._create_turn_button(canvas, x, y, b_radius, "#000000")
            turn_event = self._turn_factory(ident, level, dimension, cube_face) 
            self._turn_buttons[(cube_face, level)] = (ident, turn_event)
            self._turn_buttons[ident] = ((cube_face, level), turn_event)
            canvas.tag_bind(ident,sequence='<ButtonRelease-1>',func=turn_event)
            x += x_step
            y += y_step
        x -= x_step
        y -= y_step
        x, y = (big_x+(start_x+x)/2, big_y+(start_y+y)/2)
        ident = self._create_turn_button(canvas, x, y, b_radius, "#FF0000")
        turn_event = self._turn_all_factory(ident, dimension, cube_face)
        self._turn_buttons[(cube_face,)] = (ident, turn_event)
        self._turn_buttons[ident] = ((cube_face,), turn_event)
        canvas.tag_bind(ident,sequence='<ButtonRelease-1>',func=turn_event)
    def _create_turn_button(self, canvas, x, y, radius=3, color="#000000"):
        # SQ = math.sqrt(1/2)     (SQ is already globally defined)
        xi, yi, xf, yf = x-SQ*radius, y-SQ*radius, x+SQ*radius, y+SQ*radius
        ident = canvas.create_oval(xi, yi, xf, yf, outline=color, fill=color)
        return ident
    def _turn_factory(self, ident, level, dimension, cube_face):
        def turn(*args, **kargs):
            self._cube.turn(dimension, level, cube_face, 1)
            self._update_cube()
            if self._recording:
                self._record('s', ident,level,dimension,cube_face)
        return turn
    def _turn_all_factory(self, ident, dimension, cube_face):
        def turn(*args, **kargs):
            for level in range(self._cube._size):
                self._cube.turn(dimension, level, cube_face, 1)
            self._update_cube()
            if self._recording:
                self._record('a', ident,dimension,cube_face)
        return turn

    def getkey(self, event):
        print repr(event.char)
    def turn_all(self, dimension, cube_face, amt=1):
        for level in range(self._cube._size):
            self._cube.turn(demension, level, cube_face, amt)
    def _update_cube(self):
        for square in self._squares:
            square.update_square()
    def shuffle(self, num_turns):
        import time
        for i in range(num_turns):
            self._cube.perform_random_turn()
            self._update_cube()
            time.sleep(0.1)
            self.update()
    def save(self, file_name):
        f = open(file_name, 'w')
        f.write(str(self._cube.raw_data()))
        f.flush()
        f.close()
    def load(self, file_name):
        f = open(file_name, 'r')
        raw_data = eval(f.read())
        f.close()
        self._cube.load(raw_data)
        try: self._canvas.destroy()
        except(AttributeError): pass
        self.construct_cube()

    def solved(self):
        return self._cube.solved()


class CubeUtils(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Rubik's Cube Utilities")
        self.construct_interface()
    def construct_interface(self):
        Label(self, text="Enter default length:").grid(row=0, column=0,
              sticky=E)
        Label(self, text="Enter a cube size:").grid(row=1, column=0, sticky=E)
        Label(self, text="Enter number of times to shuffle:").grid(row=2,
              column=0, sticky=E)

        dl_entry = Entry(self)
        dl_entry.grid(row=0, column=1)

        size_entry = Entry(self)
        size_entry.grid(row=1, column=1)
        size_bttn = Button(self, text="Create", command=self.create_cube)
        size_bttn.grid(row=1, column=2, sticky=W)

        shuffle_entry = Entry(self)
        shuffle_entry.grid(row=2, column=1)
        shuffle_bttn = Button(self, text="Shuffle", command=self.shuffle_cube)
        shuffle_bttn.grid(row=2, column=2, sticky=W)

        save_bttn = Button(self, text="Save", command=self.save)
        save_bttn.grid(row=0, column=3)
        load_bttn = Button(self, text="Load", command=self.load)
        load_bttn.grid(row=1, column=3)

        macro_bttn = Button(self, text="Create Macro",
                            command=self.create_macro)
        macro_bttn.grid(row=3,column=0)
        run_macro_bttn = Button(self, text="Run Macro", command=self.run_macro)
        run_macro_bttn.grid(row=3,column=1)
        save_macros_bttn = Button(self, text="Ultra Run!", command=self.save_macros)
        save_macros_bttn.grid(row=3,column=2,columnspan=2)

        self.dl_entry = dl_entry
        self.size_entry = size_entry
        self.size_bttn = size_bttn
        self.shuffle_entry = shuffle_entry
        self.shuffle_bttn = shuffle_bttn
        self.save_bttn = save_bttn
        self.load_bttn = load_bttn
        self.macro_bttn = macro_bttn
        self.run_macro_bttn = run_macro_bttn
        self.save_macros_bttn = save_macros_bttn
        self.recording = False
        self.macros = {}
        self.gc = None
    def create_cube(self):
        try:
            size = int(self.size_entry.get())
        except(ValueError):
            tkMessageBox.showwarning("gawdammit!",
                "Please enter an integer cube size.")
            return
        try:
            dl = int(self.dl_entry.get())
        except(ValueError):
            tkMessageBox.showerror("you friggin' idiot!",
                "Please enter an integer default length")
            return
        if self.gc is not None: self.gc.destroy()
        cube = CubeLib.Cube(size)
        self.gc = GraphicalCube(self, cube, dl)
        self.gc.grid(row=4, column=0, columnspan=4)
        dl_bttn = Button(self, text="Warp", command=self.warp_cube)
        dl_bttn.grid(row=0, column=2, sticky=W)
        self.dl_bttn = dl_bttn
    def warp_cube(self):
        try:
            dl = int(self.dl_entry.get())
        except(ValueError):
            tkMessageBox.showerror("you friggin' idiot!",
                "Please enter an integer default length")
            return
        if self.gc is not None: self.gc.destroy()
        self.gc = GraphicalCube(self, self.gc._cube, dl)
        self.gc.grid(row=4, column=0, columnspan=4)
    def shuffle_cube(self):
        try:
            times = int(self.shuffle_entry.get())
        except(ValueError):
            tkMessageBox.showerror("craptastic",
                "Please enter an integer number of times to shuffle")
            return
        self.gc.shuffle(times)
    def save(self):
        if self.gc is not None:
            self.gc.save(tkFileDialog.asksaveasfilename())
        else:
            tkMessageBox.showerror("Save what?",
                "object 'None' has no attribute 'save'")
    def load(self):
        if self.gc is None:
            try:
                dl = int(self.dl_entry.get())
            except(ValueError):
                tkMessageBox.showerror("you friggin' idiot!",
                    "Please enter an integer default length")
                return
            self.gc = GraphicalCube(self, dl=dl)
            self.gc.load(tkFileDialog.askopenfilename())
            self.gc.grid(row=3, column=0, columnspan=4)
            dl_bttn = Button(self, text="Warp", command=self.warp_cube)
            dl_bttn.grid(row=0, column=2, sticky=W)
            self.dl_bttn = dl_bttn
            return
        self.gc.load(tkFileDialog.askopenfilename())

    def create_macro(self, *args, **kargs):
        if self.gc is None:
            tkMessageBox.showerror("Cannot macro...",
                "when there is no cube.")
            return
        if self.recording:
            self.gc.stop_recording()
            record = self.gc.snap_record()
            s = askstring("Defining Macro", "What do you want to call it?")
            self.macros[s] = record
            self.macro_bttn["text"] = "Create Macro"
            self.recording = False
        else:
            self.gc.record()
            self.macro_bttn["text"] = "Define it!"
            self.recording = True
    def run_macro(self, *args, **kargs):
        if self.gc is None:
            tkMessageBox.showerror("Cannot macro...",
                "when there is no cube.")
            return
        s = askstring("Retrieving Macro", "Which macro do you wish to run?")
        if s in self.macros:
            self.gc.run(self.macros[s])
        else:
            tkMessageBox.showerror("Silleh", "Don't you know there is no %s?"%s)
    def save_macros(self, *args, **kargs):
        i = 0
        s = askstring("What Macro", "would you like to do over and over and"
            "and over and over?")
        if s not in self.macros:
            tkMessageBox.showerror("Silleh", "Don't you know there is no %s?"%s)
        while True:
            i += 1
            self.gc.run(self.macros[s])
            if self.gc.solved():
                tkMessageBox.showinfo("Hooray!", "It only took %s tries!"%i)
                return

def test():
    win = CubeUtils()
    win.mainloop()

test()

#if __name__ == '__main__' and isinstance(__import__('sys').stdout, file):
#    import code
#    code.interact(local=globals())
