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
import tiktoken
sys.path.append(r"/Users/dovcohen/Documents/Projects/AI/NL2SQL")
#from .OpenAI_Func import Num_Tokens_From_String, OpenAI_Embeddings_Cost
from ChatGPT.src.lib.OpenAI_Func import Num_Tokens_From_String, OpenAI_Embeddings_Cost
from ChatGPT.src.lib.OpenAI_Func import Prompt_Cost, OpenAI_Usage_Cost
from ChatGPT.src.lib.DB_Func import execute_query, run_query

## Vector Datastore
from ChatGPT.src.lib.lib_OpenAI_Embeddings import VDS, OpenAI_Embeddings

class GenAI_NL2SQL():
    def __init__(self, OPENAI_API_KEY, Model, Embedding_Model, Encoding_Base, Max_Tokens, Temperature, \
                  Token_Cost, DB, MYSQL_User, MYSQL_PWD, UsePrompt = True, UseMessage = False, VDSDB=None, VDSDB_Filename=None):
        self._LLM_Model = Model
        self._Embedding_Model = Embedding_Model
        self._Encoding_Base = Encoding_Base
        self._Max_Tokens = Max_Tokens
        self._Temperature = Temperature
        self._Token_Cost = Token_Cost
        self._OpenAI_API_Key = OPENAI_API_KEY
        self._DB = DB
        self._MYSQL_Credemtals = {'User':MYSQL_User,'PWD':MYSQL_PWD}
        self._UsePrompt = UsePrompt
        self._UseMessage = UseMessage
        self.Set_OpenAI_API_Key()
        if VDSDB is not None:
            self._VDSDB = VDSDB
            self._VDS = VDS(VDSDB_Filename, Encoding_Base, Embedding_Model, Token_Cost, Max_Tokens) 
            self._VDS.Load_VDS_DF(Verbose=False)
        
    def Set_OpenAI_API_Key(self):
        openai.api_key = self._OpenAI_API_Key
        return 0
    
    def Print_Open_AI_Key(self):
        print(self._OpenAI_API_Key)

    def Print_MySQL_Keys(self):
        print(self._MYSQL_Credemtals)

  
  ##############################################################################  
    def Prompt_Question(self, _Prompt_Template_, Inputs, Write_Template=True):
        """
        """
        for i,j in Inputs.items():
            Prompt = _Prompt_Template_.replace(i,j)

        if Write_Template:
            filename = '../prompt_templates/Template_tmp.txt'
            prompt_file = open(filename, 'w') 
            prompt_file.write(Prompt)
            prompt_file.close()
        return Prompt

  ###############################################################################  

    def Insert_N_Shot_Examples(self, _Prompt_Template_, N_Shot_Examples, Verbose=False):
        """
        """
        # prepare Examples text
        # Question = ....
        # Query = ...

        Examples = '\n'
        for i in range(len(N_Shot_Examples['Question'])):
            Examples += f"Question: {N_Shot_Examples['Question'][i]} \nQuery: {N_Shot_Examples['Query'][i]} \n\n"

        # insert into template
            Prompt_Template = _Prompt_Template_.replace('{EXAMPLES}', Examples)
        if Verbose:
            print(f'Insert_N_Shot_Examples: {Prompt_Template}')
        return Prompt_Template
            
##############################################################################
    def OpenAI_Completion(self, Prompt):
        try:
            #Make your OpenAI API request here
            response = openai.Completion.create(
            model=self._LLM_Model,
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
    def OpenAI_ChatCompletion(self, messages):
        try:
            #Make your OpenAI API request here
            response = response = openai.ChatCompletion.create(
                model=self._LLM_Model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Knock knock."},
                    {"role": "assistant", "content": "Who's there?"},
                    {"role": "user", "content": "Orange."},
                ],
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
            ## Call prompt that removes extraneaous characters from the returned query
            Txt = str(Response['choices'][0]['text'])
            if Txt[0:7] == "\nQuery:":
                Txt = Txt[7:]
        elif Type == 'Text':
            Txt = str(Response['choices'][0]['text'])
        else:
            print(f'Type: {Type} is Unsupported ')
            Txt = ''
        return(Txt)


##############################################################################    
    def Prompt_Query(self, Prompt_Template, Question = '', N_Shot_Examples = None, Verbose=False, Debug=False):
        status = 0
        df = pd.DataFrame()

# Prompt for Model 3-turbo 
        if self._UsePrompt:
            Prompt_Template = self.Insert_N_Shot_Examples(Prompt_Template, N_Shot_Examples)

            # Construct prompt
            Prompt = self.Prompt_Question(Prompt_Template,{'{Question}':Question})

            # Estimate input prompt cost
            Cost, Tokens_Used  = Prompt_Cost(Prompt, self._LLM_Model, self._Token_Cost, self._Encoding_Base)
            if Verbose:
                print('Input')  
                print(f'Total Cost: {round(Cost,3)} Tokens Used {Tokens_Used}')
        
        # Send prompt to LLM
            Response = self.OpenAI_Completion(Prompt)
            if Debug:
                print(f'Prompt: \n',Prompt,'\n')
                print('Response \n',Response,'\n')
            Cost, Tokens_Used  = OpenAI_Usage_Cost(Response, self._LLM_Model, self._Token_Cost )
            
            if Verbose:
                print('Output')  
                print(f'Total Cost: {round(Cost,3)} Tokens Used {Tokens_Used}','\n') 

    # extract query from LLM response
        Query = self.OpenAI_Text_Extraction(Response, Type='SQL')

        return Query

##############################################################################
    # Given an single input question, run the entire process
    def GPT_Completion(self, Question, Prompt_Template, Correct_Query=False, Correction_Prompt=None, \
                       Max_Iterations=0,Verbose=False, QueryDB = False, Update_VDS=True, Prompt_Update=True):
    
        Correct_Query_Iterations = 0

    # Request Question Embedding vector
        Question_Emb = self._VDS.OpenAI_Get_Embedding(Text=Question, Verbose=False)
        
    # Search Vector Datastore for similar questions
        rtn = self._VDS.Search_VDS(Question_Emb, Similarity_Func = 'Cosine', Top_n=3)
        Prompt_Examples = {'Question':rtn[1], 'Query':rtn[2]}

    # Construct prompt
        Query = self.Prompt_Query(Prompt_Template, Question, N_Shot_Examples = Prompt_Examples, Verbose=False)
        if Verbose:
            print(f'Query: \n {Query} \n')

    # Test query the DB - 
        if QueryDB:
            status, df = run_query(Query = Query, Credentials = self._MYSQL_Credemtals, DB=self._DB, Verbose=False)
            # if query was malformed, llm halucianated for example
            if Correct_Query and (status == -5):
                while (status == -5) and (Correct_Query_Iterations < Max_Iterations): 
                    Correct_Query_Iterations += 1
                    print('Attempting to correct query syntax error')
                    Query = self.Prompt_Query(Correction_Prompt, Question, Verbose=False)
            # Query the DB
                    status, df = run_query(Query = Query, Credentials = self._MYSQL_Credemtals,\
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
