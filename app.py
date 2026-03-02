from flask import Flask, request, jsonify, send_file
import csv
import io

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h1>CSV Extracter</h1>
    <form action="/extract" method="post" enctype="multipart/form-data">
      <label for="file">Upload CSV file:</label>
      <input type="file" name="file" id="file" required><br><br>
      <label for="column">Column name to extract:</label>
      <input type="text" name="column" id="column" required><br><br>
      <input type="submit" value="Extract">
    </form>
    '''

@app.route('/extract', methods=['POST'])
def extract():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    column = request.form.get('column')
    if not column:
        return jsonify({'error': 'No column specified'}), 400

    try:
        stream = io.StringIO(file.stream.read().decode('utf-8'))
        reader = csv.DictReader(stream)
        if column not in reader.fieldnames:
            return jsonify({'error': f'Column "{column}" not found in CSV'}), 400

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([column])
        for row in reader:
            writer.writerow([row[column]])
        output.seek(0)

        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'extracted_{column}.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
