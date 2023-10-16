import os
import getpass
from dotenv import load_dotenv, dotenv_values
import pandas as pd
import openai

# for local modules
import sys
sys.path.append(r"/Users/dovcohen/Documents/Projects/AI/NL2SQL")
from OpenAI.lib.lib_OpenAI import GenAI_NL2SQL

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
    return GenAI_NL2SQL(OPENAI_API_KEY, Model, Encoding_Base, Max_Tokens, Temperature, Token_Cost,\
                         DB, MYSQL_USER, MYSQL_PWD)



def main():
    GPT3 = Instantiate_OpenAI_Class()

    #txt = "Hello World"
    #GPT3.Encoding(txt, Verbose=True)
    #GPT3.Decoding(Verbose=True)

    Prompt_Template_File = r"OpenAI/prompt_templates/Template_1.txt"
    Correction_Prompt_File = r"OpenAI/prompt_templates/Correction_Template.txt"
    print(f'LLM Natural Language to SQL translator')
    print(f'Using {GPT3._Model} set at temperature {GPT3._Temperature} \n')

    Question = input('Prompt> Question: ')

    Prompt_Template = GPT3.Load_Prompt_Template(File=Prompt_Template_File )
    Correction_Prompt_Template = GPT3.Load_Prompt_Template(File=Correction_Prompt_File )
    Query = GPT3.GPT_Completion(Question, Prompt_Template, Correction_Prompt_Template, Verbose=True, QueryDB = True)

    return 0

if __name__ == '__main__':
    main()
