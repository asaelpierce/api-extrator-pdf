from flask import Flask, request, jsonify
import pdfplumber
import io
import base64

app = Flask(__name__)

@app.route('/extrair', methods=['POST'])
def extract_pdf():
    try:
        file_bytes = None
        filename = "arquivo.pdf"

        # ✅ Caso 1: multipart/form-data
        if 'file' in request.files:
            file = request.files['file']

            if file.filename == '':
                return jsonify({"error": "Nome de arquivo vazio."}), 400

            if not file.filename.lower().endswith('.pdf'):
                return jsonify({"error": "O arquivo precisa ser um PDF."}), 400

            file_bytes = file.read()
            filename = file.filename

        # ✅ Caso 2: JSON com base64 (Power Automate)
        else:
            data = request.get_json()

            if not data or 'file' not in data:
                return jsonify({
                    "error": "Nenhum arquivo enviado. Use 'file' (multipart) ou JSON base64."
                }), 400

            try:
                file_bytes = base64.b64decode(data['file'])
            except Exception:
                return jsonify({"error": "Base64 inválido."}), 400

        # 🚨 Validação básica
        if not file_bytes or len(file_bytes) < 10:
            return jsonify({"error": "Arquivo vazio ou inválido."}), 400

        # ✅ Processar PDF
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
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

        return jsonify({
            "filename": filename,
            "status": "success",
            "text": full_text.strip(),
            "metadata": {
                "total_pages": len(pdf.pages),
                "pages_detail": pages_info
            }
        })

    except Exception as e:
        return jsonify({
            "error": f"Erro ao processar PDF: {str(e)}"
        }), 500


if __name__ == '__main__':
    print("API rodando em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)
