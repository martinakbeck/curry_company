import inflection
import plotly.express as px

def clean_code(df1):
    df1 = rename_columns(df1)
    #ver soma de valores nulos por coluna
    ##df1.isnull().sum()

    #tirar dados duplicados
    df1 = df1.drop_duplicates()

    #excluir NaN
    df1 = df1.dropna()

    #Categorizar, inicialmente, por um tipo de comida
    df1["cuisines"] = df1.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

    #alterar valores das colunas
    df1["country_code"] = df1.loc[:, "country_code"].apply(lambda x: country_name(x))
    df1["rating_color"] = df1.loc[:, "rating_color"].apply(lambda x: color_name(x))
    df1["price_range"] = df1.loc[:, "price_range"].apply(lambda x: create_price_tye(x))
    
    return df1

#======================================
##           Funções Senior          ##
#======================================

#Preencher nome dos países
COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}
def country_name(country_id):
    return COUNTRIES[country_id]

#Criação do Tipo de Categoria de Comida
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"
    
#Criação do nome das Cores
COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]

#Renomear as colunas do DataFrame
def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df


#download arquivo
def convert_df(df1):
    return df1.to_csv().encode('utf-8')


#============================================
#               Funções Análises
#============================================

#metricas gerais
def metricas_gerais(df1, coluna):
    ''' Função que pega conta o valor único de cada coluna '''
    metrica = len(df1.loc[:, coluna].unique())
    return metrica

#média nota por tipo culinário
def media_culinaria(df1, tipo):
    ''' Função que gera a média da avaliação por tipo culinário
        Retorna a média da avaliação e o nome do restaurante
    
    '''
    df_aux = (df1.loc[df1['cuisines'] == tipo, ['aggregate_rating', 'restaurant_name']]
              .groupby('restaurant_name')
              .mean()
              .round(2)
              .sort_values('aggregate_rating', ascending = False)
              .reset_index())
    
    
    nome = df_aux.loc[0, 'restaurant_name']
    nota = df_aux.loc[0, 'aggregate_rating']

    
    return nome, nota
#==================================
#          GRÁFICOS
#==================================

#gráfico top tipos culinários
def grafico_top_culinaria(df1, top_rest, tipo, top_asc):
    '''
        
    '''
    
    df_aux = (df1.loc[:, ['aggregate_rating', 'cuisines']]
              .groupby('cuisines')
              .mean()
              .round(2)
              .sort_values('aggregate_rating', ascending = top_asc)
              .reset_index())
    

    if top_asc == 'True':

        linhas_selecionadas = df_aux['aggregate_rating'] > 0
        df_aux = df_aux.loc[linhas_selecionadas, :].reset_index()


        fig = (px.bar(df_aux, x='cuisines', y='aggregate_rating', 
                      title=f'Top {top_rest} {tipo} Tipos Culinários', 
                      color = 'cuisines',
                      text='aggregate_rating', 
                      labels={'aggregate_rating' : 'Média avaliações', 'cuisines' : 'Tipos Culinários'}))
        return fig
    else:

        fig = (px.bar(df_aux, x='cuisines', y='aggregate_rating', 
                      title=f'Top {top_rest} {tipo} Tipos Culinários', 
                      color = 'cuisines',
                      text='aggregate_rating', 
                      labels={'aggregate_rating' : 'Média avaliações', 'cuisines' : 'Tipos Culinários'}))
        return fig

    
# gráfico média por país    
def grafico_media_pais(df1, coluna):
    df_aux = (df1.loc[:, [coluna, 'country_code']]
              .groupby('country_code')
              .mean()
              .round(2)
              .sort_values(coluna, ascending = False)
              .reset_index())
    
    fig = (px.bar(df_aux, x='country_code', y=coluna, 
                  text=coluna, 
                  labels={coluna: 'Quantidade de Avaliações', 'country_code': 'Países'}, 
                  title='Média de Avaliações por País'))
    return fig
