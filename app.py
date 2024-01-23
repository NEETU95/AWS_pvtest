from flask import Flask,request
from main import pdf_extraction
        
app = Flask(__name__)

@app.route('/pred', methods=['POST','GET'])
def pred():
    data = request.get_json()
    print("data : ",str(data))
    pdf_info = data.get('pdf_info',str)
    print("pdf_info : ",str(pdf_info))
    return pdf_extraction(pdf_info)

if __name__ == '__main__' :
    app.run(port=8901,host='0.0.0.0',debug=True)