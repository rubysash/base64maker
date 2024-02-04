'''
When writing stories for twine2, there is no option for directly importing 
scenic pictures.  So you need to write some code, save the file, do some 
stupid stuff, etc. 

However, you can also just quickly paste base64 data becase twine2 renders 
into a browser.    This means your data files like pictures, music, etc
will load as a single file instead of trying to host it online.

When you pass your twine2 book around, the user only has 1 file to get.
This is much simpler, and likely faster too.   The downside is the file size.
You could easily have a few hundred MB book that embeds base64 data into it.

In this case it would load slow because your machine needs to load all images at once.

So, it solves some problems, but you would need to divide your book into chapters
to prevent long page load times.

You can also simply convert an image to base64, it's not ONLY for twine2 you 
would want to do this.    I wrote it for twine2 though.

Basically it creates something like this:

<img src="data:image/png;base64,[Base64 Goes Here]"/>

which you just cut and paste into your twine passage.

TODO:  add option for audio data too!

<audio autoplay loop>
  <source src="data:audio/mp3;base64,[Base64 Goes Here]" type="audio/mp3">
</audio>




james@rubysash.com
'''
import sys
import tkinter as tk
import tkinter.messagebox as mb                             # to make the popup

from tkinter import *
from tkinter import Tk, Text, BOTH, W, N, E, S, DISABLED
from tkinter import filedialog                              # for file selector

from tkinter import ttk
from tkinter.ttk import Frame, Button, Label, Style, LabelFrame

# loads up default browser search
import webbrowser
import time
import base64

# some colors predefined
bgcolor = '#f0f0f0'
white  = '#FFFFFF'

dblack = '#000000'
lblack = '#444444'

dred   = '#FF0000'
lred   = '#f9dede'

dgreen = '#076d05'
lgreen = '#e0f9d9'

dblue  = '#0000FF'
lblue  = '#e2e6ff'

# globals
debug = 0
start_dir = "."
title = "Base64 Maker for Twine2 Visual Novels"

# general appearances
# todo: fix up fonts and bold stuff, hard to read
opts1 = { 'padx': 10, 'pady': 10 , 'sticky': 'nswe' } # centered
opts2 = { 'ipadx': 5, 'ipady': 5 , 'sticky': 'e' } # right justified
opts3 = { 'ipadx': 5, 'ipady': 5 , 'sticky': 'w' } # left justified
opts4 = { 'fg': 'red', 'font': 14}
opts5 = { 'fg': 'black', 'font': 14}
opts6 = { 'ipadx': 13, 'ipady': 13 , 'padx': 0, 'pady': 0, 'sticky': 'nswe' } # centered

class b64_data(tk.Tk):
    def __init__(self):
        super().__init__()
        self.initUI()

    """
    Creates the gui, buttons, fields
    """
    def initUI(self):
        # predefine variables we are using/looking for
        self.image = tk.StringVar()

        # the title bar
        self.title(title)
        
        self.style = ttk.Style(self.master)
        # Check if 'winnative' theme is available, else use a cross-platform theme
        if 'winnative' in self.style.theme_names():
            self.style.theme_use('winnative')
        else:
            # Fallback to 'clam' or another available theme
            self.style.theme_use('clam')

        self.style.configure('H.TLabel', font=('Arial', 18, 'bold'))
        self.style.configure('H.TLabel', foreground=dblack)
        self.style.configure('H.TLabel', background=bgcolor)


        self.style.configure("TLabelframe", font=('Arial', 14, 'bold'))
        self.style.configure('TLabelframe', foreground=dblue)
        self.style.configure('TLabelframe', background=bgcolor)
        self.style.configure('TLabelframe', bordercolor=dred)
        self.style.configure('TLabelframe', borderwidth = 0, highlightthickness = 0)
        #self.style.configure('TLabelframe', padx=0, pady=0, ipadx=0, ipady=0)

        self.style.configure("TLabelframe.Label", font=('Arial', 14, 'bold'))
        self.style.configure('TLabelframe.Label', foreground=dblue)
        self.style.configure('TLabelframe.Label', background=bgcolor)
        self.style.configure('TLabelframe.Label', bordercolor=dblue)
        #self.style.configure('TLabelframe.Label', padx=0, pady=0, ipadx=0, ipady=0)
        #self.style.configure('TLabelframe.Label', borderwidth = 0, highlightthickness = 0)

        self.style.configure('TLabel', font=('Arial', 12))
        self.style.configure('TLabel', foreground=dblack)
        self.style.configure('TLabel', background=bgcolor)
        #self.style.configure('TLabel', padx=0, pady=0, ipadx=0, ipady=0)
        #self.style.configure('TLabel', borderwidth = 0, highlightthickness = 0)
        
        self.style.configure('TButton', font=('Arial', 12, 'bold'))
        self.style.configure('TButton', foreground=dblack)
        self.style.configure('TButton', background=bgcolor)
        self.style.configure('TButton', padx=5, pady=5, ipadx=22, ipady=25)

        self.style.configure('TEntry', font=('Arial', 12, 'bold'))
        self.style.configure('TEntry', foreground=dblack)
        self.style.configure('TEntry', background=white)
        self.style.configure('TEntry', padx=10, pady=10, ipadx=20, ipady=20)
        
        # corners for spacing/layout
        # I wanted equal spacing on both sides of my grid layout objects
        # the solution was a space as a label todo: what is better way?
        self.label_nw = ttk.Label(self, text=" ")
        self.label_nw.grid(row=0, column=0, **opts1)
        self.label_ne = ttk.Label(self, text=" ")
        self.label_ne.grid(row=0, column=9, **opts1)

        # Instructions header
        self.label_b = ttk.Label(self, text="Select an File to Base64 Encode it",  style="H.TLabel")
        self.label_b.grid(row=1, column=1, columnspan=8, **opts1)

        # label frame for "CONTROLS"
        self.controls = ttk.LabelFrame(self, text="CONTROLS")
        self.controls.grid(row=2, column=1, columnspan=8, **opts1)
        
        # buttons
        self.btn_load_img = ttk.Button(self.controls, text=" LOAD IMAGE",command=self.load_image)
        self.btn_load_img.grid(row=3,column=1, columnspan=2)

        self.btn_load_audio = ttk.Button(self.controls, text=" LOAD AUDIO",command=self.load_audio)
        self.btn_load_audio.grid(row=3,column=3, columnspan=2)

        self.btn_view = ttk.Button(self.controls, text=" PREVIEW ",command=self.preview)
        self.btn_view.grid(row=3,column=5, columnspan=2)

        # variable where the filename/path is stored in memory
        self.loadfile = tk.StringVar()
        
        # entry where the filename is visible to us
        ttk.Entry(self.controls, textvariable=self.loadfile, width=84).grid(
            row=4, column=1, columnspan=6, **opts1)

        # Instructions header
        self.h_images = ttk.LabelFrame(self, text="IMAGE INSTRUCTIONS", style="TLabelframe")
        self.h_images.grid(row=5, column=1, columnspan=8, **opts1)

        img_instruct = """There will be a file created called b64_somefile.png.html.
Open this file with a text editor and you will see:

<img src="data:image/png;base64,[BASE64HERE]"/>
        
Paste this huge block of text directly into the twine2 passage where
you want it to appear.

It is advised to use .png images, but other formats appear to work."""

        self.img_instructions = ttk.Label(self.h_images, text=img_instruct)
        self.img_instructions.grid(row=6, column=1, columnspan=6, **opts1)

        # Instructions header
        self.h_audio = ttk.LabelFrame(self, text="AUDIO INSTRUCTIONS", style="TLabelframe")
        self.h_audio.grid(row=7, column=1, columnspan=8, **opts1)

        mp3_instruct = """There will be a file created called b64_somefile.mp3.html.
Open this file with a text editor and you will see:

<audio autoplay loop controls>
    <source src="data:audio/mp3;base64,[BASE64HERE]" type="audio/mp3">
</audio>'

You can remove loop and controls if you do not want those on your audio.
        
Paste this huge block of text directly into the twine2 passage where 
you want the audio to play.  It will not preview because autoplay
is disabled on many browsers.   It will work if you view it in twine2.

It is advisable to use mp3 only because this is universally compatible.
"""

        self.mp3_instructions = ttk.Label(self.h_audio, text=mp3_instruct)
        self.mp3_instructions.grid(row=8, column=1, columnspan=6, **opts1)


        # label frame for "DATA"
        #self.data = LabelFrame(self, text="DATA", style="B.TLabelframe")
        #self.data.grid(row=5, column=1, columnspan=8, **opts1)

        # the block of text containing the base64 data
        #self.encoded_b64_data = tk.Text(self.data, fg=dgreen,bg=lgreen, height=5)
        #self.encoded_b64_data.grid(row=6, column=1, columnspan=6, rowspan=30, **opts1)



        # some spacers at bottom
        self.label_sw = ttk.Label(self, text=" ")
        self.label_sw.grid(row=9, column=0, **opts1)
        self.label_se = ttk.Label(self, text=" ")
        self.label_se.grid(row=9, column=9, **opts1)

    """
    Erase existing data in preparation for new
    """
    def clear_all(self):
        #self.encoded_b64_data.delete("1.0", tk.END)
        self.loadfile.set("")

    """
    loads the file you choose with dialog box
    Then automatically encodes it into the DATA field
    """
    def load_image(self):

        # call the clear all definition first
        self.clear_all()

        # the file selector dialogue, each OS has a different way to list the tuples
        # https://effbot.org/tkinterbook/tkinter-file-dialogs.htm
        loadfile =  filedialog.askopenfilename(
            initialdir = start_dir,
            title = "Select file",
            filetypes = (("PNG Files","*.png"),("JPG Files","*.jpg"),("All files","*.*")))

        # put your selection in the entry field
        self.loadfile.set(loadfile)

        # this is an example of a 1 button file processor.   Modify the following
        # to do whatever you want on your file and when you load it, it will automatically
        # process it however your code is written.  My code just finds the base64 equivalent.
        
        # the entire script and GUI is for the following 4 lines of code.
        # grab the selection from entry field and do the encoding
        # add prefix and suffix so it's a complete chunk of useable data
        encoded_data = ""
        with open(self.loadfile.get(), "rb") as img_file:
            encoded_data = base64.b64encode(img_file.read()).decode('utf-8')
            encoded_data = '<img src="data:image/png;base64,' + encoded_data + '"/>'
            
            #self.encoded_b64_data.insert(tk.INSERT, encoded_data)

        print("ENCODED IMAGE: ", self.loadfile.get())

        file_path = self.loadfile.get()
        #file_data = self.encoded_b64_data.get("1.0", "end-1c")
        file_data = encoded_data

        chunks = file_path.split('/')
        file_name = chunks[-1]

        file_name = 'b64_' + file_name + '.html'

        with open(file_name, 'w') as f:
            f.write(file_data)

        print("SAVED IMAGE: ", file_name)


    def load_audio(self):

        # call the clear all definition first
        self.clear_all()

        # the file selector dialogue, each OS has a different way to list the tuples
        # https://effbot.org/tkinterbook/tkinter-file-dialogs.htm
        loadfile =  filedialog.askopenfilename(
            initialdir = start_dir,
            title = "Select file",
            filetypes = (("MP3 Files","*.mp3"),("WAV Files","*.wav"),("OGG Files", "*.ogg"),("All files","*.*")))

        # put your selection in the entry field
        self.loadfile.set(loadfile)


        # this is an example of a 1 button file processor.   Modify the following
        # to do whatever you want on your file and when you load it, it will automatically
        # process it however your code is written.  My code just finds the base64 equivalent.
        
        # the entire script and GUI is for the following 4 lines of code.
        # grab the selection from entry field and do the encoding
        # add prefix and suffix so it's a complete chunk of useable data
        encoded_data = ""
        
        with open(self.loadfile.get(), "rb") as file:
            encoded_data = base64.b64encode(file.read()).decode('utf-8')
            encoded_data = '<audio autoplay loop controls><source src="data:audio/mp3;base64,'+ encoded_data +'" type="audio/mp3"></audio>'

            #self.encoded_b64_data.insert(tk.INSERT, encoded_data)

        print("ENCODED AUDIO: ", self.loadfile.get())

        file_path = self.loadfile.get()
        #file_data = self.encoded_b64_data.get("1.0", "end-1c")
        file_data = encoded_data

        chunks = file_path.split('/')
        file_name = chunks[-1]

        file_name = 'b64_' + file_name + '.html'

        with open(file_name, 'w') as f:
            f.write(file_data)

        print("SAVED AUDIO: ", file_name)
        
    """
    You can open it in browser if you want
    """
    def preview(self):
        # take whatever data is already in the loadfile entry and use it
        file_path = self.loadfile.get()
        #file_data = self.encoded_image.get("1.0", "end-1c")

        # split the filepath and grab file name from last member or array
        chunks = file_path.split('/')
        file_name = chunks[-1]

        # rebuild filename to work with assocated OS defaults
        file_name = 'b64_' + file_name + '.html'

        # pop open the file in the default browser
        webbrowser.open(file_name)
        
        print("PREVIEW: ", file_name)


# ok, do the stuff above
if __name__ == "__main__":

    app = b64_data()
    app.mainloop()