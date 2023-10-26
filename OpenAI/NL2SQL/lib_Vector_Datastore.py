import pandas as pd

class VDS():
    def __init__(self, Filename):
        self._DBFilename = Filename

    def Load_VDS_DF(self):
        # for version 1, import dataframe
        df = pd.read_excel(self._DBFilename, sheet_name='Sheet1')
        print('Here')
        print(df)
        return df

#### Embeddings
# OpenAI
    def Initialize_OpenAI_Embedding_API(self):
        self._Embedding_Function = embedding_functions.OpenAIEmbeddingFunction(
                api_key="YOUR_API_KEY",
                model_name="text-embedding-ada-002"
            )