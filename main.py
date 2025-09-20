from tkinter import *
import os
import subprocess
import sys

path_to_vfs, path_to_script = None, None
cmds = ["ls", "cd", "printenv"]
input_data = ""

def output_error(errm):
    output_field.insert(index = "0.0", chars = "Error: " + errm + "\n")

def output_message(message):
    output_field.insert(index = "0.0", chars = message + "\n")

def output_messages(msgs):
    output_field.insert(index = "0.0", chars = "Command: " + msgs.split()[0] + ";" + " parameters: " + ', '.join(msgs.split()[1::]) + "\n")

def output_messages2(msgs):
    output_field.insert(index = "0.0", chars = ' '.join(msgs) + "\n")

def execute_command(cmd):
    return subprocess.check_output(cmd, text=True)

def read_input(event):
    input_data = input_field.get()
    
    input_handler(input_data)
    
    input_field.delete(0, "end")

def fake_input(msg):
    input_field.insert(0, msg)

def clear_input():
    input_field.delete("0", "end")

def parse_script():
    with open(path_to_script) as file:
        for i in file.readlines():
            fake_input(i)
            read_input("")
            clear_input()

def input_handler(data):
    if data == "":
        output_error("no command entered.")

    elif data[0] == "$":
        if os.environ.get(data[1::]):
            output_message(os.environ.get(data[1::]))
        else:
            output_error("there is no such environment variable.")
    
    
    elif data.split()[0] in cmds:
        if data.split()[0] in cmds[0:2]:
            output_messages(data)
        else:
            output_messages2(execute_command(data.split()[0]))
            
            
    elif data.split()[0] == "exit":
        root.destroy()

    elif data.split()[0] == "clear":
        output_field.delete("0.0", "end")

    else:
        output_error("unrecognized command.")

root = Tk()
root.geometry("1600x1080")
root.title("VFS")

input_field = Entry(root, width=50)
input_field.grid(row=0, column=0)

input_button = Button(root, text = "Enter")
input_button.grid(row=0, column=1)
input_button.bind("<Button-1>", func = read_input)

output_field = Text(root)
output_field.grid(row=2, column=0)

def main():
    global path_to_vfs, path_to_script
    if any(["-p" in i for i in sys.argv]): # path to the physical dir of VFS
        # output_messages2(sys.argv)
        for i in sys.argv:
            if "-p" in i:
                path_to_vfs = i[2::]

    elif any(["-s" in i for i in sys.argv]): # path to the script to be executed
        output_messages2(sys.argv)
        for i in sys.argv:
            if "-s" in i:
                path_to_script = i[2::]

    if path_to_vfs:
        output_message("Path to the physical directory of VFS: " + path_to_vfs)

    if path_to_script:
        output_message("Path to the script to be executed: " + path_to_script)
        parse_script()

    root.mainloop()

if __name__ == "__main__":
    main()