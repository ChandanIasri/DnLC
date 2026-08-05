#!/usr/bin/env python3
"""
DnLC: Dendrobium nobile Leaf Counter

A CustomTkinter desktop application for automated leaf detection and counting
using a pinned YOLOv5 source tree and the trained Leaf_count.pt model.

Expected project structure
--------------------------
DnLCApplication/
├── DnLC.py
├── Leaf_count.pt
├── yolov5/
│   ├── models/
│   ├── utils/
│   └── data/
├── orchid_logo.png
├── icar_logo.png
├── iasri_logo.png
├── new_count_icon.png
└── old_count_icon.png

Validated inference settings
----------------------------
Confidence threshold: 0.65
IoU threshold: 0.45
Inference size: 640
"""

from __future__ import annotations

import csv
import datetime as dt
import os
import pathlib
import platform
import subprocess
import sys
import threading
import traceback
from dataclasses import dataclass
from typing import Any

import customtkinter as ctk
import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageOps
from tkinter import filedialog, messagebox


# ---------------------------------------------------------------------------
# Cross-platform checkpoint compatibility
# ---------------------------------------------------------------------------
# Leaf_count.pt was created on Windows and may contain pathlib.WindowsPath
# objects. Mapping WindowsPath to PosixPath allows it to load on macOS/Linux.
if os.name == "nt":
    pathlib.PosixPath = pathlib.WindowsPath
else:
    pathlib.WindowsPath = pathlib.PosixPath


# ---------------------------------------------------------------------------
# Project configuration
# ---------------------------------------------------------------------------
BASE_DIR = pathlib.Path(__file__).resolve().parent
YOLOV5_DIR = BASE_DIR / "yolov5"
WEIGHTS_PATH = BASE_DIR / "Leaf_count.pt"
DATA_YAML_PATH = YOLOV5_DIR / "data" / "coco128.yaml"
COUNTS_DIR = BASE_DIR / "Counts"

CONFIDENCE_THRESHOLD = 0.65
IOU_THRESHOLD = 0.45
INFERENCE_SIZE = 640
MAX_DETECTIONS = 1000

APP_TITLE = "DnLC Application"
WINDOW_SIZE = "900x620"


@dataclass(frozen=True)
class CountResult:
    image_name: str
    leaf_count: int
    output_file: str


class App(ctk.CTk):
    """Main DnLC graphical application."""

    def __init__(self) -> None:
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(820, 560)
        self.configure(fg_color="#8B0000")

        self.frames: dict[str, ctk.CTkFrame] = {}
        self.selected_image_paths: list[pathlib.Path] = []
        self.current_output_folder: pathlib.Path | None = None
        self.selected_folder: pathlib.Path | None = None

        self.model: Any | None = None
        self.device: Any | None = None
        self.stride: Any | None = None
        self.names: Any | None = None
        self.imgsz: tuple[int, int] | None = None

        self._set_window_icon()
        self._show_splash()

    # ------------------------------------------------------------------
    # General helpers
    # ------------------------------------------------------------------
    def _asset(self, filename: str) -> pathlib.Path:
        return BASE_DIR / filename

    def _set_window_icon(self) -> None:
        icon_path = self._asset("orchid_logo.png")
        if not icon_path.exists():
            return

        try:
            icon = tk.PhotoImage(file=str(icon_path))
            self._window_icon_reference = icon
            self.wm_iconphoto(True, icon)
        except Exception:
            # The application remains usable if the OS rejects the icon.
            pass

    @staticmethod
    def _load_pil_image(path: pathlib.Path) -> Image.Image:
        """Open an image, apply EXIF orientation, and return RGB."""
        with Image.open(path) as source:
            oriented = ImageOps.exif_transpose(source)

            if oriented.mode in ("RGBA", "LA") or (
                oriented.mode == "P" and "transparency" in oriented.info
            ):
                rgba = oriented.convert("RGBA")
                background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
                background.alpha_composite(rgba)
                return background.convert("RGB")

            return oriented.convert("RGB")

    @staticmethod
    def _fit_preview(image: Image.Image, max_size: tuple[int, int]) -> Image.Image:
        """Return an aspect-ratio-preserving preview."""
        preview = image.copy()
        preview.thumbnail(max_size, Image.Resampling.LANCZOS)
        return preview

    # ------------------------------------------------------------------
    # Splash and navigation
    # ------------------------------------------------------------------
    def _show_splash(self) -> None:
        self.splash_frame = ctk.CTkFrame(self, fg_color="#8B0000")
        self.splash_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.splash_frame,
            text="Welcome to DnLC Application",
            font=("Arial", 25, "bold"),
            text_color="white",
        ).pack(pady=(180, 30))

        self.splash_progress = ctk.CTkProgressBar(
            self.splash_frame,
            width=330,
            height=18,
            corner_radius=10,
        )
        self.splash_progress.pack(pady=20)
        self.splash_progress.set(0)

        self._advance_splash(0)

    def _advance_splash(self, value: int) -> None:
        if value <= 100:
            self.splash_progress.set(value / 100)
            self.after(15, lambda: self._advance_splash(value + 2))
            return

        self.splash_frame.destroy()
        self._build_navigation()
        self._create_frames()
        self.show_frame("Home")

    def _build_navigation(self) -> None:
        self.nav_frame = ctk.CTkFrame(
            self,
            height=54,
            fg_color="#6E0000",
            corner_radius=0,
        )
        self.nav_frame.pack(fill="x", side="top")

        nav_items = ("Home", "Leaf Count", "Old Count", "Contact Us")
        for column, name in enumerate(nav_items):
            button = ctk.CTkButton(
                self.nav_frame,
                text=name,
                width=130,
                font=("Arial", 14),
                fg_color="#8B0000",
                hover_color="#A52A2A",
                command=lambda page=name: self.show_frame(page),
            )
            button.grid(row=0, column=column, padx=6, pady=10)

        self.nav_frame.grid_columnconfigure(tuple(range(len(nav_items))), weight=1)

        self.footer_frame = ctk.CTkFrame(
            self,
            fg_color="#8B0000",
            corner_radius=0,
        )
        self.footer_frame.pack(side="bottom", fill="x")

        left_logo = self._make_ctk_image("icar_logo.png", (48, 48))
        right_logo = self._make_ctk_image("iasri_logo.png", (48, 48))

        if left_logo is not None:
            self.footer_left_logo = left_logo
            ctk.CTkLabel(
                self.footer_frame,
                image=self.footer_left_logo,
                text="",
            ).pack(side="left", padx=12, pady=5)

        ctk.CTkLabel(
            self.footer_frame,
            text=(
                "DnLC: Dendrobium nobile Leaf Counter\n"
                "ICAR–Indian Agricultural Statistics Research Institute, New Delhi"
            ),
            font=("Arial", 11),
            text_color="white",
            justify="center",
        ).pack(side="left", expand=True, pady=7)

        if right_logo is not None:
            self.footer_right_logo = right_logo
            ctk.CTkLabel(
                self.footer_frame,
                image=self.footer_right_logo,
                text="",
            ).pack(side="right", padx=12, pady=5)

    def _make_ctk_image(
        self,
        filename: str,
        size: tuple[int, int],
    ) -> ctk.CTkImage | None:
        path = self._asset(filename)
        if not path.exists():
            return None

        try:
            image = self._load_pil_image(path)
            return ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=size,
            )
        except Exception:
            return None

    def _create_frames(self) -> None:
        creators = {
            "Home": self._create_home_page,
            "Leaf Count": self._create_leaf_count_page,
            "Old Count": self._create_old_count_page,
            "Contact Us": self._create_contact_page,
        }

        for name, creator in creators.items():
            frame = ctk.CTkFrame(
                self,
                fg_color="white",
                corner_radius=15,
            )
            self.frames[name] = frame
            creator(frame)

    def show_frame(self, name: str) -> None:
        for frame in self.frames.values():
            frame.pack_forget()

        target = self.frames.get(name)
        if target is None:
            messagebox.showerror("Navigation Error", f"Page not found: {name}")
            return

        target.pack(fill="both", expand=True, padx=20, pady=18)

        if name == "Old Count":
            self._refresh_old_count_page()

    # ------------------------------------------------------------------
    # Home page
    # ------------------------------------------------------------------
    def _create_home_page(self, frame: ctk.CTkFrame) -> None:
        ctk.CTkLabel(
            frame,
            text="DnLC: Dendrobium nobile Leaf Counter",
            font=("Arial", 24, "bold"),
            text_color="#4A0000",
        ).pack(pady=(45, 18))

        description = (
            "DnLC is a YOLOv5-based desktop application for automated leaf "
            "detection and counting in Dendrobium nobile plant images. "
            "The application creates a separate output folder for every task "
            "and saves annotated images, a CSV file, and task metadata."
        )

        ctk.CTkLabel(
            frame,
            text=description,
            wraplength=650,
            justify="center",
            font=("Arial", 14),
            text_color="black",
        ).pack(pady=12)

        settings_text = (
            f"Validated confidence threshold: {CONFIDENCE_THRESHOLD:.2f}\n"
            f"IoU threshold: {IOU_THRESHOLD:.2f}\n"
            f"Inference size: {INFERENCE_SIZE} pixels"
        )

        ctk.CTkLabel(
            frame,
            text=settings_text,
            font=("Arial", 13),
            text_color="#555555",
        ).pack(pady=18)

        ctk.CTkButton(
            frame,
            text="Start a New Leaf Count",
            width=240,
            height=42,
            fg_color="#8B0000",
            hover_color="#A52A2A",
            command=lambda: self.show_frame("Leaf Count"),
        ).pack(pady=20)

    # ------------------------------------------------------------------
    # New leaf-count page
    # ------------------------------------------------------------------
    def _create_leaf_count_page(self, frame: ctk.CTkFrame) -> None:
        ctk.CTkLabel(
            frame,
            text="New Leaf Count",
            font=("Arial", 23, "bold"),
            text_color="#4A0000",
        ).pack(pady=(35, 20))

        form = ctk.CTkFrame(frame, fg_color="#F3F3F3")
        form.pack(fill="x", padx=80, pady=15)

        ctk.CTkLabel(
            form,
            text="Species:",
            font=("Arial", 15, "bold"),
            text_color="black",
        ).grid(row=0, column=0, padx=18, pady=20, sticky="w")

        self.species_entry = ctk.CTkEntry(
            form,
            width=330,
            font=("Arial", 14),
        )
        self.species_entry.insert(0, "Dendrobium nobile")
        self.species_entry.grid(row=0, column=1, padx=18, pady=20, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        self.selected_images_label = ctk.CTkLabel(
            frame,
            text="No images selected",
            font=("Arial", 13),
            text_color="#555555",
        )
        self.selected_images_label.pack(pady=10)

        ctk.CTkButton(
            frame,
            text="Select Plant Images",
            width=230,
            height=40,
            fg_color="#8B0000",
            hover_color="#A52A2A",
            command=self._select_images,
        ).pack(pady=8)

        self.count_progress = ctk.CTkProgressBar(
            frame,
            width=380,
            height=18,
        )
        self.count_progress.pack(pady=(24, 8))
        self.count_progress.set(0)

        self.count_status_label = ctk.CTkLabel(
            frame,
            text="Ready",
            font=("Arial", 13),
            text_color="#333333",
        )
        self.count_status_label.pack(pady=5)

        self.count_button = ctk.CTkButton(
            frame,
            text="Count Leaves",
            width=230,
            height=42,
            fg_color="#8B0000",
            hover_color="#A52A2A",
            state="disabled",
            command=self._start_counting,
        )
        self.count_button.pack(pady=15)

    def _select_images(self) -> None:
        selected = filedialog.askopenfilenames(
            title="Select Dendrobium plant images",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),
                ("All files", "*.*"),
            ],
        )

        if not selected:
            return

        self.selected_image_paths = [pathlib.Path(path) for path in selected]
        self.selected_images_label.configure(
            text=f"{len(self.selected_image_paths)} image(s) selected"
        )
        self.count_button.configure(state="normal")
        self.count_status_label.configure(text="Images selected; ready to count.")
        self.count_progress.set(0)

    def _start_counting(self) -> None:
        if not self.selected_image_paths:
            messagebox.showwarning(
                "No Images",
                "Please select at least one plant image.",
            )
            return

        species = self.species_entry.get().strip() or "Dendrobium nobile"
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = COUNTS_DIR / f"Count_{timestamp}"
        output_folder.mkdir(parents=True, exist_ok=False)
        self.current_output_folder = output_folder

        self._write_basic_info(output_folder, species)

        self.count_button.configure(state="disabled")
        self.count_progress.set(0)
        self.count_progress.start()
        self.count_status_label.configure(text="Loading model and counting leaves...")

        worker = threading.Thread(
            target=self._count_worker,
            args=(list(self.selected_image_paths), output_folder),
            daemon=True,
        )
        worker.start()

    def _write_basic_info(
        self,
        output_folder: pathlib.Path,
        species: str,
    ) -> None:
        info_path = output_folder / "basic_info.txt"
        lines = [
            f"TASK ID: {output_folder.name}",
            f"SPECIES: {species}",
            f"NUMBER OF IMAGES: {len(self.selected_image_paths)}",
            f"CONFIDENCE THRESHOLD: {CONFIDENCE_THRESHOLD:.2f}",
            f"IOU THRESHOLD: {IOU_THRESHOLD:.2f}",
            f"INFERENCE SIZE: {INFERENCE_SIZE}",
            f"YOLOV5 COMMIT: 46d9a3c48ee08c5d2c9cb1a827d5462d1b24527c",
        ]
        info_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        (BASE_DIR / "current_folder.txt").write_text(
            str(output_folder),
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    # YOLOv5 inference
    # ------------------------------------------------------------------
    def _load_model(self) -> None:
        """Load YOLOv5 once and reuse it for all images."""
        if self.model is not None:
            return

        if not YOLOV5_DIR.is_dir():
            raise FileNotFoundError(
                f"YOLOv5 source folder not found:\n{YOLOV5_DIR}"
            )
        if not WEIGHTS_PATH.is_file():
            raise FileNotFoundError(
                f"Model weights not found:\n{WEIGHTS_PATH}"
            )

        if str(YOLOV5_DIR) not in sys.path:
            sys.path.insert(0, str(YOLOV5_DIR))

        from models.common import DetectMultiBackend
        from utils.general import check_img_size
        from utils.torch_utils import select_device

        self.device = select_device("cpu")
        self.model = DetectMultiBackend(
            str(WEIGHTS_PATH),
            device=self.device,
            dnn=False,
            data=str(DATA_YAML_PATH),
        )
        self.stride = self.model.stride
        self.names = self.model.names
        self.imgsz = check_img_size(
            (INFERENCE_SIZE, INFERENCE_SIZE),
            s=self.stride,
        )

    def _infer_one(
        self,
        image_path: pathlib.Path,
    ) -> tuple[np.ndarray, int]:
        """Run leaf detection while preserving original image dimensions."""
        self._load_model()

        from utils.augmentations import letterbox
        from utils.general import non_max_suppression, scale_boxes
        from utils.plots import Annotator, colors

        original = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if original is None:
            raise ValueError(f"Could not read image: {image_path}")

        original_height, original_width = original.shape[:2]

        resized = letterbox(
            original,
            new_shape=self.imgsz,
            stride=self.stride,
            auto=True,
        )[0]

        input_array = resized.transpose((2, 0, 1))[::-1]
        input_array = np.ascontiguousarray(input_array)

        tensor = (
            __import__("torch")
            .from_numpy(input_array)
            .to(self.device)
            .float()
            / 255.0
        )
        if tensor.ndim == 3:
            tensor = tensor.unsqueeze(0)

        torch_module = __import__("torch")
        with torch_module.inference_mode():
            raw_prediction = self.model(
                tensor,
                augment=False,
                visualize=False,
            )

        if isinstance(raw_prediction, (list, tuple)):
            prediction_tensor = raw_prediction[0]
        else:
            prediction_tensor = raw_prediction

        predictions = non_max_suppression(
            prediction_tensor,
            conf_thres=CONFIDENCE_THRESHOLD,
            iou_thres=IOU_THRESHOLD,
            classes=[0],
            agnostic=False,
            max_det=MAX_DETECTIONS,
        )

        detections = predictions[0]
        annotated = original.copy()
        line_width = max(2, round(max(original_height, original_width) * 0.003))
        annotator = Annotator(
            annotated,
            line_width=line_width,
            example=str(self.names),
        )

        if len(detections):
            detections[:, :4] = scale_boxes(
                tensor.shape[2:],
                detections[:, :4],
                original.shape,
            ).round()

            for *xyxy, confidence, class_id in reversed(detections):
                class_index = int(class_id)
                label = f"{self.names[class_index]} {float(confidence):.2f}"
                annotator.box_label(
                    xyxy,
                    label,
                    color=colors(class_index, True),
                )

        annotated = annotator.result()
        count = int(len(detections))

        cv2.putText(
            annotated,
            f"Leaf Count: {count}",
            (12, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )

        # Geometry guard: the saved image must match the source dimensions.
        if annotated.shape[:2] != original.shape[:2]:
            raise RuntimeError(
                "Output geometry changed unexpectedly: "
                f"input={original.shape[:2]}, output={annotated.shape[:2]}"
            )

        return annotated, count

    def _count_worker(
        self,
        image_paths: list[pathlib.Path],
        output_folder: pathlib.Path,
    ) -> None:
        results: list[CountResult] = []

        try:
            total = len(image_paths)

            for index, image_path in enumerate(image_paths, start=1):
                annotated, count = self._infer_one(image_path)

                output_name = f"{image_path.stem}_counted.png"
                output_path = output_folder / output_name

                if not cv2.imwrite(str(output_path), annotated):
                    raise OSError(f"Could not save output image: {output_path}")

                results.append(
                    CountResult(
                        image_name=image_path.name,
                        leaf_count=count,
                        output_file=output_name,
                    )
                )

                progress = index / total
                self.after(
                    0,
                    lambda p=progress, n=image_path.name, c=count:
                    self._update_count_progress(p, n, c),
                )

            self._write_results_csv(output_folder, results)

            self.after(
                0,
                lambda: self._counting_completed(output_folder, results),
            )

        except Exception as error:
            traceback.print_exc()
            self.after(
                0,
                lambda exc=error: self._counting_failed(exc),
            )

    @staticmethod
    def _write_results_csv(
        output_folder: pathlib.Path,
        results: list[CountResult],
    ) -> None:
        csv_path = output_folder / "leaf_count_results.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=["Image", "Leaf Count", "Output File"],
            )
            writer.writeheader()
            for result in results:
                writer.writerow(
                    {
                        "Image": result.image_name,
                        "Leaf Count": result.leaf_count,
                        "Output File": result.output_file,
                    }
                )

    def _update_count_progress(
        self,
        progress: float,
        image_name: str,
        count: int,
    ) -> None:
        self.count_progress.set(progress)
        self.count_status_label.configure(
            text=f"{image_name}: {count} leaf/leaves detected"
        )

    def _counting_completed(
        self,
        output_folder: pathlib.Path,
        results: list[CountResult],
    ) -> None:
        self.count_progress.stop()
        self.count_progress.set(1)
        self.count_button.configure(state="normal")

        total_count = sum(result.leaf_count for result in results)
        self.count_status_label.configure(
            text=(
                f"Completed: {len(results)} image(s), "
                f"{total_count} total detected leaves"
            )
        )

        summary = "\n".join(
            f"{result.image_name}: {result.leaf_count}"
            for result in results
        )

        messagebox.showinfo(
            "Leaf Counting Completed",
            f"Leaf counting completed successfully.\n\n"
            f"{summary}\n\n"
            f"Results saved to:\n{output_folder}",
        )

        self._refresh_old_count_page()

    def _counting_failed(self, error: Exception) -> None:
        self.count_progress.stop()
        self.count_progress.set(0)
        self.count_button.configure(state="normal")
        self.count_status_label.configure(text="Counting failed.")

        messagebox.showerror(
            "Leaf Counting Error",
            f"Leaf counting could not be completed.\n\n{error}",
        )

    # ------------------------------------------------------------------
    # Old-count browser
    # ------------------------------------------------------------------
    def _create_old_count_page(self, frame: ctk.CTkFrame) -> None:
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 8))

        ctk.CTkLabel(
            header,
            text="Previous Count Results",
            font=("Arial", 22, "bold"),
            text_color="#4A0000",
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            header,
            text="Open Counts Folder",
            width=160,
            fg_color="#8B0000",
            hover_color="#A52A2A",
            command=lambda: self._open_path(COUNTS_DIR),
        ).pack(side="right", padx=5)

        body = ctk.CTkFrame(frame, fg_color="#F5F5F5")
        body.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        self.tasks_listbox = tk.Listbox(
            body,
            width=28,
            bg="#262626",
            fg="white",
            selectbackground="#8B0000",
            borderwidth=0,
            highlightthickness=0,
            font=("Arial", 12),
        )
        self.tasks_listbox.pack(
            side="left",
            fill="y",
            padx=(10, 5),
            pady=10,
        )
        self.tasks_listbox.bind(
            "<<ListboxSelect>>",
            self._on_task_selected,
        )

        self.files_listbox = tk.Listbox(
            body,
            width=32,
            bg="#333333",
            fg="white",
            selectbackground="#8B0000",
            borderwidth=0,
            highlightthickness=0,
            font=("Arial", 12),
        )
        self.files_listbox.pack(
            side="left",
            fill="y",
            padx=5,
            pady=10,
        )
        self.files_listbox.bind(
            "<<ListboxSelect>>",
            self._on_result_file_selected,
        )

        self.preview_frame = ctk.CTkFrame(body, fg_color="white")
        self.preview_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(5, 10),
            pady=10,
        )

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Select a task and output file",
            text_color="#333333",
        )
        self.preview_label.pack(expand=True, fill="both", padx=10, pady=10)

    def _refresh_old_count_page(self) -> None:
        if not hasattr(self, "tasks_listbox"):
            return

        COUNTS_DIR.mkdir(parents=True, exist_ok=True)
        self.tasks_listbox.delete(0, tk.END)
        self.files_listbox.delete(0, tk.END)
        self.selected_folder = None

        task_folders = sorted(
            [
                path
                for path in COUNTS_DIR.iterdir()
                if path.is_dir() and path.name.startswith("Count_")
            ],
            reverse=True,
        )

        self._task_paths = task_folders
        for folder in task_folders:
            self.tasks_listbox.insert(tk.END, folder.name)

    def _on_task_selected(self, _event: tk.Event) -> None:
        selection = self.tasks_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        self.selected_folder = self._task_paths[index]

        self.files_listbox.delete(0, tk.END)
        files = sorted(
            [
                path
                for path in self.selected_folder.iterdir()
                if path.suffix.lower()
                in {".png", ".jpg", ".jpeg", ".txt", ".csv"}
            ]
        )

        self._result_paths = files
        for path in files:
            self.files_listbox.insert(tk.END, path.name)

    def _clear_preview(self) -> None:
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

    def _on_result_file_selected(self, _event: tk.Event) -> None:
        selection = self.files_listbox.curselection()
        if not selection:
            return

        path = self._result_paths[selection[0]]
        self._clear_preview()

        if path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            image = self._load_pil_image(path)
            preview = self._fit_preview(image, (500, 390))
            ctk_image = ctk.CTkImage(
                light_image=preview,
                dark_image=preview,
                size=preview.size,
            )
            label = ctk.CTkLabel(
                self.preview_frame,
                image=ctk_image,
                text="",
            )
            label.image = ctk_image
            label.pack(expand=True, padx=10, pady=10)
            return

        content = path.read_text(encoding="utf-8", errors="replace")
        text_box = ctk.CTkTextbox(
            self.preview_frame,
            wrap="word",
        )
        text_box.insert("1.0", content)
        text_box.configure(state="disabled")
        text_box.pack(fill="both", expand=True, padx=10, pady=10)

    @staticmethod
    def _open_path(path: pathlib.Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(str(path))  # type: ignore[attr-defined]
            elif system == "Darwin":
                subprocess.run(["open", str(path)], check=True)
            else:
                subprocess.run(["xdg-open", str(path)], check=True)
        except Exception as error:
            messagebox.showerror(
                "Open Folder Error",
                f"Could not open:\n{path}\n\n{error}",
            )

    # ------------------------------------------------------------------
    # Contact page
    # ------------------------------------------------------------------
    def _create_contact_page(self, frame: ctk.CTkFrame) -> None:
        ctk.CTkLabel(
            frame,
            text="Contact the Development Team",
            font=("Arial", 23, "bold"),
            text_color="#4A0000",
        ).pack(pady=(35, 25))

        contacts = [
            (
                "Dr. Chandan Kumar Deb",
                "Scientist, Division of Computer Applications, "
                "ICAR–IASRI, New Delhi",
                "chandan.deb@icar.gov.in",
            ),
            (
                "Dr. Madhurima Das",
                "Scientist, Division of Plant Physiology, "
                "ICAR–IARI, New Delhi",
                "madhurima.das@icar.gov.in",
            ),
            (
                "Dr. Sudeep Marwaha",
                "Principal Scientist and Head, Division of Computer Applications, "
                "ICAR–IASRI, New Delhi",
                "sudeep@icar.gov.in",
            ),
        ]

        for name, affiliation, email in contacts:
            card = ctk.CTkFrame(frame, fg_color="#F2F2F2")
            card.pack(fill="x", padx=90, pady=8)

            ctk.CTkLabel(
                card,
                text=name,
                font=("Arial", 15, "bold"),
                text_color="#4A0000",
            ).pack(anchor="w", padx=16, pady=(12, 3))

            ctk.CTkLabel(
                card,
                text=f"{affiliation}\nEmail: {email}",
                font=("Arial", 12),
                text_color="black",
                justify="left",
                wraplength=620,
            ).pack(anchor="w", padx=16, pady=(0, 12))


def main() -> None:
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
