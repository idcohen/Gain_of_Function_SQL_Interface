# fapp.py
from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        Question = request.form['Question']
        
        # Call the print_ij.py script with i and j as arguments
        result = subprocess.check_output(['python', '../src/Completions.py', Question]).decode('utf-8')
        Query = result.strip().split(',')
        return render_template('Completions.html', Question, Query)
    return render_template('Completions.html')

if __name__ == '__main__':
    app.run(debug=True)