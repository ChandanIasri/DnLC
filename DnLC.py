import customtkinter as ctk
from PIL import Image
import os
import datetime
import tkinter.filedialog as fd
import csv
import torch
from PIL import Image
import numpy as np
import pathlib
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import pandas as pd
from tkinter import ttk
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from tkinter import filedialog, messagebox
import threading

temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath
image_array = []
file_name_array=[]
image_wise_sillique=[]
results=[]
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("DnLC Application")
        self.geometry("800x500")
        self.configure(fg_color="#8B0000")  # Dark red/maroon background
        # self.resizable(False, False)

        # Set window icon (PNG format)
        icon = tk.PhotoImage(file="icon.png")  # Replace with your icon path
        self.wm_iconphoto(True, icon)
        # Splash Screen Setup
        self.splash_screen()

    def splash_screen(self):
        # Create a Splash Frame
        self.splash_frame = ctk.CTkFrame(self, fg_color="#8B0000")  # Dark red/maroon
        self.splash_frame.pack(fill="both", expand=True)

        # Add Logos or App Title
        splash_label = ctk.CTkLabel(
            self.splash_frame,
            text="Welcome to DnLC Application",
            font=("Arial", 24, "bold"),
            text_color="white",
        )
        splash_label.pack(pady=150)

        # Progress Bar (Dynamic)
        self.progress_bar = ctk.CTkProgressBar(self.splash_frame, width=300, height=20, corner_radius=10)
        self.progress_bar.pack(pady=30)
        self.progress_bar.set(0)  # Initialize to 0%

        # Start Progress Bar Animation
        self.update_progress()

    def update_progress(self):
        progress = self.progress_bar.get()  # Get current progress
        if progress < 1.0:  # Continue updating until full
            self.progress_bar.set(progress + 0.01)  # Increment progress
            self.after(50, self.update_progress)  # Update every 50ms
        else:
            self.show_home_screen()  # Transition to the main app

    def show_home_screen(self):
        # Remove Splash Frame
        self.splash_frame.pack_forget()

        # Create Main Application Frames
        self.nav_bar()
        self.create_frames()

    def nav_bar(self):
        # Navigation Bar
        self.nav_frame = ctk.CTkFrame(self, height=50, fg_color="darkred", corner_radius=0)
        self.nav_frame.pack(fill="x", side="top")

        # self.nav_buttons = ["Home", "Leaf Count", "Image Upload", "MGIDI", "Contact Us"]
        self.nav_buttons = ["Home", "Leaf Count", "MGIDI", "Contact Us"]
        self.frames = {}

        for idx, btn_text in enumerate(self.nav_buttons):
            btn = ctk.CTkButton(
                self.nav_frame,
                text=btn_text,
                font=("Arial", 14),
                fg_color="#8B0000" if idx != 0 else "red",
                hover_color="darkred",
                corner_radius=5,
                width=120,
                command=lambda name=btn_text: self.show_frame(name),
            )
            btn.grid(row=0, column=idx, padx=5, pady=10)

        # Footer
        # Load the logos
        logo_left = Image.open("icar_logo.png").resize((50, 50))  # Adjust size as needed
        logo_right = Image.open("iasri_logo.png").resize((50, 50))  # Adjust size as needed

        logo_left_img = ImageTk.PhotoImage(logo_left)
        logo_right_img = ImageTk.PhotoImage(logo_right)
        self.footer_frame = ctk.CTkFrame(self, fg_color="#8B0000")  # Footer in dark red/maroon
        self.footer_frame.pack(side="bottom", pady=5, fill="x")
        # Left logo
        self.footer_logo_left = ctk.CTkLabel(
            self.footer_frame,
            image=logo_left_img,
            text=""  # No text, only image
        )
        self.footer_logo_left.pack(side="left", padx=10, pady=5)

        self.footer = ctk.CTkLabel(
            self.footer_frame,
            text="© 2025 Copyright: All Rights Reserved\nICAR - Indian Agricultural Statistics Research Institute, New Delhi",
            font=("Arial", 12),
            text_color="white",
            justify="center",
        )
        self.footer.pack(side="left", expand=True, pady=5)
        # Right logo
        self.footer_logo_right = ctk.CTkLabel(
            self.footer_frame,
            image=logo_right_img,
            text=""  # No text, only image
        )
        self.footer_logo_right.pack(side="right", padx=10, pady=5)

    def create_frames(self):
        # Create all frames and store them in the dictionary
        for name in self.nav_buttons:
            frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
            self.frames[name] = frame

            # Add unique content to each frame
            if name == "Home":
                # label = ctk.CTkLabel(frame, text="Welcome to DnLC Application", font=("Arial", 18, "bold"), text_color="black")
                # label.pack(pady=50)
                self.go_to_home(frame)
            elif name == "Leaf Count":
                self.create_basic_info_content(frame)
                # self.create_image_upload_content(frame)
                # label = ctk.CTkLabel(frame, text="Basic Information Screen", font=("Arial", 18, "bold"), text_color="black")
                # label.pack(pady=50)
            elif name == "Image Upload":
                self.create_image_upload_content(frame)
            elif name == "MGIDI":
                label = ctk.CTkLabel(frame, text="MGIDI Functionality Under Development", font=("Arial", 18, "bold"), text_color="black")
                label.pack(pady=50)
                # self.MGIDI(frame)
            elif name == "Contact Us":
                # label = ctk.CTkLabel(frame, text="Help Screen", font=("Arial", 18, "bold"), text_color="black")
                # label.pack(pady=50)
                self.show_contact_us(frame)


        # Show the initial frame (Home)
        self.show_frame("Home")

    def show_frame(self, name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()

        # Show the selected frame
        self.frames[name].pack(fill="both", expand=True, padx=20, pady=20)

    def create_image_upload_content(self, frame):
        # Add fields for the Image Upload screen
        for widget in frame.winfo_children():
            widget.destroy()

            # Add unique ID label and value
        unique_id_frame = ctk.CTkFrame(frame)  # Frame for grouping the label and value
        unique_id_frame.pack(fill="x", pady=5, padx=10)

        unique_id_label = ctk.CTkLabel(unique_id_frame, text="Batch ID:", font=("Arial", 16), text_color="black")
        unique_id_label.pack(side="left", padx=5)

        unique_id_value = ctk.CTkLabel(unique_id_frame, text="Auto-generated", font=("Arial", 16, "italic"),
                                       text_color="gray")
        unique_id_value.pack(side="left", padx=5)

        # Add species label and entry
        species_frame = ctk.CTkFrame(frame)  # Frame for grouping the label and entry
        species_frame.pack(fill="x", pady=5, padx=10)

        species_label = ctk.CTkLabel(species_frame, text="SPECIES:", font=("Arial", 16), text_color="black")
        species_label.pack(side="left", padx=5)

        species_entry = ctk.CTkEntry(species_frame, width=200, font=("Arial", 14))
        species_entry.pack(side="left", padx=5)

        # # Add images/plants label and entry
        # images_frame = ctk.CTkFrame(frame)  # Frame for grouping the label and entry
        # images_frame.pack(fill="x", pady=5, padx=10)
        #
        # images_label = ctk.CTkLabel(images_frame, text="No. of images/plants:", font=("Arial", 16), text_color="black")
        # images_label.pack(side="left", padx=5)
        #
        # images_entry = ctk.CTkEntry(images_frame, width=200, font=("Arial", 14))
        # images_entry.pack(side="left", padx=5)
        # Add a submit button
        global submit_button
        # submit_button = ctk.CTkButton(
        #     frame,
        #     text="Submit",
        #     command=lambda: self.submit_basic_info(
        #         unique_id_value.cget("text"),
        #         species_entry.get(),
        #         images_entry.get(),frame
        #     ),
        # )
        # submit_button.pack(pady=20)
        submit_button = ctk.CTkButton(
            frame,
            text="Open Image Folder",
            command=lambda: self.submit_basic_info(
                unique_id_value.cget("text"),
                species_entry.get(),
                 frame
            ),fg_color="#800000", hover_color="#A52A2A"
        )
        submit_button.pack(pady=20)
        back_button = ctk.CTkButton(frame, text="Back to Leaf Count",command=lambda: self.create_basic_info_content(frame), fg_color="#800000",hover_color="#A52A2A")
        back_button.pack(pady=10)


    def create_basic_info_content(self,frame):
    # Clear the frame (if needed)
        for widget in frame.winfo_children():
            widget.destroy()

    # Title Label
        title_label = ctk.CTkLabel(
        frame,
        text="Leaf Count",
        font=("Arial", 18, "bold"),
        text_color="black"
        )
        title_label.pack(pady=20)

    # Option 1: New Count
        new_count_icon = ctk.CTkImage(light_image=Image.open("new_count_icon.png"), size=(120, 35))
        new_count_button = ctk.CTkButton(
        frame,
        image=new_count_icon,
        text="New Count",
        compound="top",  # Icon on top of the text
        font=("Arial", 14),
        fg_color="#8B0000",
        hover_color="darkred",
        command=lambda: self.create_image_upload_content(frame),
        )
        new_count_button.pack(pady=10)

    # Option 2: Old Count
        old_count_icon = ctk.CTkImage(light_image=Image.open("old_count_icon.png"), size=(120, 35))
        old_count_button = ctk.CTkButton(
        frame,
        image=old_count_icon,
        text="Old Count",
        compound="top",  # Icon on top of the text
        font=("Arial", 14),
        fg_color="#8B0000",
        hover_color="darkred",
        command=lambda: self.create_old_project_opening(frame),#print("Old Count Selected"),
        )
        old_count_button.pack(pady=10)

    def submit_basic_info(self, unique_id, species,frame):
        # Step 1: Generate a unique folder name
        # Back button
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"Count_{timestamp}"

        # Base directory where folders will be created
        base_directory = os.path.join(os.getcwd(), "Counts")

        # Full path for the new folder
        folder_path = os.path.join(base_directory, folder_name)

        # Step 2: Create the folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)
        print("The folder path variable contains", folder_path)

        # Step 3: Save the input data into a text file in the folder
        info_file_path = os.path.join(folder_path, "basic_info.txt")
        with open(info_file_path, "w") as file:
            file.write(f"UNIQUE ID: {unique_id}\n")
            file.write(f"SPECIES: {species}\n")
            # file.write(f"No. of Images/Plants: {num_images}\n")

        current_folder_path=os.path.join("current_folder.txt")
        with open(current_folder_path, "w") as file:
            file.write(folder_path)
        # Display confirmation to the user
        print(f"Folder '{folder_name}' created successfully at {folder_path}.")
        print(f"Basic info saved in '{info_file_path}'.")

        # Additional logic: For example, redirect to image upload or counting process
        self.start_image_upload_process(folder_path,frame)

    def start_image_upload_process(self, folder_path,frame):
        # Step 1: Ask the user to upload multiple images
        filename = fd.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )

        if not filename:
            print("No images selected.")
            return
        col = 1  # start from column 1
        row = 3  # start from row 3
        for f in filename:
            img = Image.open(f)  # read the image file
            file_name = os.path.basename(f)
            image_array.append(img)
            file_name_array.append(file_name)
            img = img.resize((100, 100))  # new width & height
            img = ImageTk.PhotoImage(img)
            # e1 = tk.Label(my_w)
            # e1.grid(row=row, column=col)
            # e1.image = img  # keep a reference! by attaching it to a widget attribute
            # e1['image'] = img  # Show Image
            # if (col == 3):  # start new line after third column
            #     row = row + 1  # start wtih next row
            #     col = 1  # start with first column
            # else:  # within the same row
            #     col = col + 1  # increase to next column

        print(f"Selected images: {filename}")
        print('Number of images selected',len(filename))
        # Reset the progress bar
        # submit_button.configure(state=ctk.DISABLED)
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(frame, width=300)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)  # Set progress to 0 initially
        submit_button = ctk.CTkButton(frame, text="Count Leaf",command=lambda: self.start_analysis(folder_path), fg_color="#800000",hover_color="#A52A2A")
        submit_button.pack(pady=20)
        # label = ctk.CTkLabel(frame, text="Counting Completed", font=("Arial", 18, "bold"),text_color="black")
        # label.pack(pady=50)
        # Progress Bar (Dynamic)
        # Step 2: Load the pre-trained model
        # model_path = "Leaf_count.pt"  # Update this with the path to your .pt file
        # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # model = torch.load(model_path, map_location=device,weights_only=False)
        # print(model.keys())
        # model=model['model'].to(device)
        # model.eval()
        # # Check if the model is in FP16
        # if next(model.parameters()).dtype == torch.float16:
        #     model = model.half()  # Ensure model is in FP16 if its weights are in HalfTensor
        #
        # # Step 3: Process each image and count leaves
        # results = []
        # for img_path in filename:
        #     # Load and preprocess the image
        #     image = Image.open(img_path).convert("RGB")
        #     image = image.resize((224, 224))  # Resize based on your model's input requirements
        #     image_tensor = torch.tensor(np.array(image)).permute(2, 0, 1).unsqueeze(0).float() / 255.0
        #     image_tensor = image_tensor.to(device)
        #     # Match input type with model weight type
        #     if next(model.parameters()).dtype == torch.float16:
        #         image_tensor = image_tensor.half()  # Convert input to HalfTensor for FP16
        #     else:
        #         image_tensor = image_tensor.float()  # Ensure input is FloatTensor for FP32
        #
        #     image_tensor = image_tensor.to(device)  # Move input to the same device as the model
        #
        #     # Predict leaf count
        #     with torch.no_grad():
        #         output = model(image_tensor)  # Model prediction
        #         print(output)
        #         print(type(output))
        #
        #         # If output is a tuple, access the correct element
        #         # print('output from the model',output[0])
        #         if isinstance(output, tuple):
        #             predictions = output[0]  # Adjust based on your model's structure
        #         else:
        #             predictions = output
        #         # Confidence threshold
        #         # confidence_threshold = 0.50
        #
        #         # Extract the confidence scores (assumed in column 4 here)
        #         # print('prediction is',predictions)
        #         # print('confidence score',predictions[:, 1])
        #         # confidence_scores = predictions[:, 4]
        #         # print('Prediction shape',predictions.shape)
        #         # print('Prediction shape',predictions[0])
        #         # Extract confidence scores and class predictions
        #         confidence_scores = predictions[0, :, 4]  # Confidence at index 4
        #         class_predictions = predictions[0, :, 5]  # Class labels at index 5
        #         print('classs label',class_predictions)
        #
        #         # Define confidence threshold and leaf class ID
        #         confidence_threshold = 0.81  # Adjust if needed
        #         leaf_class_id = 1  # Change based on your dataset
        #
        #         # Filter valid detections
        #         valid_detections = (confidence_scores > confidence_threshold) & (class_predictions == leaf_class_id)
        #         print('Valid detection',valid_detections)
        #         # valid_detections = (confidence_scores > confidence_threshold)
        #         # Count detected leaves
        #         leaf_count = valid_detections.sum().item()
        #         print(f"Number of leaves detected: {leaf_count}")
        #
        #         # print(confidence_scores)
        #
        #         # Count detections above the threshold
        #         # valid_detections = confidence_scores > confidence_threshold
        #         # print('valid detection',valid_detections)
        #         # leaf_count = valid_detections.sum().item()  # Count of valid detections
        #         # leaf_count = len(output)  # Count of valid detections
        #
        #         # print(f"Number of leaves detected: {leaf_count}")
        #         # print('leaf count prediction', predictions)
        #         # print('leaf count prediction type',type(predictions))
        #         # # Handle multiple predictions
        #         # # leaf_counts = predictions.argmax(dim=0)  # Tensor of predicted classes
        #         # leaf_counts = predictions[:, 0].size(0)  # Tensor of predicted classes
        #         # print('Value of leaf count', leaf_counts)
        #         # for i, leaf_count in enumerate(leaf_counts):
        #         #     print(f"Leaf count for image {i}: {int(leaf_count.item())}")
        #         results.append({"Image": img_path, "Leaf Count": leaf_count})
        #

        #
        # print(f"Results saved to '{csv_path}'.")
        # submit_button.configure(state=ctk.NORMAL)
        # app.display_results(results,frame)

    def display_results(self, data_array, frame1):
        global result_label
        result_label = ctk.CTkLabel(frame1, text="Loading results...")
        result_label.pack(pady=10)

        result_label.configure(text="Results displayed below.")
        back_button = ctk.CTkButton(frame1, text="Back to Leaf Count",
                                    command=lambda: self.create_basic_info_content(frame1), fg_color="#800000",
                                    hover_color="#A52A2A")
        back_button.pack(pady=20)

        global result_frame
        result_frame = ctk.CTkFrame(frame1, width=800, height=300, corner_radius=10)
        result_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        if not data_array or len(data_array) < 2:
            result_label.configure(text="Error: No data available.")
            return

        # Extract column headers from first row
        column_names = data_array[0]
        data_rows = data_array[1:]

        # Add scrollbars
        scroll_y = tk.Scrollbar(result_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_x = tk.Scrollbar(result_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a treeview to display the data
        tree = ttk.Treeview(result_frame, columns=column_names, show="headings", yscrollcommand=scroll_y.set,
                            xscrollcommand=scroll_x.set)
        tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Configure scrollbars
        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)

        # Define column headers
        for col in column_names:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)  # Adjust column width as needed

        # Add data rows
        for row in data_rows:
            tree.insert("", "end", values=row)


    def create_old_project_opening(self,frame):
        # Destroy existing widgets in frame
        for widget in frame.winfo_children():
            widget.destroy()

        # Back button
        back_button = ctk.CTkButton(frame, text="Back to Leaf Count",command=lambda: self.create_basic_info_content(frame),fg_color="#800000", hover_color="#A52A2A")
        back_button.pack(pady=10)

        # Top frame for buttons
        top_frame = ctk.CTkFrame(frame, corner_radius=10)
        top_frame.pack(side=ctk.TOP, fill=ctk.X, pady=5, padx=10)

        btn_open = ctk.CTkButton(top_frame, text="Open Task Folder", command=self.open_folder,fg_color="#800000", hover_color="#A52A2A")
        btn_open.pack(side=ctk.LEFT, padx=5, pady=5)

        # Left frame for file list
        left_frame = ctk.CTkFrame(frame, corner_radius=10)
        left_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=10, pady=10)

        global listbox_frame
        listbox_frame = ctk.CTkFrame(left_frame, corner_radius=10)
        listbox_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        global file_listbox
        file_listbox = tk.Listbox(listbox_frame, height=20, width=30, bg="#2c2c2c", fg="white",
                                  selectbackground="#1f538d",
                                  highlightthickness=0, borderwidth=0)
        file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        file_listbox.bind('<<ListboxSelect>>', self.show_file_content)

        scrollbar = ctk.CTkScrollbar(listbox_frame, command=file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        file_listbox.config(yscrollcommand=scrollbar.set)

        # Right frame for content preview
        global content_frame
        content_frame = ctk.CTkFrame(frame, corner_radius=10)
        content_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=10, pady=10)

        self.image_label = ctk.CTkLabel(content_frame, text="No Image Selected", width=400, height=300)
        self.image_label.pack(expand=True)

    def open_folder(self):
        # folder_selected = filedialog.askdirectory()
        with open("current_folder.txt", "r") as file:
            first_line = file.readline().strip()
            print(first_line)
        # if folder_selected:
        self.selected_folder = first_line
            # print(folder_selected)
        self.list_files()

    def list_files(self):
        """ Populate listbox with image files from selected folder. """
        file_listbox.delete(0, tk.END)  # Clear previous items
        if self.selected_folder:
            for file in os.listdir(self.selected_folder):
                if file.lower().endswith(
                        ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.txt', '.csv')):  # Filter image files
                    file_listbox.insert(tk.END, file)

    def show_file_content(self, event):
        """ Display selected file content based on type (image or text). """
        selected_index = file_listbox.curselection()
        if selected_index:
            filename = file_listbox.get(selected_index[0])
            file_path = os.path.join(self.selected_folder, filename)

            # Clear previous content in the right panel
            for widget in content_frame.winfo_children():
                widget.destroy()

            # Handle Image Files
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                img = Image.open(file_path)
                img.thumbnail((400, 300))  # Resize to fit
                img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 300))

                image_label = ctk.CTkLabel(content_frame, image=img_ctk, text="")
                image_label.image = img_ctk  # Prevent garbage collection
                image_label.pack(expand=True)

            # Handle Text & CSV Files
            elif filename.lower().endswith(('.txt', '.csv')):
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                text_box = ctk.CTkTextbox(content_frame, width=400, height=300, wrap="word")
                text_box.insert("1.0", content)
                text_box.configure(state="disabled")  # Make it read-only
                text_box.pack(expand=True, fill="both", padx=5, pady=5)

    def analyze_image(self,folder_path):
        # model = torch.load('C:/Users/lab/PycharmProjects/MustardSilliqueCounter/best.pt')
        i = 0
        pad = 0
        # user_name = Label(my_w,text="Username").place(x=40,y=60)
        for image in image_array:
            # print('In analyse image function',image)
            import os
            import sys
            from pathlib import Path
            import time
            import numpy as np
            import cv2
            import torch
            import torch.backends.cudnn as cudnn
            import io
            import base64
            import datetime

            # ROOT = 'C:/Users/lab/PycharmProjects/MustardSilliqueCounter/yolov5'
            ROOT = './yolov5'
            if str(ROOT) not in sys.path:
                sys.path.append(str(ROOT))  # add ROOT to PATH
            ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

            import argparse
            import os
            import sys
            from pathlib import Path

            import torch

            from models.common import DetectMultiBackend

            import utils
            from utils.augmentations import letterbox
            from models.common import DetectMultiBackend
            from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
            from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                                       increment_path, non_max_suppression, print_args, scale_boxes, strip_optimizer,
                                       xyxy2xywh)
            from utils.plots import Annotator, colors, save_one_box
            from utils.torch_utils import select_device, time_sync
            import cv2
            from PIL import Image
            import time

            from scipy.spatial import distance as dist

            import argparse
            # import imutils
            import time
            # import dlib
            import time
            from threading import Thread
            import math
            import cv2
            # import playsound
            import numpy as np
            import threading

            import cv2
            import numpy as np
            import pandas as pd
            import csv
            import numpy
            from datetime import datetime

            import math

            # from imutils.video import VideoStream
            # from imutils import face_utils

            device = select_device('cpu')  # Set 0 if you have GPU
            model = DetectMultiBackend('./Leaf_count.pt', device=device, dnn=False, data='data/coco128.yaml')
            model.classes = [0, 2]
            stride, names, pt, jit, onnx, engine = model.stride, model.names, model.pt, model.jit, model.onnx, model.engine
            imgsz = check_img_size((640, 640), s=stride)  # check image size

            dataset = LoadImages('./me.jpg', img_size=imgsz, stride=stride, auto=pt)

            def draw_rect(image, points):
                x1 = int(points[0])
                y1 = int(points[1])
                x2 = int(points[2])
                y2 = int(points[3])
                midpoint = (int((x2 + x1) / 2), int((y2 + y1) / 2))
                print(midpoint)
                # print("Hi")
                cv2.rectangle(image, (x1, y1), (x2, y2), color=(255, 90, 90), thickness=4)
                cv2.circle(image, midpoint, radius=9, color=(0, 33, 45), thickness=-1)
                y_mid = int(y2 + y1 / 2)
                return image, y_mid

            def yolo(img):
                img0 = img.copy()
                img = letterbox(img0, 640, stride=stride, auto=True)[0]
                img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
                img = np.ascontiguousarray(img)
                im = torch.from_numpy(img).to(device)
                im = im.float()  # uint8 to fp16/32
                im /= 255  # 0 - 255 to 0.0 - 1.0
                if len(im.shape) == 3:
                    im = im[None]  # expand for batch dim
                dt = [0.0, 0.0, 0.0]
                pred = model(im, augment=False, visualize=False)
                seen = 0
                pred = non_max_suppression(pred, conf_thres=0.45, iou_thres=0.45, classes=[0, 1, 2, 3, 4, 6],
                                           max_det=1000)
                det = pred[0]
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], img0.shape).round()
                prediction = pred[0].cpu().numpy()
                for i in range(prediction.shape[0]):
                    imag, mid = draw_rect(img0, prediction[i, :])
                return imag, mid

            def custom_infer(img0,
                             weights='./Leaf_count.pt',  # model.pt path(s),
                             data='data/coco128.yaml',  # dataset.yaml path
                             imgsz=(640, 640),  # inference size (height, width)
                             conf_thres=0.35,  # confidence threshold
                             iou_thres=0.45,  # NMS IOU threshold
                             max_det=1000,  # maximum detections per image  # cuda device, i.e. 0 or 0,1,2,3 or cpu
                             view_img=False,  # show results
                             save_txt=False,  # save results to *.txt
                             save_conf=False,  # save confidences in --save-txt labels
                             save_crop=False,  # save cropped prediction boxes
                             nosave=False,  # do not save images/videos
                             classes=[0, 1, 2, 3, 4, 6, 8, 10, 12],  # filter by class: --class 0, or --class 0 2 3
                             agnostic_nms=False,  # class-agnostic NMS
                             augment=False,  # augmented inference
                             visualize=False,  # visualize features
                             update=False,  # update all models
                             project=ROOT / 'runs/detect',  # save results to project/name
                             name='exp',  # save results to project/name
                             exist_ok=False,  # existing project/name ok, do not increment
                             line_thickness=5,  # bounding box thickness (pixels)
                             hide_labels=True,  # hide labels
                             hide_conf=False,  # hide confidences
                             half=False,  # use FP16 half-precision inference
                             dnn=False,  # use OpenCV DNN for ONNX inference
                             model=model):
                img = letterbox(img0, 640, stride=stride, auto=True)[0]

                # Convert
                img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
                img = np.ascontiguousarray(img)
                im = torch.from_numpy(img).to(device)
                im = im.float()  # uint8 to fp16/32
                im /= 255  # 0 - 255 to 0.0 - 1.0
                if len(im.shape) == 3:
                    im = im[None]  # expand for batch dim
                dt = [0.0, 0.0, 0.0]
                pred = model(im, augment=augment, visualize=visualize)
                seen = 0
                if 1 < 2:

                    # NMS
                    pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

                    # Process predictions
                    for i, det in enumerate(pred):  # per image
                        seen += 1
                        p, im0, frame = 'Leaf.jpg', img0.copy(), getattr(dataset, 'frame', 0)

                        p = Path(p)  # to Path
                        imc = im0.copy() if save_crop else im0  # for save_crop
                        annotator = Annotator(im0, line_width=line_thickness, example=str(names))
                        if len(det):
                            # Rescale boxes from img_size to im0 size
                            det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                            # Print results
                            for c in det[:, -1].unique():
                                n = (det[:, -1] == c).sum()  # detections per class

                            # Write results
                            sillique = 0
                            for *xyxy, conf, cls in reversed(det):
                                if save_txt:  # Write to file

                                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(
                                        -1).tolist()  # normalized xywh
                                    line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                                    with open(txt_path + '.txt', 'a') as f:
                                        f.write(('%g ' * len(line)).rstrip() % line + '\n')

                                if 1 < 2:  # Add bbox to image
                                    sillique += 1
                                    c = int(cls)  # integer class
                                    # label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                                    label = None if hide_labels else (names[c] if hide_conf else f'{names[c]}')
                                    annotator.box_label(xyxy, label, color=colors(c, True))
                                    if save_crop:
                                        save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg',
                                                     BGR=True)
                        text = p.name + 'Leaf Count' + str(sillique)
                        # print(file_name_array[i]+"**********"+str(sillique)+"**************************************")
                        results.append({"Image": file_name_array[i], "Leaf Count": str(sillique)})
                        image_wise_sillique.append(sillique)
                        # Stream results
                        # Stream results
                        # font
                        font = cv2.FONT_HERSHEY_SIMPLEX

                        # org
                        org = (50, 100)

                        # fontScale
                        fontScale = 1

                        # Red color in BGR
                        color = (0, 0, 255)

                        # Line thickness of 2 px
                        thickness = 2
                        im0 = cv2.putText(im0, text, org, font, fontScale, color, thickness, cv2.LINE_AA, False)
                        im0 = annotator.result()
                print(file_name_array[i] + "**********" + str(sillique) + "**************************************")
                return im0, pred

            from matplotlib import pyplot as plt

            def my_resize(img):
                scale_percent = 10  # percent of original size
                width = int(img.shape[1] * scale_percent / 100)
                height = int(img.shape[0] * scale_percent / 100)
                dim = (width, height)

                # resize image
                resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
                return resized

            # In[8]:

            # import the opencv library
            import cv2
            import time
            from datetime import datetime

            print("Im before while Loop")
            window_name = "window"
            # vid = cv2.VideoCapture(0)
            # cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
            # cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            print("Im before while Loop 2")

            start = time.time()
            # img_for_test = cv2.imread('./DSC_0001.JPG')
            img_for_test = image  # cv2.imread('./DSC_0001.JPG')
            # print("Im inside the loop",image)
            # ret, frame = vid.read()
            frame = img_for_test
            frame = numpy.array(frame)
            frame = frame[:, :, ::-1].copy()
            print("Frame is ", type(frame))
            print("Frame shape ", frame.shape)

            # Image returned by yolo with classesQQ
            pred_img = custom_infer(img0=frame)[0]
            print(pred_img, "Predicted image")
            # detected classes returned by Yolo
            detected_classes = custom_infer(img0=frame)[1]
            detected_classes
            classses = detected_classes[:][0].cpu().numpy()[:, -1]

            # cv2.imshow('ceh', pred_img)
            cv2.imwrite(folder_path+"/output_image" + str(i) + ".jpg", pred_img)  # Save the image
            print('Image Succesfully saved')
            # vid.release()
            # cv2.destroyAllWindows()

            # exec(open('detect.py').read())
            # print(type(image))
            # user_name = Label(my_w,text=file_name_array[i] + "Sillique Count" + str(image_wise_sillique[i]) + "\n").place(x=40, y=60 + pad)
            # user_name = Label(my_w, text=file_name_array[i] + "\n")
            i += 1
            pad += 20
        self.progress_bar.stop()  # Stop progress animation
        self.progress_bar.set(1)  # Set progress to 100% (completed) vcf
        resultspath=folder_path+"/"+"leaf_count_results.csv"
        # app.display_results(folder_path,frame)
        # Step 4: Save the results to a CSV file in the folder
        csv_path = os.path.join(folder_path, "leaf_count_results.csv")
        with open(csv_path, mode="w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["Image", "Leaf Count"])
            writer.writeheader()
            writer.writerows(results)
        #
        # print(f"Results saved to '{csv_path}'.")
        # submit_button.configure(state=ctk.NORMAL)
        # app.display_results(csv_path,frame)
        # app.display_results(results, frame)

    def MGIDI(self,frame):
        # Upload Section
        tk.Button(frame, text="Upload Dataset", command=app.upload_file).pack(pady=10)

        # Compute MGIDI Button
        tk.Button(frame, text="Compute MGIDI", command=app.compute_mgidi(frame)).pack(pady=10)

    def calculate_mgidi(self,data, trait_weights=None):
        scaler = StandardScaler()
        standardized_data = scaler.fit_transform(data)

        pca = PCA()
        pca_data = pca.fit_transform(standardized_data)
        explained_variance = pca.explained_variance_ratio_

        if trait_weights is None:
            trait_weights = np.ones(len(data.columns)) / len(data.columns)

        weights = explained_variance[:len(trait_weights)] * trait_weights
        mgidi_scores = np.sum(np.abs(pca_data[:, :len(weights)]) * weights, axis=1)
        return mgidi_scores, explained_variance, pca

    def upload_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            try:
                global data
                data = pd.read_csv(filepath)
                messagebox.showinfo("File Loaded", "Dataset loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def compute_mgidi(self,frame):
        if 'data' not in globals():
            messagebox.showerror("Error", "No dataset loaded. Please upload a dataset first.")
            return

        try:
            # Example: Equal weights; can be customized.
            trait_weights = [0.4, 0.3, 0.2, 0.1][:len(data.columns)]
            mgidi_scores, explained_variance, _ = app.calculate_mgidi(data, trait_weights)

            # Display results in the GUI
            result_window = tk.Toplevel(frame)
            result_window.title("MGIDI Results")

            results_df = pd.DataFrame({
                "Genotype": data.index,
                "MGIDI Score": mgidi_scores
            }).sort_values(by="MGIDI Score")

            tk.Label(result_window, text="MGIDI Scores", font=("Arial", 14)).pack()
            text = tk.Text(result_window, wrap="word", width=60, height=20)
            text.insert("1.0", results_df.to_string(index=False))
            text.pack()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to compute MGIDI: {e}")

    def show_contact_us(self, frame):
        # contact_window = tk.Toplevel(frame)
        # contact_window.title("Contact Us")
        # contact_window.geometry("400x300")

        # Title
        tk.Label(frame, text="Contact the Development Team", font=("Arial", 14)).pack(pady=10)

        # Contact Information
        team_members = [
            {"name": "Dr. Chandan Kumar Deb", "designation": "Scientist","Email":"chandan.deb@icar.gov.in", "affiliation": "Division of Computer Applications, ICAR-IASRI, New Delhi-12"},
            {"name": "Dr. Madhurima Das", "designation": "Scientist", "Email":"madhurima.das@icar.gov.in","affiliation": "Division of Plant Physiology,ICAR-IARI, New Delhi-12"},
            {"name": "Dr. Sudeep Marwaha", "designation": "Principal Scientist & Head","Email":"sudeep@icar.gov.in", "affiliation": "Division of Computer Applications,ICAR-IASRI, New Delhi-12"},
        ]

        for member in team_members:
            contact_info = f"Name: {member['name']}\nDesignation: {member['designation']}\nE-mail: {member['Email']}\nAffiliation: {member['affiliation']}\n"
            ctk.CTkLabel(frame, text=contact_info, justify="left", padx=10, font=("Arial", 10)).pack(anchor="w", pady=5)

    # Function for the main home page
    def go_to_home(self,frame):
        # Clear the window
        for widget in frame.winfo_children():
            widget.destroy()

        # Title
        tk.Label(frame, text="Welcome to DnLC(Denodrobium Nobile Leaf Count)", font=("Arial", 18, "bold")).pack(pady=10)

        # Description
        description = """
        DnLC (Dendrobium nobile Leaf Counter) is a specialized application designed
        to analyze phenomics data related to leaf counting in Dendrobium nobile species.
        It allows users to efficiently process and compute MGIDI (Under Developomet)values for assessing traits
        associated with leaf analysis and crop phenotyping.
        """
        tk.Label(frame, text=description, wraplength=350, justify="center", font=("Arial", 10)).pack(pady=10)

        # Features
        tk.Label(frame, text="Key Features", font=("Arial", 14)).pack(pady=5)

        features_list = [
            "✅ Upload your phenomics datasets.",
            "✅ Perform MGIDI computation.",
            "✅ Visualize trait indices.",
            "✅ View team contact information."
        ]

        for feature in features_list:
            tk.Label(frame, text=feature, font=("Arial", 10)).pack(anchor="w", padx=20)

    def open_folder_new(self):
        folder_path = "Counts"  # Change to your specific folder
        os.startfile(folder_path)  # Opens the folder in File Explorer (Windows)

    def start_analysis(self,folder_path):
        self.progress_bar.set(0)  # Reset progress bar
        self.progress_bar.start()  # Start progress animation

        # Run analyze_image in a separate thread
        analysis_thread = threading.Thread(target=self.analyze_image(folder_path))
        analysis_thread.start()
if __name__ == "__main__":
    app = App()
    app.mainloop()
