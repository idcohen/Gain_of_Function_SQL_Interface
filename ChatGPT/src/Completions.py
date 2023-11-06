# for local modules
import sys
sys.path.append(r"/Users/dovcohen/Documents/Projects/AI/NL2SQL")

import os
import getpass
from dotenv import load_dotenv
import pandas as pd
import argparse
from ChatGPT.src.lib.Flask_Data_Exchage import Flask_data_exchange
from ChatGPT.src.lib.lib_OpenAI import GenAI_NL2SQL 

# from ChatGPT.src.lib.lib_Vector_Datastore import VDS

# Directories
WD = "/Users/dovcohen/Documents/Projects/AI/NL2SQL/ChatGPT"
Flask_output_dir = "Output"

# write Query and DF to temp files
Query_filename = "Query.sql"
Results_filename = "Results.csv"

def Instantiate_OpenAI_Class(VDSDB_Filename=None):
    load_dotenv("/Users/dovcohen/.NL2SQL_env")
    # SQL DB
    DB = 'mysql'
    MYSQL_USER = os.getenv("MYSQL_USER", None)
    MYSQL_PWD = os.getenv("MYSQL_PWD", None)

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

    # LLM parameters
    Model = "gpt-3.5-turbo-instruct"
    Embedding_Model = "text-embedding-ada-002"
    Encoding_Base = "cl100k_base"
    Max_Tokens = 250
    Temperature = 0
    Token_Cost = {"gpt-3.5-turbo-instruct":{"Input":0.0015/1000,"Output":0.002/1000},
                  "text-embedding-ada-002":{"Input":0.0001/1000, "Output":0.0001/1000}}
    
    VDSDB = "Dataframe"

    if VDSDB_Filename is None:  
        VDSDB_Filename = "../Vector_DB/Question_Query_Embeddings-1.txt"


    #Instantiate GenAI_NL2SQL Object
    return GenAI_NL2SQL(OPENAI_API_KEY, Model, Embedding_Model, Encoding_Base, Max_Tokens, Temperature, \
                        Token_Cost,DB, MYSQL_USER, MYSQL_PWD, VDSDB, VDSDB_Filename)

def main(Input=None, Req=None, Flask_mode = False, Verbose=False):
    if Req == 'Query':
        GPT3 = Instantiate_OpenAI_Class()
        # 
        Question = Input

        Prompt_Template_File = f"../prompt_templates/Template_3.txt"
        Correction_Prompt_File = r"../prompt_templates/Correction_Template.txt"
        # Update VDS
        Update_VDS=True
        Prompt_Update = True
        Verbose = True
        if Flask_mode:  
            Prompt_Update = False
            Verbose = False
     

        Prompt_Template, status = GPT3.Load_Prompt_Template(File=Prompt_Template_File )
        if status != 0:
            print(f'{Prompt_Template_File } failed to load')
            return ""
        
        Correction_Prompt, status = GPT3.Load_Prompt_Template(File=Correction_Prompt_File )
        if status != 0:
            print(f'{Correction_Prompt_File } failed to load')
            return ""

        if Verbose:
            print(f'LLM Natural Language to SQL translator')
            print(f'Using {GPT3._LLM_Model} set at temperature {GPT3._Temperature} \n')

        if Question is None:
            Question = input('Prompt> Question: ')

        Query, df = GPT3.GPT_Completion(Question, Prompt_Template, Correct_Query=False,  \
                                    Correction_Prompt= Correction_Prompt, \
                                    Max_Iterations=2, Verbose=Verbose, QueryDB = True,
                                    Update_VDS=Update_VDS, Prompt_Update=Prompt_Update)
        
        
        if Flask_mode:
            Fde = Flask_data_exchange(WD, Output_dir= Flask_output_dir)
            Fde.Write_query(Query, Query_filename)
            Fde.Output_results_df(df, Results_filename)

        return(Query)
    
    elif Req == 'Embedding':
        VDSDB_Filename = Input
        GPT3 = Instantiate_OpenAI_Class(VDSDB_Filename=VDSDB_Filename)
        rtn = GPT3.Populate_Embeddings_from_DF_Column(Verbose=True)
    
if __name__ == '__main__':
    p = argparse.ArgumentParser('Natural Language to SQL')
    p.add_argument('-E', action='store_true', help=" 'Filename' {Calculate Embeddings from Dataframe File}", default=False)
    p.add_argument('-q', action='store_true', help=" 'Question' {generate SQL query from question}", default=False)
    p.add_argument('-v', action='store_true', help=" Verbose Mode", default=False)
    p.add_argument('-F', action='store_true', help=" Flask Mode", default=False)
    p.add_argument('-T', action='store_true', help=" Test Mode", default=False)
    p.add_argument('Question_Filename', type=str, nargs=1) 
   
    args = p.parse_args()

    Verbose = True if args.v == True else False
    Flask_mode = True if args.F == True else False
    Test_mode = True if args.T == True else False


    if args.q == True:
        Question = args.Question_Filename[0]
        if Flask_mode == False:
            print(Question)
        Query =  main(Question, Req='Query', Flask_mode=Flask_mode, Verbose=Verbose)
       # print(Query)
    elif args.E == True:
        Filename = args.Question_Filename[0]
        print(Filename)
        rtn=  main(Filename, Req='Embedding',Verbose=args.V)
    elif Test_mode:
        pass
    else:
        print('unsupported option')
        


    #txt = "Hello World"
    #GPT3.Encoding(txt, Verbose=True)
    #GPT3.Decoding(Verbose=True)
