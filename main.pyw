from classes import *
from tkinter import *
from tkinter.colorchooser import *
from tkinter import filedialog
import PIL.Image
import PIL.ImageDraw
import PIL.ImageTk
import os, math
import io

class App:
    def __init__(self, master):
        self.master = master
        self.icon_style = "material"
        # self.tool_names = ["rect_select", "brush", "eraser", "text", "line", "rectangle", "fill", "picker"]
        self.tool_names = ["brush", "eraser", "line", "rectangle"]

        self.file_name = "Untitled"
        self.colours = ["black", "white"]
        self.brush_width = 5
        self.brush_shapes = ("Circle", "Square")

        self.brush_shape = StringVar(self.master)
        self.brush_shape.set(self.brush_shapes[0])

        self.canvas_width = 700
        self.canvas_height = 700
        self.selecting = False
        self.drawing_selection = False
        self.moving_selection = False

        self.master.title(self.file_name + " - LS Paint")
        self.master.iconbitmap("assets/favicon.ico")
        self.master.geometry("800x800")
        self.master.state("zoomed")
        self.master.config(bg="#a9a9a9")

        self.menu_bar = Menu(self.master)
        self.file_menu = Menu(self.menu_bar)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open...", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As...", command=self.save_file_as)

        self.status_bar = Frame(self.master)
        self.status_label = Label(self.status_bar, relief="ridge", anchor=W, text=f"Dimensions: {self.canvas_width} x {self.canvas_height}px, Cursor Position: ")

        self.toolbar = Sidebar("Tools", LEFT, W, Y)
        self.tool_buttons = {}
        for i, t in enumerate(self.tool_names):
            self.tool_buttons[t] = Button(self.toolbar.frame, width=24, height=24, bg="white", command=lambda t=t: self.select_tool(t))
            self.tool_buttons[t].img = PhotoImage(file=f"assets/{self.icon_style}/{t}.png")
            self.tool_buttons[t].config(image=self.tool_buttons[t].img)
            self.tool_buttons[t].grid(row=i//2, column=i%2)

        self.colour_buttons = []
        for i in range(2):
            self.colour_buttons.append(Button(self.toolbar.frame, bg=self.colours[i], relief="sunken", borderwidth=2, command=lambda i=i: self.choose_colour(i), width=3))

        self.brush_options = Sidebar("Brush Options", RIGHT, E, Y)

        self.brush_width_label = Label(self.brush_options.frame, text="Size: ", bg="white")
        self.brush_width_box = Spinbox(self.brush_options.frame, from_=1, to=100, command=self.set_brush_width, width=10)

        self.brush_width_box.delete(0)
        self.brush_width_box.insert(END, 5)

        self.brush_shape_label = Label(self.brush_options.frame, text="Shape: ", bg="white")
        self.brush_shape_box = OptionMenu(self.brush_options.frame, self.brush_shape, *self.brush_shapes)
        self.brush_shape_box.configure(width=5)

        # self.scrollbar_separator = Frame(width=15, height=15)
        self.x_scrollbar = Scrollbar(self.master, orient="horizontal")
        self.y_scrollbar = Scrollbar(self.master)

        self.canvas = Canvas(width=self.canvas_width, height=self.canvas_height, xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set, scrollregion=(0, 0, self.canvas_width, self.canvas_height), bg="white", cursor="crosshair", highlightthickness=0)

        self.x_scrollbar.config(command=self.canvas.xview)
        self.y_scrollbar.config(command=self.canvas.yview)

        self.master.config(menu=self.menu_bar)

        self.status_bar.pack(side=BOTTOM, anchor=S, fill=X)
        self.status_label.pack(fill=X)

        for i, b in enumerate(self.colour_buttons):
            b.grid(row=5, column=i)

        self.brush_width_label.grid(row=1, sticky=W)
        self.brush_width_box.grid(row=1, column=1)

        self.brush_shape_label.grid(row=2, sticky=W)
        self.brush_shape_box.grid(row=2, column=1)

        # self.scrollbar_separator.pack(side=RIGHT, anchor=S)
        self.x_scrollbar.pack(side=BOTTOM, fill=X)
        self.y_scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas.pack(expand=True)

        self.select_tool("brush")

        self.canvas.bind("<Enter>", self.enter)
        self.canvas.bind("<Motion>", self.motion)
        self.canvas.bind("<Button-3>", lambda e: self.b_down(e, 1))
        self.canvas.bind("<B3-Motion>", lambda e: self.b_motion(e, 1))
        self.canvas.bind("<Button-1>", lambda e: self.b_down(e, 0))
        self.canvas.bind("<B1-Motion>", lambda e: self.b_motion(e, 0))
        self.canvas.bind("<ButtonRelease-1>", lambda e: self.b_release(e, 0))
        self.canvas.bind("<ButtonRelease-3>", lambda e: self.b_release(e, 1))
        self.canvas.bind("<Leave>", self.leave_canvas)

        self.master.mainloop()

    def new_file(self):
        self.new_file_dialogue = Toplevel(self.master)

        self.new_file_dialogue.title("New File")
        self.new_file_dialogue.iconbitmap("assets/favicon.ico")
        self.new_file_dialogue.columnconfigure(1, weight=1)

        self.with_label = Label(self.new_file_dialogue, text="Width:")
        self.with_entry = Entry(self.new_file_dialogue)

        self.height_label = Label(self.new_file_dialogue, text="Height:")
        self.height_entry = Entry(self.new_file_dialogue)

        self.new_file_dialogue_button = Button(self.new_file_dialogue, text="New File", command=self.new_file_confirm)

        self.with_label.grid(row=0, sticky=W, padx=2, pady=2)
        self.with_entry.grid(row=0, column=1, sticky=E+W, padx=2, pady=2)

        self.height_label.grid(row=1, sticky=W, padx=2, pady=2)
        self.height_entry.grid(row=1, column=1, sticky=E+W, padx=2, pady=2)

        self.new_file_dialogue_button.grid(row=2, columnspan=2, sticky=E+W, padx=2, pady=2)

        self.with_entry.insert(END, self.canvas_width)
        self.height_entry.insert(END, self.canvas_height)

    def new_file_confirm(self):
        self.canvas_width = int(self.with_entry.get())
        self.canvas_height = int(self.height_entry.get())

        self.canvas.config(width=self.canvas_width, height=self.canvas_height, scrollregion=(0, 0, self.canvas_width, self.canvas_height))

        self.file_name = "Untitled"
        self.master.title(self.file_name + " - LS Paint")

        self.update_status(None)
        self.new_file_dialogue.destroy()

        try:
            del self.polygon
            del self.line
            self.canvas.delete("all")
        except:
            self.canvas.delete("all")

    def open_file(self):
        self.open_path = filedialog.askopenfilenames(title="Open", filetypes=[("PNG (*.png)", ".png")])
        self.open_path = self.open_path[0]
        self.to_open = PhotoImage(file=self.open_path)

        try:
            del self.polygon
            del self.line
        except:
            pass

        self.canvas.delete("all")

        self.canvas_width = self.to_open.width()
        self.canvas_height = self.to_open.height()

        self.file_name = os.path.basename(os.path.splitext(self.open_path)[0])
        self.master.title(f"{self.file_name} - LS Paint")

        self.canvas.config(width=self.canvas_width, height=self.canvas_height, scrollregion=(0, 0, self.canvas_width, self.canvas_height))
        self.update_status(None)

        self.canvas.create_image((0, 0), image=self.to_open, anchor=NW)
        self.canvas.to_open = self.to_open

        self.save_path = self.open_path

    def save_file(self):
        try:
            self.img = self.get_image()
            self.img.save(self.save_path)
        except:
            self.save_file_as()

    def save_file_as(self):
        self.save_path = filedialog.asksaveasfilename(title="Save As...", filetypes=[("PNG (*.png)", ".png")], defaultextension=".png", initialfile=self.file_name)
        self.img = self.get_image()
        self.img.save(self.save_path)

        self.file_name = os.path.basename(os.path.splitext(self.save_path)[0])
        self.master.title(self.file_name + " - LS Paint")

    def select_tool(self, tool):
        self.selected_tool = tool
        for t in self.tool_buttons:
            if t == tool:
                self.tool_buttons[t].configure(relief="sunken")
            else:
                self.tool_buttons[t].configure(relief="flat")

        if tool != "rect_select":
            try:
                self.finish_selecting()
            except:
                pass

    def choose_colour(self, i):
        self.colours[i] = askcolor()[1]
        self.colour_buttons[i].config(bg=self.colours[i])

    def set_brush_width(self):
        self.brush_width = int(self.brush_width_box.get())

    def update_status(self, event):
        if event == None:
            pos = ""
        else:
            pos = f"{event.x}, {event.y}"
        self.status_label.config(text=f"Dimensions: {self.canvas_width} x {self.canvas_height}px, Cursor Position: {pos}")

    def enter(self, event):
        self.update_status(event)

    def motion(self, event):
        self.update_status(event)

    def get_image(self):
        ps = self.canvas.postscript()
        img = PIL.Image.open(io.BytesIO(ps.encode("utf-8")))
        print(img)
        return img

    def finish_selecting(self):
        self.img = self.get_image()
        self.canvas.create_image((self.s_bbox[0], self.s_bbox[1]), image=self.selection_photo_img, anchor=NW)
        self.canvas.delete(self.selection)
        self.selecting = False

    def b_down(self, event, c):
        self.x_start, self.y_start = event.x, event.y

        if self.selected_tool == "rect_select" and self.selecting:
            if not self.drawing_selection and self.s_bbox[0] < event.x < self.s_bbox[2] and self.s_bbox[1] < event.y < self.s_bbox[3]:
                self.moving_selection = True
            else:
                self.finish_selecting()

        if self.selected_tool == "line":
            try:
                self.canvas.itemconfig(self.line, width=self.brush_width, fill=self.colours[c])
            except:
                self.line = self.canvas.create_line(self.x_start, self.y_start, event.x, event.y, width=self.brush_width, fill=self.colours[c])

        elif self.selected_tool == "rectangle":
            try:
                self.canvas.itemconfig(self.polygon, width=self.brush_width, outline=self.colours[c])
            except:
                self.polygon = self.canvas.create_rectangle(self.x_start, self.y_start, event.x, event.y, width=self.brush_width, outline=self.colours[c])

    def b_motion(self, event, colour):
        self.update_status(event)
        if self.selected_tool == "rect_select" and colour == 0:
            if self.selecting:
                if self.moving_selection:
                    x = self.s_bbox[0] + (event.x - self.x_start)
                    y = self.s_bbox[1] + (event.y - self.y_start)
                    width =  self.s_bbox[2] - self.s_bbox[0]
                    height = self.s_bbox[3] - self.s_bbox[1]
                    self.canvas.coords(self.selection_img_obj, x, y)
                    self.canvas.coords(self.selection, x, y, x + width, y + height)

                else:
                    bounded_x = min(max(0, event.x), self.canvas_width - 1)
                    bounded_y = min(max(0, event.y), self.canvas_height - 1)
                    self.canvas.coords(self.selection, self.x_start, self.y_start, bounded_x, bounded_y)
                    self.drawing_selection = True

            else:
                bounded_x = min(max(0, event.x), self.canvas_width - 1)
                bounded_y = min(max(0, event.y), self.canvas_height - 1)
                self.img = self.get_image()
                self.selection = self.canvas.create_rectangle(self.x_start, self.y_start, bounded_x, bounded_y, width=1, outline="black", dash=(2,2))
                self.selecting = True

        elif self.selected_tool == "brush":
            dx, dy = self.x_start - event.x, self.y_start - event.y
            points = []
            if abs(dx) > abs(dy):
                min_x, max_x = min(self.x_start, event.x), max(self.x_start, event.x)
                for x in range(min_x, max_x + 1):
                    y = self.y_start + (x - self.x_start) * dy // dx
                    a, b = x - math.floor(self.brush_width / 2), y - math.floor(self.brush_width / 2)
                    c, d = x + math.ceil(self.brush_width / 2), y + math.ceil(self.brush_width / 2)
                    points.append((a, b, c, d))

            else:
                min_y, max_y = min(self.y_start, event.y), max(self.y_start, event.y)
                for y in range(min_y, max_y + 1):
                    x = self.x_start + (y - self.y_start) * dx // dy
                    a, b = x - math.floor(self.brush_width / 2), y - math.floor(self.brush_width / 2)
                    c, d = x + math.ceil(self.brush_width / 2), y + math.ceil(self.brush_width / 2)
                    points.append((a, b, c, d))

            for p in points:
                if self.brush_shape.get() == "Circle":
                    self.canvas.create_oval(p[0], p[1], p[2], p[3], fill=self.colours[colour], outline=self.colours[colour])
                elif self.brush_shape.get() == "Square":
                    self.canvas.create_rectangle(p[0], p[1], p[2], p[3], fill=self.colours[colour], outline=self.colours[colour])

            self.x_start, self.y_start = event.x, event.y

        elif self.selected_tool == "eraser":
            self.canvas.create_line(self.x_start, self.y_start, event.x, event.y, width=self.brush_width, fill="white")
            self.x_start, self.y_start = event.x, event.y

        elif self.selected_tool == "line":
            self.canvas.coords(self.line, self.x_start, self.y_start, event.x, event.y)

        elif self.selected_tool == "rectangle":
            self.canvas.coords(self.polygon, self.x_start, self.y_start, event.x, event.y)

    def b_release(self, event, c):
        if self.selected_tool == "rect_select":
            if self.selecting:
                self.s_bbox = self.canvas.bbox(self.selection)
                if self.drawing_selection:
                    self.drawing_selection = False

                    self.selection_img = self.img.crop(self.s_bbox)
                    self.canvas.create_rectangle(self.s_bbox, fill=self.colours[1], outline=self.colours[1])

                    self.selection_photo_img = PIL.ImageTk.PhotoImage(self.selection_img)
                    self.selection_img_obj = self.canvas.create_image((self.s_bbox[0], self.s_bbox[1]), image=self.selection_photo_img, anchor=NW)
                    self.canvas.tag_raise(self.selection)

                elif self.moving_selection:
                    self.moving_selection = False

        elif self.selected_tool == "line":
            self.line = self.canvas.create_line(self.x_start, self.y_start, event.x, event.y, width=self.brush_width, fill=self.colours[c])

        elif self.selected_tool == "rectangle":
            self.polygon = self.canvas.create_rectangle(self.x_start, self.y_start, event.x, event.y, width=self.brush_width, outline=self.colours[c])

    def leave_canvas(self, event):
        self.update_status(event)

if __name__ == "__main__":
    root = Tk()
    app = App(root)
