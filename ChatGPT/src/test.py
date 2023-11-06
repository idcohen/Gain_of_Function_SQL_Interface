import subprocess
#subprocess.check_output(['python', 'Completions.py -T', Question])
print( 'Running command...' )
#subprocess.run( [ 'cat', 'flask_gui.py' ] )
#subprocess.run( [ 'python', "Completions.py -T" ] )
#subprocess.run( [ 'echo', "$?" ] )
# Even if `cat /foo` fails above, we will always get here.
print( 'All done!' )

import subprocess
import sys

#result = subprocess.run([sys.executable, "-c", "print('ocean')"])
#result = subprocess.run([sys.executable,  "test1.py","1","2"])
Question = 'What are Mary Spock Account Balances on 10/11/2023. Return date, account type, sum(balance) labeled Balance Total'
result = subprocess.run([sys.executable,  "Completions.py","-F","-q",Question])
print(result)

