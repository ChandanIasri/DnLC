# DnLC: Automated Leaf Counting in *Dendrobium nobile* Using YOLOv5

DnLC is a deep learning-based application developed for the automated detection and counting of leaves in the medicinal orchid *Dendrobium nobile* Lindl. The system uses the YOLOv5 object-detection architecture to identify individual leaves from plant images and provides an automated leaf count through a user-friendly desktop interface.

The application is intended to support non-destructive plant phenotyping, growth monitoring, and high-throughput evaluation of *Dendrobium nobile* plants.

---

## Overview

Manual counting of leaves is time-consuming, labour-intensive, and prone to observer-related variation, particularly when a large number of plants must be evaluated repeatedly. DnLC addresses this limitation by applying a trained YOLOv5 model to detect individual leaves and automatically calculate the total leaf count from an input image.

The overall workflow consists of:

1. Image acquisition of *Dendrobium nobile* plants.
2. Annotation of individual leaves using bounding boxes.
3. Training and validation of YOLOv5 models.
4. Detection of individual leaves in unseen images.
5. Automated calculation and display of the total leaf count.
6. Export of the annotated image and prediction results.

---

## Key Features

* Automated detection and counting of *Dendrobium nobile* leaves.
* YOLOv5-based object-detection framework.
* Support for individual image analysis.
* Bounding-box visualization of detected leaves.
* Display of detection confidence scores.
* Automated calculation of total leaf count.
* Graphical user interface developed using Tkinter.
* Export of annotated output images.
* Suitable for non-destructive plant phenotyping.
* Can be adapted for other crops or plant organs using a suitably annotated dataset.

---

## Graphical Abstract

```text
Plant Image
     │
     ▼
Image Pre-processing
     │
     ▼
YOLOv5 Leaf Detection Model
     │
     ▼
Bounding-box Predictions
     │
     ▼
Leaf Counting
     │
     ▼
Annotated Image and Total Leaf Count
```

---

## Dataset

The dataset used for developing DnLC contained:

| Dataset component      |                      Value |
| ---------------------- | -------------------------: |
| Total plant images     |                        766 |
| Total annotated leaves |                     10,490 |
| Target class           |                       Leaf |
| Annotation type        |               Bounding box |
| Plant species          | *Dendrobium nobile* Lindl. |

Each visible leaf was manually annotated with a bounding box. The annotated images were subsequently divided into training, validation, and testing subsets for model development and independent evaluation.

> **Note:** The original image dataset may be subject to institutional, ethical, intellectual-property, or data-sharing restrictions. Dataset availability should therefore be specified separately in the Data Availability section.

---

## Model Performance

The developed YOLOv5-based leaf-detection model achieved the following principal performance values:

| Performance metric | Value |
| ------------------ | ----: |
| F1-score           | 0.750 |
| mAP@0.50           | 0.753 |

Additional evaluation outputs, such as precision, recall, precision–recall curves, confusion matrices, and prediction examples, may be included in the `results/` directory.

The reported performance values correspond to the experimental dataset and evaluation protocol used in the associated study. Performance on images acquired under substantially different backgrounds, illumination conditions, camera distances, plant developmental stages, or leaf-overlap conditions may vary.

---

## Repository Structure

The repository may be organised as follows:

```text
DnLC/
├── DnLC.py
├── Leaf_count.pt
├── requirements.txt
├── README.md
├── LICENSE
├── Screen.png
├── dendrobium.png
├── me.jpg
├── icar_logo.png
├── iasri_logo.png
├── orchid_logo.png
├── new_count_icon.png
└── old_count_icon.png
```

Modify this structure to match the actual organisation of the repository.

---

## System Requirements

Recommended configuration:

* Windows, Linux, or macOS
* Python 3.8 or later
* Minimum 8 GB RAM
* NVIDIA GPU with CUDA support recommended for model training
* CPU execution supported for inference, although processing may be slower

### Main Python Dependencies

* PyTorch
* Torchvision
* OpenCV
* NumPy
* Pandas
* Pillow
* Matplotlib
* PyYAML
* Tkinter
* YOLOv5 dependencies

Tkinter is normally included with standard Python installations. On some Linux systems, it may need to be installed separately.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ChandanIasri/DnLC.git
cd DnLC
```

### 2. Create a Virtual Environment

Using `venv`:

```bash
python -m venv dnlc_env
```

Activate the environment on Windows:

```bash
dnlc_env\Scripts\activate
```

Activate the environment on Linux or macOS:

```bash
source dnlc_env/bin/activate
```

### 3. Install the Required Packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

When the YOLOv5 source code is included as a submodule or separate directory, install its requirements as follows:

```bash
pip install -r yolov5/requirements.txt
```

### 4. Download or Add the Trained Model

Place the trained model file in:

```text
models/Leaf_count.pt
```

The expected model path should be updated in the application configuration or inference script when a different location is used.

---

## Running the DnLC Graphical User Interface

Run the following command from the root directory:

```bash
python DnLC.py
```

The graphical interface allows the user to:

1. Select an image of a *Dendrobium nobile* plant.
2. Load the trained YOLOv5 model.
3. Perform leaf detection.
4. View the detected leaves with bounding boxes.
5. View the total number of detected leaves.
6. Save the annotated output image.

---



## Confidence Threshold

The confidence threshold determines which predicted bounding boxes are accepted as leaves.

For example:

```bash
--conf-thres 0.25
```

A lower threshold may improve sensitivity but may also increase false-positive detections. A higher threshold may reduce false positives but could exclude partially visible, overlapping, or small leaves.

The threshold should therefore be selected using the validation dataset rather than chosen solely from the test results.

---

## Example Python Inference

```python
from pathlib import Path
import torch


def count_leaves(
    image_path: str,
    weights_path: str = "models/best.pt",
    confidence_threshold: float = 0.25,
) -> int:
    """Detect and count Dendrobium nobile leaves in an image."""

    image = Path(image_path)
    weights = Path(weights_path)

    if not image.exists():
        raise FileNotFoundError(f"Image not found: {image}")

    if not weights.exists():
        raise FileNotFoundError(f"Model weights not found: {weights}")

    model = torch.hub.load(
        "ultralytics/yolov5",
        "custom",
        path=str(weights),
        force_reload=False,
    )

    model.conf = confidence_threshold
    results = model(str(image))

    predictions = results.xyxy[0]
    leaf_count = len(predictions)

    results.save()

    print(f"Detected leaves: {leaf_count}")
    return leaf_count


if __name__ == "__main__":
    count_leaves("sample_images/sample_plant.jpg")
```

For long-term reproducibility, using a locally archived YOLOv5 source version is recommended instead of dynamically downloading the current version through `torch.hub`.

---

## Output Interpretation

For every accepted detection, the model generates:

```text
x_min, y_min, x_max, y_max, confidence, class_id
```

The total leaf count is calculated as:

```text
Leaf count = Number of accepted leaf bounding boxes
```

For a one-class model, every accepted bounding box corresponds to one predicted leaf.

---

## Reproducibility

For reproducible results, users should record:

* Python version
* PyTorch version
* Torchvision version
* CUDA version
* YOLOv5 commit or release
* Operating system
* Random seed
* Training, validation, and test split
* Image resolution
* Batch size
* Number of epochs
* Optimiser and learning rate
* Confidence threshold
* Intersection-over-Union threshold
* Model weights used for inference

A fixed random seed may be configured using:

```python
import random
import numpy as np
import torch

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
```

---

## Limitations

The current implementation has the following limitations:

* Accuracy may decrease when leaves are heavily overlapping or occluded.
* Very small, folded, blurred, damaged, or partially visible leaves may be missed.
* Background objects resembling leaves may generate false-positive detections.
* Performance may be affected by uneven illumination and complex backgrounds.
* The model was developed specifically for *Dendrobium nobile* and should not be assumed to generalise directly to other plant species.
* Images acquired using substantially different cameras or imaging protocols may require additional calibration or model fine-tuning.
* Automated leaf counts should be independently validated before use in critical breeding, physiological, or commercial decisions.

---

## Recommended Image-Acquisition Conditions

For improved prediction quality:

* Capture the complete plant within the image frame.
* Use a plain or minimally complex background.
* Avoid severe shadows and overexposure.
* Maintain a consistent camera-to-plant distance.
* Minimise motion blur.
* Keep the plant approximately perpendicular to the camera.
* Use sufficient image resolution.
* Avoid including unrelated plants or leaf-like objects in the image.

---

## Data Availability

The dataset used in the study is available from the corresponding author upon reasonable request, subject to applicable institutional policies and data-sharing restrictions.

Alternatively, when the dataset is publicly archived, replace the statement above with:

```text
The dataset used in this study is available through <repository name> at
<dataset DOI or permanent identifier>.
```

---

## Code Availability

The source code, trained model configuration, inference scripts, and graphical user-interface files associated with DnLC are available in this GitHub repository.

An archived version of the code should also be deposited in a DOI-assigning repository such as Zenodo.

```text
Archived software version: <version number>
Zenodo DOI: <Zenodo DOI>
GitHub release: <GitHub release URL>
```

A DOI badge can be added after the Zenodo record is created:

```markdown
[![DOI](https://zenodo.org/badge/DOI/<Zenodo-DOI>.svg)](https://doi.org/<Zenodo-DOI>)
```

---

## Citation

When using DnLC in research, please cite the associated publication:

```bibtex
@article{deb_dnlc,
  title   = {Deep Learning-based application for automated leaf counting in medicinal orchid Dendrobium nobile L. using YOLOv5},
  author  = {<Complete author list>},
  journal = {<Journal name>},
  year    = {<Publication year>},
  volume  = {<Volume>},
  number  = {<Issue>},
  pages   = {<Page or article number>},
  doi     = {<Publication DOI>}
}
```

Please also cite the archived software release:

```bibtex
@software{dnlc_software,
  author    = {Deb, Chandan Kumar and collaborators},
  title     = {DnLC: Automated Leaf Counting in Dendrobium nobile Using YOLOv5},
  year      = {2026},
  version   = {v1.0.0},
  publisher = {Zenodo},
  doi       = {<Zenodo DOI>}
}
```

---

## Software Versioning

The repository follows semantic versioning:

```text
MAJOR.MINOR.PATCH
```

Example:

```text
v1.0.0
```

* **MAJOR:** Incompatible changes to the application or model interface.
* **MINOR:** Addition of new backward-compatible functionality.
* **PATCH:** Bug fixes and minor improvements.

---

## Licence

The project is distributed under the licence specified in the `LICENSE` file.

Recommended options include:

* MIT Licence
* BSD 3-Clause Licence
* Apache Licence 2.0
* GNU General Public License v3.0

The selected software licence must be compatible with institutional policy and the licences of all included third-party components.

The dataset, trained weights, documentation, and source code may require separate licences. These should be stated explicitly where applicable.

---

## Third-Party Software and Trademarks

DnLC uses or interfaces with third-party open-source software, including PyTorch, YOLOv5, OpenCV, and Tkinter.

The names of third-party software packages are used only for descriptive and attribution purposes. Their logos and trademarks are not included in this repository unless appropriate permission or licence terms permit their redistribution.

This repository is not endorsed by or affiliated with the developers or trademark holders of the third-party software packages.

---

## Contributing

Contributions that improve model reproducibility, usability, documentation, testing, or support for additional plant species are welcome.

A typical contribution workflow is:

```bash
git checkout -b feature/feature-name
git add .
git commit -m "Describe the proposed change"
git push origin feature/feature-name
```

Then open a pull request containing:

* A description of the change.
* The reason for the change.
* Testing details.
* Updated documentation.
* Representative output, where applicable.

---

## Reporting Issues

When reporting an issue, provide:

* Operating system
* Python version
* PyTorch version
* CUDA version, when applicable
* Exact error message
* Steps needed to reproduce the issue
* Model weight filename
* Input image format
* Relevant screenshot or log file

Do not upload confidential, copyrighted, or personally identifiable data when submitting an issue.

---

## Authors and Contributors

**Dr. Chandan Kumar Deb**
Division of Computer Applications
ICAR–Indian Agricultural Statistics Research Institute
New Delhi, India

Additional authors and contributors:

* `<Author or contributor name>`
* `<Author or contributor name>`
* `<Institution or laboratory>`

---

## Contact

For scientific, technical, or collaborative enquiries:

**Dr. Chandan Kumar Deb**
Division of Computer Applications
ICAR–Indian Agricultural Statistics Research Institute
New Delhi, India

Email: `<official email address>`

GitHub: `https://github.com/<github-username>`

---

## Acknowledgements

The authors acknowledge the institutional facilities, scientific guidance, technical support, plant-material providers, annotation contributors, and computing resources used for the development and evaluation of DnLC.

Insert the applicable project title, institute support, funding agency, project number, and acknowledgements required by the associated publication.

---

## Disclaimer

DnLC is a research software application. Predictions generated by the model may contain false-positive or false-negative detections. The software should therefore be used with appropriate scientific validation and expert interpretation.

The authors and participating institutions are not responsible for decisions made solely on the basis of software-generated predictions.
