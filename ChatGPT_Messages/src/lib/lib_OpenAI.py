# sys.path.append(r"/Users/dovcohen/Documents/Projects/AI/NL2SQL")
import sys
import getpass
from dotenv import load_dotenv, dotenv_values
import pandas as pd

from IPython.display import display, Markdown, Latex, HTML, JSON

import langchain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from cmd import PROMPT
import os
from pyexpat.errors import messages

import openai

#from ChatGPT_Messages.src.lib.OpenAI_Func import Num_Tokens_From_String, OpenAI_Embeddings_Cost, Prompt_Cost
from ChatGPT_Messages.src.lib.OpenAI_Func import OpenAI_Usage_Cost
from ChatGPT_Messages.src.lib.DB_Func import Execute_Query, Run_Query

## Vector Datastore
from ChatGPT_Messages.src.lib.lib_OpenAI_Embeddings import VDS, OpenAI_Embeddings

class GenAI_NL2SQL():
    def __init__(self, OPENAI_API_KEY, Model, Embedding_Model, Encoding_Base, Max_Tokens, Temperature, \
                  Token_Cost, DB, MYSQL_User, MYSQL_PWD, WD, VDSDB=None, VDSDB_Filename=None):
        self._LLM_Model = Model
        self._Embedding_Model = Embedding_Model
        self._Encoding_Base = Encoding_Base
        self._Max_Tokens = Max_Tokens
        self._Temperature = Temperature
        self._Token_Cost = Token_Cost
        self._OpenAI_API_Key = OPENAI_API_KEY
        self._DB = DB
        self._MYSQL_Credentials = {'User':MYSQL_User,'PWD':MYSQL_PWD}
        self._WD = WD
        self.Set_OpenAI_API_Key()
        if VDSDB is not None:
            self._VDSDB = VDSDB
            self._VDS = VDS(VDSDB_Filename, Encoding_Base, Embedding_Model, Token_Cost, Max_Tokens) 
            self._VDS.Load_VDS_DF(Verbose=False)
        self._Message_Template = f'{self._WD}/Message_Templates/Template_MySQL.txt'
        self._Messages = [] # message a list of dictionary elements
        
    def Set_OpenAI_API_Key(self):
        openai.api_key = self._OpenAI_API_Key
        return 1
    
    def Print_Open_AI_Key(self):
        print(self._OpenAI_API_Key)

    def Print_MySQL_Keys(self):
        print(self._MYSQL_Credemtals)
    
#############################################################################
    def OpenAI_ChatCompletion(self):
        try:
            response = openai.ChatCompletion.create(
                model=self._LLM_Model,
                messages=self._Messages,
                max_tokens=self._Max_Tokens,
                temperature=self._Temperature,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            status = 0
        except openai.error.APIError as e:
            #Handle API error here, e.g. retry or log
            print(f"OpenAI API returned an API Error: {e}")
            status = -1
            return {}, status
        except openai.error.APIConnectionError as e:
            #Handle connection error here
            print(f"Failed to connect to OpenAI API: {e}")
            status = -1
            return {}, status
        except openai.error.RateLimitError as e:
            #Handle rate limit error (we recommend using exponential backoff)
            print(f"OpenAI API request exceeded rate limit: {e}")
            status = -1
            return {}, status
        return response, status

##############################################################################
    # Given an single input question, run the entire process
    def GPT_ChatCompletion(self, Question, Max_Iterations=0, Verbose=False, QueryDB = False, 
                       Correct_Query=False, Update_VDS=True, Prompt_Update=True):
        """
            Method to Orchestrate Process
        
        """
    # Request Question Embedding vector
        Question_Emb = self._VDS.OpenAI_Get_Embedding(Text=Question, Verbose=Verbose)
        
    # Search Vector Datastore for similar questions
        rtn = self._VDS.Search_VDS(Question_Emb, Similarity_Func = 'Cosine', Top_n=3)
        N_Shot_Examples = {'Question':rtn[1], 'Query':rtn[2]}

    # Construct prompt
        Query, Status = self.Message_Query(Question, N_Shot_Examples = N_Shot_Examples, Verbose=Verbose, Debug=False)
        
        if Status == -100:
            return 
        if Verbose:
            print(f'Query: \n {Query} \n')

    # Test query the DB - 
        if QueryDB:
            status, df = Run_Query(Query = Query, Credentials = self._MYSQL_Credentials, DB=self._DB, Verbose=False)
            print(f'Status {status}')
            
            # Correct query if malformed
            if Correct_Query and (status == -5):
                while (status == -5) and (Correct_Query_Iterations < Max_Iterations): 
                    Correct_Query_Iterations += 1
                    print('Attempting to correct query syntax error')
                    # need to append message with returned error, want correction vds
                    " for example - I'm sorry, but I cannot provide the answer to that question as there is no table or column in the given database schema that contains transaction balances."
                    Query = self.Prompt_Query(Correction_Prompt, Question, Verbose=False)
            # Query the DB
                    status, df = Run_Query(Query = Query, Credentials = self._MYSQL_Credentials,\
                    DB=self._DB, Verbose=False)    

            if Verbose:      
                print(f'Results of query: \n',df)

        if Update_VDS:
            if Prompt_Update:
                rtn = ''
                while rtn not in ('Y','N'):
                    print(f'Add results to Vector Datastore DB? Y or N')
                    rtn = input('Prompt> ')
                if rtn == 'Y':
                    self._VDS.Insert_VDS(Question=Question, Query=Query, Metadata='',Embedding=Question_Emb)
            else:
                self._VDS.Insert_VDS(Question=Question, Query=Query, Metadata='',Embedding=Question_Emb)
    # Return Query
        return Query, df
    
#############################################################################
    def OpenAI_Response_Parser(self, Response, Debug=False):

        if Debug:
            print(f'Response {Response}')
    
        id = Response['id']
        object = Response['object']
        if object == 'text_completion':
            Txt = str(Response['choices'][0]['text'])
            if Txt[0:7] == "\nQuery:":
                Txt = Txt[7:]
        elif object == 'chat.completion':
            Txt = str(Response['choices'][0]['message']['content'])
        else:
            print(f'Reponse object: {object} is Unsupported ')
            Txt = ''
        return(Txt)

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
            self._LLM = OpenAI(temperature=self._Temperature, model_name=self._LLM_Model, \
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
    def Populate_Embeddings_from_DF_Column(self,Verbose=False):
        self._VDS.Retrieve_Embeddings_DF_Column(Verbose=Verbose)
        return 0

##############################################################################
# Prepare Message list    
    def Prepare_Message_Template(self, Verbose=False, Debug=False):
        # Import Mesage Template file
        Filename = self._Message_Template 
        # Filename = self._MessageTemplate
        try:
            with open(Filename, 'r') as file:
                Template = file.read().replace('\n', '')
                Status = 0
        except:
            print(f'Prompt file {Filename} load failed ')
            Status = -1
            return  "", Status
        
        Messages = [{"role": "system", "content": Template}]
        if Debug:
            print(f'Prepare Message Template: \n {Messages} \n end \n')
        self._Messages = Messages
        return Status
    
##############################################################################  
# Insert_N_Shot_Messages
    def Append_N_Shot_Messages(self, N_Shot_Examples, Verbose=False, Debug=False):
        """
            Append example questions and queries into message list for ChatCompletion API
        """ 

        for i in range(len(N_Shot_Examples['Question'])):
            self._Messages.append({"role": "system", "name":"example_user", "content": N_Shot_Examples['Question'][i]})
            self._Messages.append({"role": "system", "name":"example_assistant", "content": N_Shot_Examples['Query'][i]})
            
        status = 0
        return status
    
##############################################################################    
    def Append_Queston(self, Question, Verbose=True, Debug=False):
        """
            Append question  into message list for ChatCompletion API
         """  
        self._Messages.append({"role": "user", "content": Question})
        status = 0
        return status
                        
##############################################################################    
    def Message_Query(self, Question = '', N_Shot_Examples = None, Verbose=False, Debug=True):
        """
        Message dictionary format for ChatCompletion API
        """
        Status = 0
        df = pd.DataFrame()
        
        # Prepare Message Template
        Status = self.Prepare_Message_Template(Verbose)

        # Insert Example Messages
        Status = self.Append_N_Shot_Messages(N_Shot_Examples, Verbose=Verbose)

        # Insert question
        Status = self.Append_Queston(Question, Verbose=Verbose)
        
        if Debug:
            print(f' Message_Query: \n {self._Messages}')

        # Estimate input prompt cost
#        Cost, Tokens_Used  = Prompt_Cost(Prompt, self._LLM_Model, self._Token_Cost, self._Encoding_Base)
#        if Verbose:
#            print('Input')  
#            print(f'Total Cost: {round(Cost,3)} Tokens Used {Tokens_Used}')
    
    # Send prompt to LLM
        Response, Status = self.OpenAI_ChatCompletion()

        if Debug:
            print(f'Status {Status} \n Response {Response} \n')
       
        Cost, Tokens_Used  = OpenAI_Usage_Cost(Response, self._LLM_Model, self._Token_Cost )
        
        if Verbose:
            print(f'Total Cost: {round(Cost,3)} Tokens Used {Tokens_Used}','\n') 

    # extract query from LLM response
        Query = self.OpenAI_Response_Parser(Response)

        return Query, Status

##############################################################################    
    
