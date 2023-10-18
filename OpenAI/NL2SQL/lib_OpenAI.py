import os
import getpass
from dotenv import load_dotenv, dotenv_values
import pandas as pd
import openai

from IPython.display import display, Markdown, Latex, HTML, JSON
import sqlite3
from sqlite3 import Error
import pymysql
from sqlalchemy import create_engine, text as sql_text

import langchain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from cmd import PROMPT
import os
from pyexpat.errors import messages

import openai
import tiktoken

class GenAI_NL2SQL():
    def __init__(self, OPENAI_API_KEY, Model, Encoding_Base, Max_Tokens, Temperature, \
                  Token_Cost, DB, MYSQL_User, MYSQL_PWD):
        self._Model = Model
        self._Encoding_Base = Encoding_Base
        self._Max_Tokens = Max_Tokens
        self._Temperature = Temperature
        self._Token_Cost = Token_Cost
        self._OpenAI_API_Key = OPENAI_API_KEY
        self._DB = DB
        self._MYSQL_User=MYSQL_User 
        self._MYSQL_PWD=MYSQL_PWD
        self.Set_OpenAI_API_Key()

    def Set_OpenAI_API_Key(self):
        openai.api_key = self._OpenAI_API_Key
        return 0
    
    def Print_Open_AI_Key(self):
        print(self._OpenAI_API_Key)

    def Print_MySQL_Keys(self):
        print()

    # count the number of input tokens in prompt
    def Num_Tokens_From_String(self, Prompt: str, Verbose=False) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(self._Encoding_Base)
        num_tokens = len(encoding.encode(Prompt))
        if Verbose:
            print(f'number of tokens {num_tokens}')
        return num_tokens
    
   ############################################################################## 
    # Extimate prompt cost per GPT model
    def Prompt_Cost(self, Prompt):
        Cost = self._Token_Cost[self._Model]  # cost per 1K tokens
        Input_Cost = Cost['Input']*self.Num_Tokens_From_String(Prompt)
        return(Input_Cost, self.Num_Tokens_From_String(Prompt, Verbose=False))
    
    def OpenAI_Usage_Cost(self, Response):
        Cost = self._Token_Cost[self._Model]  # cost per 1K tokens
        Total_Cost = Cost['Input']*Response['usage']['prompt_tokens'] + \
            Cost['Output']*Response['usage']['completion_tokens']
        return(Total_Cost, Response['usage']['total_tokens'])

  ##############################################################################  
    def Prompt_Question(self, _Prompt_Template_, Inputs):
        """
        """
    #    print(f'Inputs {Inputs}')
        for i,j in Inputs.items():
            Prompt = _Prompt_Template_.replace(i,j)
        return Prompt

##############################################################################
    def OpenAI_Completion(self, Prompt):
        Response = openai.Completion.create(
            model=self._Model,
            prompt=Prompt,
            max_tokens=self._Max_Tokens,
            temperature=self._Temperature
        )
        return(Response)

#############################################################################
    def OpenAI_Text_Extraction(self, Response, Type='SQL'):
        if Type == 'SQL':
            Txt = Response['choices'][0]['text']
        else:
            print(f'Type: {Type} is Unsupported ')
            txt = ''
        return(Txt)

##############################################################################
    def execute_query(self, conn, query=None):
        """
        """
        cur = conn.cursor()
        cur.execute(query)
        #cur.execute("SELECT * FROM employee limit 5")
    
        rows = cur.fetchall()
    
        for row in rows:
            print(row)
##############################################################################
    def run_query(self, Conn=None, DB=None, DBFile = None, Query=None, Verbose=True):
        """
        """
        # initialize empty dataframe
        df = pd.DataFrame()
        status = 0

        if Conn:
            try:
                return(pd.DataFrame(pd.read_sql(Query, Conn)))
            except Error as e:
                print(e)  
                return -20  
        else:
            if DB == 'sqlite':
                try:
                    Conn = sqlite3.connect(DBFile)
                except Error as e:
                    print(e)
                    return -20
                try:
                    return(pd.DataFrame(pd.read_sql(Query, Conn)))
                except Error as e:
                    print('read_sql_query error - sqlite')
                    return -1
                   
            elif DB == 'mysql':
                try:
                    Conn = create_engine(f'mysql+pymysql://{self._MYSQL_User}:{self._MYSQL_PWD}@localhost/fakebank')
                except:
                    print('failed to connect to mysql DB')
                    return -1
                try:
                    df = pd.read_sql_query(con=Conn.connect(),sql=sql_text(Query))
                    return status, df
                except :
                    print('read_sql_query error - mysql')
                    status = -5
                    return status, df
            else:
                print('DB is unsupported')
                status = -10
                return status, df

##############################################################################    
    def Prompt_Query(self, Prompt_Template, Question, Verbose):
        status = 0
        df = pd.DataFrame()

        # Construct prompt
        Prompt = self.Prompt_Question(Prompt_Template,{'{Question}':Question})
        # Estimate input prompt cost
        Cost, Tokens_Used  = self.Prompt_Cost(Prompt)
        if Verbose:
            print('Input')  
            print(f'Total Cost: {round(Cost,3)} Tokens Used {Tokens_Used}')
    
    # Send prompt to LLM
        Response = self.OpenAI_Completion(Prompt)
        Cost, Tokens_Used  = self.OpenAI_Usage_Cost(Response)
        if Verbose:
            print('Output')  
            print(f'Total Cost: {round(Cost,3)} Tokens Used {Tokens_Used}','\n') 

    # extract query from LLM response
        Query = self.OpenAI_Text_Extraction(Response, Type='SQL')
        if Verbose:
            print(Query) 

        return Query

##############################################################################
    # Given an single input question, run the entire process
    def GPT_Completion(self, Question, Prompt_Template, Correct_Query=False, Correction_Prompt=None, \
                       Max_Iterations=0,Verbose=False, QueryDB = False):
    
        Correct_Query_Iterations = 0
    
    # Construct prompt
        Prompt = self.Prompt_Question(Prompt_Template,{'{Question}':Question})
        Query = self.Prompt_Query(Prompt_Template, Question, Verbose=True)
        
    # Test query the DB - 
        if QueryDB:
            status, df = self.run_query(Query = Query, DB=self._DB)

            # if query was malformed, llm halucianated for example
            if Correct_Query and (status == -5):
                while (status == -5) and (Correct_Query_Iterations < Max_Iterations): 
                    Correct_Query_Iterations += 1
                    print('Attempting to correct query syntax error')
                    Query = self.Prompt_Query(Correction_Prompt, Question, Verbose)
            # Query the DB
                    status, df = self.run_query(Query = Query, DB=self._DB)          
            print('\n',df)

    # Return Query
        return Query

##############################################################################
# Encoding/Decoding
    def Encoding(self, Txt, Verbose=False):
        encoding = tiktoken.get_encoding(self._Encoding_Base)
        self.encodings = encoding.encode(Txt)
        if Verbose:
            print(f'encodings:  {self.encodings}')
        return self.encodings
    
    def Decoding(self, Txt=None, Verbose=False):
        if not Txt:
            Txt = self.encodings
        encoding = tiktoken.get_encoding(self._Encoding_Base)
        self.decoded_txt = encoding.decode(Txt)
        if Verbose:
            print(f'decoded text:  {self.decoded_txt}')
        return self.decoded_txt

############################################################################## 
    def Load_Prompt_Template(self, File=None):
        if File:
            try:
                with open(File, 'r') as file:
                    Template = file.read().replace('\n', '')
            except:
                print(f'Prompt file {File} load failed ')
                return 0
        return Template


#############################################################################
    def LangChain_Initiate_LLM(self, Model='OpenAI'):
        if Model=='OpenAI':
            self._LLM = OpenAI(temperature=self._Temperature, model_name=self._Model, \
                max_tokens=self._Max_Tokens, openai_api_key=self._OpenAI_API_Key)
            return 0
        else:
            print('Model Unsupported')
            return -1
            
    # Langchain Completion
    def LangChainCompletion(self, Prompt, Input):
        chain = LLMChain(llm=self._LLM, prompt=Prompt)
        return chain.run(Input) 
    

