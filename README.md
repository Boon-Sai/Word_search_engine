

# Preprocessing Script Documentation

This document provides a comprehensive guide for setting up, installing dependencies, and running the `preprocess.py` script, designed to perform Optical Character Recognition (OCR) on documents using the docTR library. The script detects bounding boxes for every word in various alignments (horizontal, vertical, and rotated) and generates structured outputs for further analysis. This README was last updated on Saturday, July 26, 2025, at 12:07 PM IST.

## Overview

The `preprocess.py` script processes documents (PDFs, images, and DOCX files) located in a specified input folder, extracts text with bounding box coordinates, and produces the following outputs:
- A JSON file (`word_index.json`) containing word data with bounding box information.
- A `logs/` directory with per-document subfolders containing original and annotated images (with blue bounding boxes).
- A timestamped log file (`preprocess.log`) for tracking operations.

The script leverages the docTR library, which employs a two-stage OCR approach (text detection and recognition), and includes progress tracking using `tqdm`.

## Prerequisites

### System Requirements
- **Operating System**: Linux (e.g., Ubuntu/Debian) is recommended for LibreOffice compatibility.
- **Python Version**: 3.10 or higher.

### Required Software
1. **LibreOffice**: For converting DOCX files to PDFs.
2. **Poppler**: For converting PDF pages to images.
3. **pip**: For installing Python packages.

## Installation

### Step 1: Install System Dependencies
Execute the following commands to install required system packages:

```bash
sudo apt-get update
sudo apt-get install libreoffice poppler-utils
```

- Verify installations:
  - LibreOffice: `soffice --version`
  - Poppler: Ensure `pdftoppm` is available (part of `poppler-utils`).

### Step 2: Install Python Dependencies
Install the necessary Python libraries using pip:

```bash
pip install python-doctr pdf2image pillow tqdm
```

- **python-doctr**: Core library for OCR tasks (includes docTR models).
- **pdf2image**: Converts PDF pages to images.
- **pillow**: Handles image processing and bounding box drawing.
- **tqdm**: Provides progress bars for monitoring processing.

### Step 3: Verify Installation
Ensure all packages are installed correctly by running:

```bash
python -c "import doctr; print(doctr.__version__)"
python -c "import pdf2image; print(pdf2image.__version__)"
python -c "import PIL; print(PIL.__version__)"
python -c "import tqdm; print(tqdm.__version__)"
```

## Models

The script utilizes pretrained models from the docTR library, configured as follows:
- **Detection Model**: `fast_base` (a lightweight and efficient model for text localization).
- **Recognition Model**: `crnn_vgg16_bn` (a convolutional recurrent neural network for character recognition).
- **Pretrained**: `True` (uses models pretrained on public datasets for robust performance).
- **Settings**: 
  - `assume_straight_pages=False` to handle rotated or vertically aligned text.
  - `export_as_straight_boxes=True` to normalize bounding box coordinates.

These models are automatically downloaded and loaded when the script initializes the `ocr_predictor`.

## Usage

### Step 1: Prepare Input Folder
- Place your documents (PDFs, JPG, JPEG, PNG, DOCX) in the hardcoded input folder: `/home/litzchill/Boon_sai/doc_search/DATA/data`.
- Example structure:
  ```
  /home/litzchill/Boon_sai/doc_search/DATA/data/
  ├── document1.pdf
  ├── image1.jpg
  ├── example.docx
  ```

### Step 2: Run the Script
Execute the script directly from the command line:

```bash
python preprocess.py
```

- **Hardcoded Inputs**:
  - Input folder: `/home/litzchill/Boon_sai/doc_search/DATA/data`
  - Output JSON: `word_index.json`
  - Logs directory: `logs`

### Step 3: Review Outputs
- **Console Output**: Displays progress bars and summary statistics (e.g., number of processed words).
- **JSON File** (`word_index.json`): Contains word data in the format:
  ```json
  [
    {
      "document": "document_name",
      "page": page_number,
      "word": "word_text",
      "bounding_box": [x_min, y_min, x_max, y_max]
    },
    ...
  ]
  ```
- **Logs Directory** (`logs/`): Contains per-document subfolders with:
  - Original images (e.g., `document1_pdf_page_1.jpg`).
  - Annotated images with blue bounding boxes (e.g., `annotated_document1_pdf_page_1.jpg`).
- **Log File** (`logs/preprocess.log`): Records timestamps and operation details.

## Troubleshooting

### Common Issues
1. **No Bounding Boxes Detected**:
   - Verify document quality (high resolution, clear text).
   - Check `logs/preprocess.log` for errors or warnings.
   - Ensure the input folder contains supported file types.

2. **Conversion Errors**:
   - Confirm LibreOffice is installed and accessible.
   - Check file permissions in the input folder.

3. **Empty JSON Output**:
   - Ensure documents contain recognizable text.
   - Review logs for OCR failures.

### Advanced Debugging
- Modify the `det_arch` to `db_resnet50` or `db_mobilenet_v3_large` in the `ocr_predictor` initialization if `fast_base` underperforms:
  ```python
  model = ocr_predictor(
      det_arch='db_resnet50',
      reco_arch='crnn_vgg16_bn',
      pretrained=True,
      assume_straight_pages=False,
      export_as_straight_boxes=True
  )
  ```
- Share `preprocess.log` and a sample image with support for further assistance.

## Additional Notes

### Performance Considerations
- Processing time may increase with large documents or many files; `tqdm` provides progress visibility.
- Storage usage may be significant due to image generation; consider archiving `logs/` after verification.

### Enhancements
- Add support for parallel processing using `concurrent.futures` for faster execution.
- Implement manual rotation preprocessing for challenging alignments.
- Integrate with the docTR `result.show()` method for interactive visualization (requires `matplotlib` and `mplcursors`).

### License
This script utilizes the docTR library, distributed under the Apache 2.0 License. Refer to the docTR GitHub repository (https://github.com/mindee/doctr) for details.

## Contact
For further assistance, consult the docTR documentation (https://mindee.github.io/doctr/) or raise an issue on the GitHub repository.

---
