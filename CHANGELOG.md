# Changelog

All notable changes to DnLC will be documented in this file.

## [1.0.0] - 2026-08-06

### Added

- Initial public release of the DnLC desktop application.
- Automated leaf detection and counting for Dendrobium nobile.
- Batch processing of plant images.
- Annotated PNG output preserving original image dimensions.
- CSV export of image-wise leaf counts.
- Previous-result browser within the graphical interface.
- Pinned YOLOv5 source at commit `46d9a3c48ee08c5d2c9cb1a827d5462d1b24527c`.
- Cross-platform loading support for the Windows-trained PyTorch checkpoint.
- Clean-clone installation test on macOS with Python 3.13.0 and PyTorch 2.6.0.

### Configuration

- Confidence threshold: 0.65
- IoU threshold: 0.45
- Inference size: 640 pixels
- Target class: leaf

### Fixed

- Duplicate inference and duplicate CSV entries.
- Incorrect background-thread invocation.
- Four-channel PNG handling.
- WindowsPath checkpoint loading on macOS and Linux.
- Image aspect-ratio distortion in the result browser.
- Missing completion and error handling.
- Missing `pkg_resources` compatibility dependency through `setuptools<81`.
