from flask import Flask, request, jsonify
import pdfplumber
import io

app = Flask(__name__)

@app.route('/extrair', methods=['POST'])
def extract_pdf():
    # Verifica se um arquivo foi enviado na requisição
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado. Use a chave 'file' no formulário (multipart/form-data)."}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo vazio."}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "O arquivo precisa ser um PDF."}), 400

    try:
        # Lê o PDF diretamente da memória
        with pdfplumber.open(io.BytesIO(file.read())) as pdf:
            full_text = ""
            pages_info = []
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    full_text += text + "\n\n"
                    pages_info.append({
                        "page": i + 1,
                        "char_count": len(text)
                    })

            # Retorna o JSON com as informações
            return jsonify({
                "filename": file.filename,
                "status": "success",
                "text": full_text.strip(),
                "metadata": {
                    "total_pages": len(pdf.pages),
                    "pages_detail": pages_info
                }
            })

    except Exception as e:
        return jsonify({"error": f"Erro ao processar PDF: {str(e)}"}), 500

if __name__ == '__main__':
    # Roda o servidor na porta 5000
    print("Servidor de API PDF rodando em http://localhost:5000")
    print("Endpoint: POST /extrair")
    app.run(debug=True, port=5000)