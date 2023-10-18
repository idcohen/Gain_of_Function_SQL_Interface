import os
import getpass
from dotenv import load_dotenv
import pandas as pd
import argparse
import openai

# for local modules
import sys

sys.path.append(r"/Users/dovcohen/Documents/Projects/AI/NL2SQL")
from OpenAI.NL2SQL.lib_OpenAI import GenAI_NL2SQL

def Instantiate_OpenAI_Class():
    load_dotenv("/Users/dovcohen/.env")
    # SQL DB
    DB = 'mysql'
    MYSQL_USER = os.getenv("MYSQL_USER", None)
    MYSQL_PWD = os.getenv("MYSQL_PWD", None)

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

    # LLM parameters
    Model = "gpt-3.5-turbo-instruct"
    Encoding_Base = "cl100k_base"
    Max_Tokens = 250
    Temperature = 0
    Token_Cost = {"gpt-3.5-turbo-instruct":{"Input":0.0015/1000,"Output":0.002/1000}}

    #Instantiate GenAI_NL2SQL Object
    return GenAI_NL2SQL(OPENAI_API_KEY, Model, Encoding_Base, Max_Tokens, Temperature, \
                        Token_Cost,DB, MYSQL_USER, MYSQL_PWD)



def main(Question=None):
    GPT3 = Instantiate_OpenAI_Class()

    #txt = "Hello World"
    #GPT3.Encoding(txt, Verbose=True)
    #GPT3.Decoding(Verbose=True)

    # 
    Prompt_Template_File = f"../prompt_templates/Template_1.txt"
    Correction_Prompt_File = r"../prompt_templates/Correction_Template.txt"

    Prompt_Template = GPT3.Load_Prompt_Template(File=Prompt_Template_File )
    Correction_Prompt = GPT3.Load_Prompt_Template(File=Correction_Prompt_File )
    print(f'LLM Natural Language to SQL translator')
    print(f'Using {GPT3._Model} set at temperature {GPT3._Temperature} \n')

    if Question is None:
       Question = input('Prompt> Question: ')

    Query = GPT3.GPT_Completion(Question, Prompt_Template, Correct_Query=True,  \
                                Correction_Prompt= Correction_Prompt, \
                                Max_Iterations=2, Verbose=False, QueryDB = True)
    return(Query)

if __name__ == '__main__':
    p = argparse.ArgumentParser('Natural Language to SQL')
    p.add_argument('-q', action='store_true', help='Question flag', default='False')
    p.add_argument('Question', type=str, nargs=1, \
                    help='Question to pass to LLM')
    args = p.parse_args()

    if args.q:

        Question = args.Question[0]
        print(Question)
        Query =  main(Question)
       # print(Query)
