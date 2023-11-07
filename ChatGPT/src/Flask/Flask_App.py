# Flask_App.py
# input and output pages

from flask import Flask, render_template, request, redirect, url_for
import subprocess
import sys 
import pandas as pd


Wd = '/Users/dovcohen/Documents/Projects/AI/NL2SQL/ChatGPT/src/Flask'
App_dir = '/Users/dovcohen/Documents/Projects/AI/NL2SQL/ChatGPT/src'
Output_dir = '/Users/dovcohen/Documents/Projects/AI/NL2SQL/ChatGPT/Output'
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    Question = None
    if request.method == 'POST':
        Question = request.form['Question']
# -- run
#         NL2SQL(Question)

# -- historical
#         result = subprocess.check_output(['python', 'lib/Completions.py -q', Question]).decode('utf-8')
# -- run
        Query = Read_query_file()
        Results = Read_results_file()
# -- run
#       return render_template('Completions.html', Question=Question, Results=Results.to_html(), Query=Query)
#    return render_template('Completions.html')
        return render_template('output.html',  Question=Question, Results=Results.to_html(), Query=Query)
#        return redirect(url_for('output_page', Question=Question))
    return render_template('input.html')

def NL2SQL(Question):
    result = subprocess.check_output([sys.executable, App_dir + "/Completions.py","-F","-q",Question])
    print(f'result = {result}')

def Read_query_file():
    try:
        Filename = Output_dir + '/Query.sql'
        with open(Filename, 'r') as output_file:
            #k = output_file.read()
            k = output_file.readlines()
        return k
    except FileNotFoundError:
        return None
    
def Read_results_file():
    try:
        Filename = Output_dir + '/Results.xlsx'
       # df = pd.read_csv(Filename)
        df = pd.read_excel(Filename, sheet_name='Flask',parse_dates=True)
        print(f'df {df}')
        return df
    except FileNotFoundError:
        return None

if __name__ == '__main__':
    app.run(debug=True)

    