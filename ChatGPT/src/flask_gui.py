# fapp.py
from flask import Flask, render_template, request
import subprocess
import sys 

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        Question = request.form['Question']
        
        NL2SQL(Question)
#        result = subprocess.check_output(['python', 'lib/Completions.py -q', Question]).decode('utf-8')
        #Query = result.strip().split(',')
        #return render_template('Completions.html', Question, Query)
        Q = read_output_file()
        print(f'Q {Q}')
        return render_template('Completions.html', Question=Question, Query=Q)
    return render_template('Completions.html')

def NL2SQL(Question):
   # subprocess.check_output(['python', 'lib/Completions.py -q', Question]).decode('utf-8')
    #subprocess.check_output(['python', 'Completions.py', "-T", Question])
    result = subprocess.check_output([sys.executable,  "Completions.py","-F","-q",Question])
    print(f'result = {result}')

def read_output_file():
    try:
        with open('../Output/Query.sql', 'r') as output_file:
            k = output_file.read()
            return k
    except FileNotFoundError:
        return None, None
    

if __name__ == '__main__':
    app.run(debug=True)

    