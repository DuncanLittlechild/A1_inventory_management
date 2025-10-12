import tkinter as tk

def resizeAndCentreWindow(width, height, window):
    # Get screen height and width
    screenWidth = window.winfo_screenwidth()
    screenHeight = window.winfo_screenheight()

    #find the offsets needed to centre the window
    offsetX = int(screenWidth/2 - width / 2)
    offsetY = int(screenHeight / 2 - height / 2)

    # Set the window to the centre of the screen
    window.geometry(f'{width}x{height}+{offsetX}+{offsetY}')

def clearWindow(window):
    for widget in window.winfo_children():
        widget.destroy()
