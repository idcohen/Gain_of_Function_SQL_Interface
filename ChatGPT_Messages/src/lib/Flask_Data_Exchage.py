# Flask_Data_Exchange.py

class Flask_data_exchange():
    def __init__(self, WD, Output_dir, Delimator=None) -> None:
        self._Delimator = Delimator
        self._WD = WD
        self._Output_dir = Output_dir

    def Write_query(self, Query, Filename=None):
            Filename = self._WD + "/" + self._Output_dir + "/" + Filename
            try:
                F = open(Filename, 'w') 
            except:
                print(f'Write_Query: File open error -  {Filename}')
            # format query
            for i in ('SELECT','FROM','INNER JOIN','LEFT JOIN','RIGHT JOIN','ON','WHERE','GROUP BY','AND','OR','ORDER BY'):
                Query = Query.replace(i,f'\n{i}\n')
            for i in (","):
                Query = Query.replace(i,f'{i}\n')
            F.write(Query)
            F.close()

    def Output_results_df(self, df, Filename, Delimator = "|", Verbose=False):   
        # Determine File type (txt with deliminator, xlsx, csvs, etc ...)
        # strip the suffix, e.g. .csv, .xlsx, assume filename is given as prefix-i.suffix
    
        Suffix = Filename[-4:].replace('.','')
        if Suffix in ({'csv', 'txt', 'xlsx'}):
            Format = Suffix
        else:
            print(f'Output_results_df: Unsupported Filetype {Suffix}')
            return 0
        Filename = self._WD + "/" + self._Output_dir + "/" + Filename 
        
        # Convert embedding vector to n columns in dataframe before saving
        if Format == 'xlsx':
            try:
                df.to_excel(Filename,sheet_name='Flask',index=False, header=True)
                if Verbose:
                    print(f'Output_results_df() wrote {df[0]} rows to file {Filename}')
                return 0
            except:
                print(f'Output results df:  Error failed to write to {Filename}')
                return -1
        elif Format == 'csv':
            Delimator = ","
            df.to_csv(Filename,header=True, index=False, sep = Delimator) 

        elif Format == 'txt':
            df.to_csv(Filename,header=True, index=False, sep = Delimator) 

        else:
            print(f"Output_results_df: File format {Format} is not supported")