import os
import getpass
from dotenv import load_dotenv, dotenv_values
import pandas as pd

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

## Embeddings
from openai.embeddings_utils import get_embedding

## Vector Datastore
from OpenAI.NL2SQL.lib_Vector_Datastore import VDS

class GenAI_NL2SQL():
    def __init__(self, OPENAI_API_KEY, Model, Encoding_Base, Max_Tokens, Temperature, \
                  Token_Cost, DB, MYSQL_User, MYSQL_PWD, VDSDB, VDSDB_Filename):
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
        self._VDSDB = VDSDB
        self._VDS = VDS(VDSDB_Filename)

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


    def OpenAI_Embeddings_Cost(self, Response):
        Cost = self._Token_Cost[self._Model]  # cost per 1K tokens
        Total_Cost = Cost['Input']*Response['usage']['total_tokens'] 
        return(Total_Cost, Response['usage']['total_tokens'])
    
  ##############################################################################  
    def Prompt_Question(self, _Prompt_Template_, Inputs):
        """
        """
        for i,j in Inputs.items():
            Prompt = _Prompt_Template_.replace(i,j)
        return Prompt

##############################################################################
    def OpenAI_Completion(self, Prompt):
        try:
            #Make your OpenAI API request here
            response = openai.Completion.create(
            model=self._Model,
            prompt=Prompt,
            max_tokens=self._Max_Tokens,
            temperature=self._Temperature,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        except openai.error.APIError as e:
            #Handle API error here, e.g. retry or log
            print(f"OpenAI API returned an API Error: {e}")
            return -1
        except openai.error.APIConnectionError as e:
            #Handle connection error here
            print(f"Failed to connect to OpenAI API: {e}")
            return -1
        except openai.error.RateLimitError as e:
            #Handle rate limit error (we recommend using exponential backoff)
            print(f"OpenAI API request exceeded rate limit: {e}")
            return -1
        return(response)

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

    # Load Vector Datastore
        rtn = self._VDS.Load_VDS_DF()

    ### Retrieve Question Embeddings
    ### Search Vector Datastore for similar questions

    ### Then feed output to Prompt
    
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
                    Status = 0
            except:
                print(f'Prompt file {File} load failed ')
                Status = -1
                return  "", Status
        return Template, Status


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
    
#############################################################################
# OpenAI Embeddings - returns list
    def OpenAI_Get_Embedding(self, Text=None, Verbose=False):
        # replace line return
        if Text is not None:
            Text = Text.replace("\n", " ")
            # check if tokens is under max tokens for model
            ntokens = self.Num_Tokens_From_String(Text)
            if ntokens < self._Max_Tokens:  
                try:
                    #Make your OpenAI API request here
                    response= openai.Embedding.create(input=Text,model=self._Model)
                except openai.error.APIError as e:
                    #Handle API error here, e.g. retry or log
                    print(f"OpenAI API returned an API Error: {e}")
                    return []
                except openai.error.APIConnectionError as e:
                    #Handle connection error here
                    print(f"Failed to connect to OpenAI API: {e}")
                    return []
                except openai.error.RateLimitError as e:
                    #Handle rate limit error (we recommend using exponential backoff)
                    print(f"OpenAI API request exceeded rate limit: {e}")
                    return []
                
                embeddings = response['data'][0]['embedding']
                cost, tokens = self.OpenAI_Embeddings_Cost(response)
                if Verbose:
                    print(f'Embeddings Cost {cost} and tokens {tokens}')
                return embeddings

#df["embedding"] = df.combined.apply(lambda x: get_embedding(x, engine=embedding_model))
