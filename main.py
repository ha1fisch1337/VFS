from tkinter import *
from time import sleep
import os
import subprocess
import sys
from parse import VFSParser

parser = VFSParser()
path_to_vfs, path_to_script = None, None
cmds = ["ls", "cd", "printenv", "vfs-info", "vfs-save", "whoami", "uptime", "rm"]
input_data = ""

def output_error(errm):
    output_field.insert(index = "0.0", chars = "Error: " + errm + "\n")

def output_message(message):
    output_field.insert(index = "0.0", chars = message + "\n")

def output_messages(msgs):
    output_field.insert(index = "0.0", chars = "Command: " + msgs.split()[0] + ";" + " parameters: " + ', '.join(msgs.split()[1::]) + "\n")

def output_messages2(msgs):
    output_field.insert(index = "0.0", chars = ''.join(msgs) + "\n")

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
    cmd = ''
    try:
        cmd = data.split()[0]
    except:
        pass
    args = data.split()[1::]
    if data == "":
        output_error("no command entered.")

    elif data[0] == "$":
        if os.environ.get(data[1::]):
            output_message(os.environ.get(data[1::]))
        else:
            output_error("there is no such environment variable.")
    
    elif cmd in cmds:
        if cmd == "ls":
            output_messages2(parser.vfs_ls())
        elif cmd == "cd":
            if parser.vfs_cd(args[0]):
                output_messages2([f"successfully changed current directory to: {args[0]}"])
            else:
                output_messages2([f"error"])
        elif cmd == "rm":
            if('-r' in args):
                if parser.vfs_rm(args[1], recursive=True):
                    output_messages2([f"successfully removed: {args[1]}"])
                else:
                    output_messages2([f"error"])
            else:
                if parser.vfs_rm(args[0]):
                    output_messages2([f"successfully removed: {args[0]}"])
                else:
                    output_messages2([f"error"])
            
            
        elif cmd == "whoami":
            output_messages2(execute_command("whoami"))
        elif cmd == "uptime":
            output_messages2(execute_command("uptime"))
        elif cmd == "vfs-info": 
            output_messages2(parser.vfs_info())
        elif cmd == "vfs-save":
            parser.vfs_save("saved_vfs.xml")
            output_messages2([f"XML saved into saved_vfs.xml."])
        else:
            output_messages2(execute_command(cmd))
            
    elif cmd == "exit":
        root.quit()

    elif cmd == "clear":
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
    global path_to_vfs, path_to_script, parser
    if any(["-p" == i for i in sys.argv]): # path to the physical dir of VFS
        # output_messages2(sys.argv)
        for i in range(len(sys.argv)):
            if "-p" == sys.argv[i]:
                path_to_vfs = sys.argv[i+1]
                print(path_to_vfs)
        if path_to_vfs:
            output_message("Path to the physical directory of VFS: " + path_to_vfs)
            parser.load_vfs(path_to_vfs)

    if any(["-s" == i for i in sys.argv]): # path to the script to be executed
        for i in range(len(sys.argv)):
            if "-s" == sys.argv[i]:
                path_to_script = sys.argv[i+1]
                print(path_to_script)

        if path_to_script:
            output_message("Path to the script to be executed: " + path_to_script)
            parse_script()

    root.mainloop()

if __name__ == "__main__": 
    main()