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
import numpy as np

st.set_page_config(page_title='Visão Restaurantes', layout='wide')

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

def distance(df1, fig):
    if fig == False:
        
                
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude','Restaurant_latitude', 'Restaurant_longitude']

        df1['distance'] = (df1.loc[:, cols].apply( lambda x: 
                                                  haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                             (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))

        distancia_media = np.round(df1.loc[:, 'distance'].mean(), 2)

        return distancia_media
    else:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude','Restaurant_latitude', 'Restaurant_longitude']

        df1['distance'] = (df1.loc[:, cols].apply( lambda x:
                                                  haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
            
        distancia_media = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=distancia_media['City'], values=distancia_media['distance'], pull=[0, 0.1, 0])])
        return fig

def media_desvio_tempo_entrega(df1, festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                -df: Dataframe com os dados necessários para o cálculo
                -op: Tipo de operação que precisa ser calculado
                    'media_time': Calcula o tempo médio
                    'desvio_time': Calcula o desvio padrão
            Output:
                - df: Dataframe com 2 colunas e 1 linha

    """

    df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
              .groupby('Festival')
              .agg({'Time_taken(min)' : ['mean', 'std']}))
    df_aux.columns = ['media_time', 'desvio_time']
    df_aux = df_aux.reset_index()

    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)
    return df_aux


def media_desvio_tempo_grafico(df1):

    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean', 'std']})
    df_aux.columns=['tempo_media', 'tempo_desvio']

    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                         x=df_aux['City'],
                         y=df_aux['tempo_media'],
                         error_y=dict(type='data', array=df_aux['tempo_desvio'])))
    fig.update_layout(barmode='group')
    return fig


def media_desvio_tempo_tráfego(df1):

    df_aux = (df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
              .groupby(['City', 'Road_traffic_density'])
              .agg({'Time_taken(min)' : ['mean', 'std']}))

    df_aux.columns=['tempo_media', 'tempo_desvio']

    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='tempo_media',
                      color='tempo_desvio', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['tempo_desvio']))
    return fig

# ------------------------------------ Início da Estrutura lógica do código ------------------------------------ #

# ======================================
# Import Dataset
# ======================================
df = pd.read_csv("repos/train.csv")
df1 = clean_code(df)


# ======================================
### Sidebar
# ======================================
st.header('Marketplace - Visão Restaurantes')

image = Image.open('logo.png')
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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.title('Métricas Gerais')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            entregadores_unicos = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', entregadores_unicos)
            
        with col2:
            distancia_media = distance(df1, fig=False)
            col2.metric('Distância média das entregas', distancia_media)
    
        with col3:
            df_aux = media_desvio_tempo_entrega(df1, 'Yes', 'media_time')
            col3.metric('Tempo Médio de Entrega com Festival', df_aux)
            
        with col4:
            df_aux = media_desvio_tempo_entrega(df1, 'Yes', 'desvio_time')
            col4.metric('Desvio Padrão de Entrega com Festival', df_aux)
            
        with col5:
            df_aux = media_desvio_tempo_entrega(df1, 'No', 'media_time')
            col5.metric('Tempo Médio de Entrega sem Festival', df_aux)
            
        with col6:
            df_aux = media_desvio_tempo_entrega(df1, 'No', 'desvio_time')
            col6.metric('Desvio Padrão de Entrega sem Festival', df_aux)
            
            
    with st.container():
        st.markdown("""---""")
        st.title('Tempo médio de entrega por cidade')
        fig = distance(df1, fig=True)
        st.plotly_chart(fig)
        
        
        
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do Tempo')       
        
        col1, col2 = st.columns(2)
        
        with col1:          
            fig = media_desvio_tempo_grafico(df1)
            st.plotly_chart(fig)
            
        with col2:            
            fig = media_desvio_tempo_tráfego(df1)
            st.plotly_chart(fig)
            
                      
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição da distância')
        
        df_aux = (df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                  .groupby(['City', 'Type_of_order'])
                  .agg({'Time_taken(min)': ['mean', 'std']}))
        
        df_aux.columns=['distancia_media', 'distancia_desvio']
        
        df_aux = df_aux.reset_index()
        
        st.dataframe(df_aux)
               
        
        
        
