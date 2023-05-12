import sidrapy


# Importa as variações do IPCA
def get_ipca_series():
    df = sidrapy.get_table(table_code = '1737',
                                territorial_level = '1',
                                ibge_territorial_code = 'all',
                                variable = '63, 69',    # incluir 69 para anual
                                period = 'all',
    )
    return df

def get_ipca():
    df = sidrapy.get_table(table_code = '1737',
                                territorial_level = '1',
                                ibge_territorial_code = 'all',
                                variable = '63, 69',    # incluir 69 para anual
    )
    return df

# Trata dataframe de IPCA.
def clean_ipca(df):
    #Renomeia as colunas com os dados da primeira linha
    df.columns = df.iloc[0]
    df = df[1:]
    df.reset_index(drop=True, inplace=True)

    # Elimina colunas não utilizadas e renomeia as demais.
    df = (
        df
        .rename(columns ={'Mês (Código)' : 'date',
                          'Variável (Código)' : 'variable',
                          'Valor' : 'percent_value'})
        .drop(columns=["Nível Territorial (Código)",
                       "Nível Territorial",
                       "Unidade de Medida (Código)",
                       "Unidade de Medida",
                       "Brasil (Código)",
                       "Brasil",
                       "Mês",
                       "Variável"])
        .replace("...",'0')
        .astype({'percent_value' : 'float'})
    )
    return df



    # Cria algumas colunas necessárias.
def ipca_new_columns(df):
    df = (
        df
        .assign(year = df['date'].apply(lambda x : str(x)[:4]),
                month = df['date'].apply(lambda x : str(x)[4:6]),
                value = df['percent_value'].apply(lambda x : x/100 + 1))
        .astype({'year' : 'int',
                'month' : 'int'})
    )
    return df

def set_deflator(df,year,month=None):
    if month:
        fix_index = df.loc[(df.year==year) & (df.month==month),'index_number'].values[0]
    else:
        fix_index = df.loc[df.year==year,'index_number'].values[0]

    df = df.assign(relative_index = df['index_number'] / fix_index)
    return df



def monthly_ipca():
    df = get_ipca_series()
    df = clean_ipca(df)
    df = ipca_new_columns(df)
    df = df[(df['variable']=='63')]
    df = df.assign(index_number = df['value'].cumprod())
    return df


def anual_ipca():
    df = get_ipca_series()
    df = clean_ipca(df)
    df = ipca_new_columns(df)
    df = df[(df['variable']=='69') & (df['month']==12)]
    df = df.assign(index_number = df['value'].cumprod())
    df = set_deflator(df, 2022)
    return df

def current_ipca():
    df = get_ipca()
    df = clean_ipca(df)
    df = ipca_new_columns(df)
    df = df[(df['variable']=='63')]
    df = df.assign(index_number = df['value'].cumprod())
    return df


if __name__ == "__main__":
    
    # Import and clean data
    ipca_anual = anual_ipca()
    ipca_mensal = monthly_ipca()
    ipca_corrente = current_ipca()

    # Save file
    ipca_anual.to_csv('data/ipca_anual.csv', encoding='UTF-8', index=False)

    print(ipca_corrente)

    exit()
