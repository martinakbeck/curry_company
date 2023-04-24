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

st.set_page_config(page_title='Visão Empresa', layout='wide')

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


def order_metric(df1):
            
    cols = ["ID", "Order_Date"]

    #seleção de linhas
    df_aux = df1.loc[:, cols].groupby("Order_Date").count().reset_index()

    #gráfico
    fig = px.bar(df_aux, x='Order_Date', y='ID',
                 labels={'ID': 'Quantidade de pedidos', 'Order_Date':'Data'})
    return fig

def traffic_order_share(df1):
                
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
              .groupby( 'Road_traffic_density' )
              .count().reset_index())
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    # gráfico
    fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density')
               
    return fig

def traffic_order_city(df1):
                
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
              .groupby( 'Road_traffic_density' )
              .count().reset_index())
    # gráfico
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City',
                    labels={'Road_traffic_density' : 'Densidade do tráfego', 'City' : 'Cidade'})
    return fig

def order_by_week(df1):
                              
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    # gráfico
    fig = px.bar( df_aux, x='week_of_year', y='ID' )
    return fig

def order_share_week(df1):
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return fig

def country_maps(df1):
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    data_plot = (df1.loc[:, cols]
                 .groupby( ['City', 'Road_traffic_density'])
                 .median().reset_index())
    # Desenhar o mapa
    map = folium.Map( zoom_start=11 )
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    folium_static( map, width=1024 , height=600 )
    
    return map

# ------------------------------------ Início da Estrutura lógica do código ------------------------------------ #

# ======================================
# Import Dataset
# ======================================
df = pd.read_csv("repos/train.csv")
df1 = clean_code(df)


# ======================================
### Sidebar
# ======================================
st.header('Marketplace - Visão Cliente')

image = Image.open('img/logo1.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até que data?',
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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric
        st.markdown("# Pedidos por Data")
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)     
        
    with st.container():
    
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Pedidos por tipo de tráfego")
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)           

        with col2:
            st.header("Tráfego por Cidade")
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)

                
with tab2:
        with st.container():
        
            st.header('Pedido por Semana')
            fig = order_by_week(df1)
            st.plotly_chart(fig, use_container_width=True)

                
    
        with st.container():      
            st.header('Pedidos por entregador por semana')
            fig = order_share_week(df1)
            st.plotly_chart(fig, use_container_width=True)
    

                
with tab3:
    st.header('Mapa')
    country_maps(df1)
    

                                                                                                
