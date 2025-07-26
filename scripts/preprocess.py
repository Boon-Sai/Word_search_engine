import os
import glob
import json
import tempfile
import shutil
import subprocess
import logging
from PIL import Image, ImageDraw
from pdf2image import convert_from_path
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from tqdm import tqdm

# Set up logging
def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def preprocess_docx(input_folder, output_folder):
    """Convert DOCX files to PDFs using LibreOffice."""
    os.makedirs(output_folder, exist_ok=True)
    docx_files = glob.glob(os.path.join(input_folder, "*.docx"))
    pdf_paths = []
    
    for docx_file in docx_files:
        pdf_path = os.path.join(output_folder, os.path.basename(docx_file).replace(".docx", ".pdf"))
        try:
            subprocess.run(
                ["soffice", "--headless", "--convert-to", "pdf", docx_file, "--outdir", output_folder],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            pdf_paths.append(pdf_path)
            logging.info(f"Converted {docx_file} to {pdf_path}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error converting {docx_file}: {e.stderr.decode()}")
        except Exception as e:
            logging.error(f"Error converting {docx_file}: {str(e)}")
    
    return pdf_paths

def convert_page_to_image(pdf_path, page_num, output_dir, doc_name):
    """Convert a PDF page to an image."""
    os.makedirs(output_dir, exist_ok=True)
    try:
        images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num)
        image_path = os.path.join(output_dir, f"{doc_name}_page_{page_num}.jpg")
        images[0].save(image_path, "JPEG")
        logging.info(f"Converted page {page_num} of {pdf_path} to {image_path}")
        return image_path
    except Exception as e:
        logging.error(f"Error converting page {page_num} of {pdf_path}: {str(e)}")
        return None

def draw_bounding_boxes(image_path, words, output_dir, doc_name, page_num):
    """Draw bounding boxes on an image for all words."""
    try:
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            img_width, img_height = img.size
            
            for word in words:
                bbox = word['bounding_box']
                # Scale bounding boxes to image dimensions
                x_min = bbox[0] * img_width
                y_min = bbox[1] * img_height
                x_max = bbox[2] * img_width
                y_max = bbox[3] * img_height
                draw.rectangle(
                    [(x_min, y_min), (x_max, y_max)],
                    outline='blue',
                    width=2
                )
                logging.info(f"Drew bounding box for word '{word['word']}' at {bbox} in {image_path}")
            
            output_path = os.path.join(output_dir, f"annotated_{doc_name}_page_{page_num}.jpg")
            img.save(output_path, "JPEG")
            logging.info(f"Saved annotated image to {output_path}")
            return output_path
    except Exception as e:
        logging.error(f"Error drawing bounding boxes on {image_path}: {str(e)}")
        return None

def preprocess_documents():
    """Process documents and save all words with bounding boxes."""
    # Hardcoded inputs
    folder_path = "/home/litzchill/Boon_sai/doc_search/DATA/data"
    output_json = "word_index.json"
    logs_dir = "logs"
    
    # Validate folder path
    if not os.path.isdir(folder_path):
        logging.error(f"Invalid folder path: {folder_path}")
        raise ValueError(f"Invalid folder path: {folder_path}")
    
    # Set up logs directory and log file
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "preprocess.log")
    setup_logging(log_file)
    
    # Initialize docTR model with settings for all alignments
    model = ocr_predictor(
        det_arch='fast_base',
        reco_arch='crnn_vgg16_bn',
        pretrained=True,
        assume_straight_pages=False,  # Handle rotated/vertical text
        export_as_straight_boxes=True  # Normalize to straight boxes
    )
    
    results = []
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Preprocess DOCX files
        converted_pdfs = preprocess_docx(folder_path, temp_dir)
        
        # Supported file extensions
        supported_extensions = ["*.pdf", "*.jpg", "*.jpeg", "*.png"]
        all_files = []
        for ext in supported_extensions:
            all_files.extend(glob.glob(os.path.join(folder_path, ext)))
        all_files.extend(converted_pdfs)
        
        # Process each file with tqdm progress bar
        for file_path in tqdm(all_files, desc="Processing documents"):
            doc_name = os.path.basename(file_path).replace(".", "_")  # Replace dots for folder names
            image_dir = os.path.join(logs_dir, f"{doc_name}")
            os.makedirs(image_dir, exist_ok=True)
            logging.info(f"Processing file: {file_path}")
            
            try:
                # Load document
                if file_path.lower().endswith(".pdf"):
                    doc = DocumentFile.from_pdf(file_path)
                else:
                    doc = DocumentFile.from_images(file_path)
                
                # Perform OCR
                result = model(doc)
                logging.info(f"OCR completed for {file_path}, found {len(result.pages)} pages")
                
                # Process each page with tqdm progress bar
                for page_idx in tqdm(range(len(result.pages)), desc=f"Pages in {os.path.basename(file_path)}", leave=False):
                    page = result.pages[page_idx]
                    page_words = []
                    for block in page.blocks:
                        for line in block.lines:
                            for word in line.words:
                                page_words.append({
                                    "document": os.path.basename(file_path),
                                    "page": page_idx + 1,
                                    "word": word.value,
                                    "bounding_box": [
                                        word.geometry[0][0],
                                        word.geometry[0][1],
                                        word.geometry[1][0],
                                        word.geometry[1][1]
                                    ]
                                })
                    results.extend(page_words)
                    
                    # Convert page to image and draw bounding boxes
                    image_path = file_path if file_path.lower().endswith((".jpg", ".jpeg", ".png")) else \
                                 convert_page_to_image(file_path, page_idx + 1, image_dir, doc_name)
                    if image_path:
                        draw_bounding_boxes(image_path, page_words, image_dir, doc_name, page_idx + 1)
            
            except Exception as e:
                logging.error(f"Error processing {file_path}: {str(e)}")
                continue
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Save results to JSON
    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)
    logging.info(f"Saved word index to {output_json}")
    
    return results

def main():
    results = preprocess_documents()
    print(f"Processed {len(results)} words across all documents.")
    print(f"Word index saved to word_index.json")
    print(f"Logs and images saved to logs")
    print(f"Log file: logs/preprocess.log")

if __name__ == "__main__":
    main()