from tkinter import *

root = Tk()
root.geometry("1440x720")
root.title("Minesweeper Game")
root.resizable(False, False)

bg_frame = Frame(root, bg="black")
bg_frame.pack(fill=BOTH, expand=True)

root.mainloop()