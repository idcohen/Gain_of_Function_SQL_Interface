# fapp.py
from flask import Flask, render_template, request
import subprocess
import sys 
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        Question = request.form['Question']
        
        NL2SQL(Question)

#        result = subprocess.check_output(['python', 'lib/Completions.py -q', Question]).decode('utf-8')
        #Query = result.strip().split(',')
        #return render_template('Completions.html', Question, Query)
        Query = Read_query_file()
        Results = Read_results_file()
        return render_template('Completions.html', Question=Question, Results=Results.to_html(), Query=Query)
    return render_template('Completions.html')

def NL2SQL(Question):
    result = subprocess.check_output([sys.executable,  "Completions.py","-F","-q",Question])
    print(f'result = {result}')

def Read_query_file():
    try:
        Filename = '../Output/Query.sql'
        with open(Filename, 'r') as output_file:
            k = output_file.read()
            return k
    except FileNotFoundError:
        return None
    
def Read_results_file():
    try:
        Filename = '../Output/Results.xlsx'
        df = pd.read_csv(Filename)
        return df
    except FileNotFoundError:
        return None
    

if __name__ == '__main__':
    app.run(debug=True)

    