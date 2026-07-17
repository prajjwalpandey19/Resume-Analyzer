import os
import pdfplumber

class PDFParsingError(Exception):
    """Custom exception for PDF parsing issues."""
    pass

def extract_text_from_pdf(file_path):
    """
    Extracts text content from a PDF file.
    
    Args:
        file_path (str): The absolute path to the PDF file.
        
    Returns:
        str: Extracted text.
        
    Raises:
        PDFParsingError: If the file is not a valid PDF or text cannot be extracted.
    """
    if not os.path.exists(file_path):
        raise PDFParsingError("File not found.")
        
    if not file_path.lower().endswith('.pdf'):
        raise PDFParsingError("Invalid file type. Only PDF files are supported.")
        
    try:
        extracted_text = []
        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) == 0:
                raise PDFParsingError("The PDF file contains no pages.")
                
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(page_text)
                else:
                    # In some scanned PDFs, text might be empty, warning the user
                    pass
                    
        full_text = "\n".join(extracted_text).strip()
        
        if not full_text:
            raise PDFParsingError(
                "Unable to extract text from the PDF. The file may be scanned, "
                "image-only, or password-protected. Please upload a text-based PDF."
            )
            
        return full_text
        
    except PDFParsingError as pe:
        raise pe
    except Exception as e:
        raise PDFParsingError(f"Error parsing PDF: {str(e)}")
