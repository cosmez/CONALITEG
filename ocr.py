#pip install paddlepaddle paddleocr pdf2image pymupdf  
import os
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import os
from paddleocr import PaddleOCR

paddle = PaddleOCR(use_angle_cls=True, lang="es")

def add_ocr_layer_to_pdf(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    ocr_texts = []
    
    font = fitz.Font("helv")
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        
        
        images = convert_from_path(input_pdf, first_page=page_num + 1, last_page=page_num + 1)
        image = images[0] 
        
        page_width, page_height = page.rect.width, page.rect.height
        img_width, img_height = image.size
        scale_x = page_width / img_width
        scale_y = page_height / img_height        
        
        temp_image_path = f"temp_page_{page_num}.jpg"
        image.save(temp_image_path, "JPEG")
        ocr_result = paddle.ocr(temp_image_path, cls=True)
        os.remove(temp_image_path)
        
        
        
        for line in ocr_result:
            line_data = []
            if line is None: continue
            for word_info in line:
                word_text = word_info[1][0] 
                confidence = word_info[1][1] 
                bbox = word_info[0]
                line_data.append({
                    "text": word_text,
                    "confidence": confidence,
                    "bounding_box": bbox
                })
                if (len(word_text.strip()) > 0):
                    print(f"Page {page_num}/{doc.page_count}")
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]

                    x = min(x_coords)
                    y = min(y_coords)
                    width = max(x_coords) - x
                    height = max(y_coords) - y
                    
                    print(f"Word: {word_text}, Bounding box: ({x}, {y}, {width}, {height}), Confidence: {confidence}")
                    
                    x1 = x * scale_x
                    y1 = (y * scale_y) + (0.8 * height * scale_y)
                    x2 = (x + width) * scale_x 
                    y2 = (y + height) * scale_y
                    textract_rect = fitz.Rect(x1, y1, x2, y2)
                    textlen = font.text_length(word_text,fontsize=1)
                    fontsize = textract_rect.width / textlen if textlen > 0 else 12 
                    page.insert_text(
                        textract_rect.tl, 
                        word_text,
                        fontname="helv",  # Font
                        fontsize=fontsize,
                        stroke_opacity = 0,
                        fill_opacity = 0,
                        color=(0, 0, 1),  
                        rotate=0
                    )
            
        doc.save(output_pdf) 
   
        
        
    doc.save(output_pdf)
    print(f"OCR aplicado {output_pdf}")
    
    

def iter_pdfs(directory):
    total_pages = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf") and not file.lower().endswith("-ocred.pdf"):
                file_path = os.path.join(root, file)
                output_file = os.path.splitext(file_path)[0] + '-ocred.pdf'
                print(file_path, output_file )
                add_ocr_layer_to_pdf(file_path, output_file )
    return total_pages


iter_pdfs("./Primaria")
iter_pdfs("./Secundaria")