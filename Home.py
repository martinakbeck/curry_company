import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon=":)",
)


image_path = 'img/logo1.png'
image = Image.open(image_path)

# ======================================
### Sidebar
# ======================================
st.header('Marketplace - Visão Restaurantes')

image = Image.open('img/logo1.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Curry Company Dashboard")

st.markdown(
    """
    O Dashboard é uma ferramenta para acompanhar as métricas de crescimento de entregadores e restaurantes. Aqui estão algumas dicas sobre como utilizá-lo efetivamente:

    * Visão Empresa:
        * Visão Gerencial: aqui você pode ver as métricas gerais de desempenho do seu negócio. Utilize esta visão para ter uma visão ampla do desempenho do seu negócio ao longo do tempo.
        * Visão Tática: nesta seção, você pode ver indicadores semanais de crescimento. Use isso para identificar tendências de curto prazo e ajustar suas estratégias de crescimento.
        * Visão Geográfica: você pode ver a geolocalização de onde a demanda é mais forte para identificar oportunidades de expansão.
    * Visão Entregador: conseguimos acompanhar o número de entregas realizadas, a satisfação do cliente. Isso pode ajudar a identificar áreas onde podem melhorar e aumentar a eficiência.
    * Visão Restaurante: podemos acompanhar os indicadores, como o número de pedidos recebidos, o tempo médio de entrega e a satisfação do cliente. 
        
        
    @martinakbeck    
""")

