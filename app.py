"""
app.py - Flask backend for Bank Indonesia PDF to Excel converter.

Serves the web frontend and handles PDF upload → parse → Excel download.
"""

import os
import uuid
import time
from flask import Flask, request, jsonify, send_file, render_template
from parser import parse_pdf, generate_excel

app = Flask(__name__)

# Configuration
# Use /tmp for Vercel serverless environment, otherwise local folders
if os.environ.get('VERCEL'):
    UPLOAD_FOLDER = '/tmp/uploads'
    OUTPUT_FOLDER = '/tmp/outputs'
else:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max


@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    """
    Convert uploaded PDF to Excel.
    
    Expects multipart form data with a 'file' field containing the PDF.
    Returns the generated Excel file for download.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'File must be a PDF'}), 400
    
    # Generate unique filenames
    file_id = str(uuid.uuid4())[:8]
    pdf_filename = f"{file_id}.pdf"
    excel_filename = f"{file_id}.xlsx"
    
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
    excel_path = os.path.join(OUTPUT_FOLDER, excel_filename)
    
    try:
        # Save uploaded PDF
        file.save(pdf_path)
        
        # Parse PDF
        records = parse_pdf(pdf_path)
        
        if not records:
            return jsonify({'error': 'No cardholder records found in the PDF. Make sure this is a Bank Indonesia (Mandiri) credit card statement.'}), 400
        
        # Generate Excel
        stats = generate_excel(records, excel_path)
        
        # Prepare download filename from original PDF name
        original_name = os.path.splitext(file.filename)[0]
        download_name = f"{original_name} - Transaksi.xlsx"
        
        # Return the Excel file
        response = send_file(
            excel_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Add stats as response headers for the frontend
        response.headers['X-Total-Cardholders'] = str(stats['total_cardholders'])
        response.headers['X-Total-Transactions'] = str(stats['total_transactions'])
        response.headers['X-Total-Rows'] = str(stats['total_rows'])
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    
    finally:
        # Clean up uploaded PDF (keep Excel for re-download if needed)
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except:
                pass


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'bi-pdf-converter'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
