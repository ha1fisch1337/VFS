from tkinter import *
import os

cmds = ["ls", "cd"]

def output_error(errm):
    output_field.insert(index = "0.0", chars = "Error: " + errm + "\n")

def output_message(message):
    output_field.insert(index = "0.0", chars = message + "\n")

def read_input(event):
    input_data = input_field.get()
    
    input_handler(input_data)
    
    input_field.delete(0, "end")

def input_handler(data):
    if data == "":
        output_error("no command entered.")

    elif data[0] == "$":
        if os.environ.get(data[1::]):
            output_message(os.environ.get(data[1::]))

        else:
            output_error("there is no such environment variable.")
    
    elif data.split()[0] in cmds:
        output_message(data)

    elif data.split()[0] == "exit":
        root.destroy()

    else:
        output_error("unrecognized command.")

input_data = ""

root = Tk()
root.title("VFS")

input_field = Entry(root)
input_field.pack()

input_button = Button(root, text = "Enter")
input_button.pack()
input_button.bind("<Button-1>", func = read_input)

output_field = Text(root)
output_field.pack()

root.mainloop()