# file lib_OpenAI_Embeddings
import os
import pandas as pd
from openai.embeddings_utils import get_embedding
import openai
import sys
from OpenAI.src.lib.OpenAI_Func import Num_Tokens_From_String, OpenAI_Embeddings_Cost, OpenAI_Embeddings_Cost

#############################################################################
class OpenAI_Embeddings():
    def __init__(self, Filename, Encoding_Base, Model, Token_Cost, Max_Tokens):
        self._DBFilename = Filename
        self._Encoding_Base = Encoding_Base
        self._Model = Model
        self._Token_Cost = Token_Cost
        self._Max_Tokens = Max_Tokens
        self._VDS_DF = pd.DataFrame()
        self._Embedding = []

#############################################################################
# OpenAI Embeddings - returns list
    def OpenAI_Get_Embedding(self, Text='', Verbose=False):
        # replace line return
        if Text != '':
            Text = Text.replace("\n", " ")
            # check if tokens is under max tokens for model
            ntokens = Num_Tokens_From_String(Text)
            if ntokens < self._Max_Tokens:  
                try:
                    #Make your OpenAI API request here
                    response= openai.Embedding.create(input=[Text],model=self._Model)
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
                cost, tokens = OpenAI_Embeddings_Cost(response, self._Token_Cost, self._Model)
                if Verbose:
                    print(f'Embeddings Cost {cost} and tokens {tokens}')
                return embeddings

#############################################################################
# Calculate Embeddings for DF columne -- assumes the existance of a Question column 
    def Calculate_VDS_Embeddings_Column(self, df, Verbose=False):
        df['Embedding'] = df.Question.apply(lambda x: self.OpenAI_Get_Embedding(x))
        return 0

#############################################################################
# Calculate Embeddings for DF columne -- assumes the existance of a Question column 
    def Calculate_VDS_Embeddings_DF(self):
        self.Calculate_VDS_Embeddings_Column(self._VDS_DF, Verbose=True)
        return 0


#############################################################################
# Insert row into Embeddings DF
    def Insert_VDS(self, Question, Query, Metadata='', Embedding=[], Verbose=False):
        # tmp dataframe
        df_tmp = pd.DataFrame([Question, Query, Metadata, Embedding],self._VDS_DF.columns,ignore_index=True)
        # append to self._VDS_DF
        df = pd.concat(self._VDS_DF,df_tmp,ignore_index=True)
        # write DF to file
        self._VDS.Store_VDS_DF(df,Verbose=Verbose)
        return 0

#############################################################################
# Calculate Embeddings for DF assumes      
class VDS(OpenAI_Embeddings):

    def Load_VDS_DF(self, Verbose=False):
        # for version 1, import dataframe
        try:
            df = pd.read_excel(self._DBFilename, sheet_name='VDS')
            if Verbose:
                print(f'Load_VDS_DF imported {df.shape[0]} rows from {self._DBFilename}')
            self._VDS_DF = df
            return 0
        except:
            print(f'Load_VDS_DF Error failed to import file {self._DBFilename}')
            return -1

    def Store_VDS_DF(self, df, Verbose=False):
        try:
            df.to_excel(self._DBFilename,sheet_name='VDS',index=False, header=True)
            if Verbose:
                print(f'Store_VDS_DF() wrote {df.shape[0]} rows to file {self._DBFilename}')
            return 0
        except:
            print(f'Store_VDS_DF Error failed to write to {self._DBFilename}')
            return -1

