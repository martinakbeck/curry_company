#libraries
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine


#bibliotecas necessárias
import streamlit as st
import pandas as pd
from PIL import Image
from streamlit_folium import folium_static
import folium

st.set_page_config(page_title='Visão Entregadores', layout='wide')

# ======================================
# FUNÇÕES
# ======================================

def clean_code(df1):
    """ Função tem responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da vairável númerica)
        
        Input: Dataframe
        Output: Dataframe
    
    """ 
    #Tirar linhas com Nan
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Time_taken(min)'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #Converter a coluna age para int
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    #converter a coluna ratings de texto para número decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #converter a order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    #converter multiple_deliveries de texto para numero inteiro (int)
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #Comando para remover o texto de números
    df1.loc[:, "ID"] = df1.loc[:, "ID"].str.strip()
    df1.loc[:, "Road_traffic_density"] = df1.loc[:, "Road_traffic_density"].str.strip()
    df1.loc[:, "Type_of_order"] = df1.loc[:, "Type_of_order"].str.strip()
    df1.loc[:, "Type_of_vehicle"] = df1.loc[:, "Type_of_vehicle"].str.strip()
    df1.loc[:, "City"] = df1.loc[:, "City"].str.strip()
    df1.loc[:, "Festival"] = df1.loc[:, "Festival"].str.strip()

    ## Limpandno a coluna time_taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

def top_delivers(df1, top_asc):         
                    
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
           .groupby(['City', 'Delivery_person_ID'])
           .max().sort_values(['City','Time_taken(min)'], ascending = top_asc).reset_index())
    
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    
    return df3

# ------------------------------------ Início da Estrutura lógica do código ------------------------------------ #

# ======================================
# Import Dataset
# ======================================
df = pd.read_csv("repos/train.csv")
df1 = clean_code(df)



# ======================================
### Sidebar
# ======================================
st.header('Marketplace - Visão Entregadores')

image = Image.open('img/logo1.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_opttions = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default='Low')
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

# Ligar filtro com os gráficos
#Datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_opttions)
df1 = df1.loc[linhas_selecionadas, :]

# ======================================
### Layout
# ======================================

with st.container():
    st.title('Métricas Gerais')
    col1, col2, col3, col4 = st.columns(4, gap='large')
    with col1:
        maior_idade =  df1.loc[:, 'Delivery_person_Age' ].max()
        col1.metric('Maior idade', maior_idade)

    with col2:
        menor_idade = df1.loc[:, 'Delivery_person_Age' ].min()
        col2.metric('Menor idade', menor_idade)
        
    with col3:
        veiculo_melhor = df1.loc[:, 'Vehicle_condition' ].max()
        col3.metric('Melhor condição de veículos', veiculo_melhor)
        
    with col4:
        veiculo_pior = df1.loc[:, 'Vehicle_condition' ].min()
        col4.metric('Pior condição de veículos', veiculo_pior)

    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Avaliação por entregadores')
            avaliacao_media = (df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                .groupby('Delivery_person_ID').mean().reset_index())
            st.dataframe(avaliacao_media)
            
        with col2:
            st.subheader('Avaliação por trânsito')
            avaliacao_agg_veiculo = (df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
                                        .groupby('Road_traffic_density')
                                        .agg({'Delivery_person_Ratings' : ('mean', 'std')}))
            avaliacao_agg_veiculo.columns = ['delivery_mean', 'delivery_std']
            avaliacao_agg_veiculo.reset_index()  
            
            st.dataframe(avaliacao_agg_veiculo)
            
            st.subheader('Avaliação média por clima')
            avaliacao_agg_climaticas = (df1.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']]
                                        .groupby('Weatherconditions')
                                            .agg({'Delivery_person_Ratings' : ('mean', 'std')}))
            avaliacao_agg_climaticas.columns = ['delivery_mean', 'delivery_std']
            avaliacao_agg_climaticas.reset_index()
            
            st.dataframe(avaliacao_agg_climaticas)
            
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Top entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)
            
        with col2:
            st.subheader('Top Entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
                

    
