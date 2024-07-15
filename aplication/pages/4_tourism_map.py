import streamlit as st
import folium
from branca.element import Template, MacroElement
from streamlit_folium import st_folium
import sys
sys.path.insert(0, 'C:/Users/ANDERSON/PycharmProjects/mapa_de_calor/covid/aplication')
from suporte import funcoes_antenas
import os

#Define a configuração base da página
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

#pega os dados gerados na página principal
geo_ra = st.session_state['geo_ra']
geo_bairro = st.session_state['geo_bairro']
dfra = st.session_state['dfra']
dfbairro = st.session_state['dfbairro']
dfantenas = st.session_state['dfantenas']

#Gera o cabeçalho da página
st.subheader('Rio de Janeiro(RJ) - May/2020 to Oct/2021', divider='grey')

st.write('<style>div.block-container{padding-top:2rem;padding-bottom: 1.5rem;padding-left: 0.5rem;padding-right: 0rem;}</style>', unsafe_allow_html=True)


# Define o caminho dos arquivos de suporte do aplicativo
path = os.path.join(os.sep, 'Users', 'ANDERSON', 'PycharmProjects', 'mapa_de_calor', 'covid', 'aplicativo', 'suporte', '')


# Cria funções de apoio
def gera_geofiltro(id):
    geofiltro = []
    filtrolocal, filtrotplocal = None, 'codra'
    listaescolha = ['ANCHIETA','BANGU','BARRA DA TIJUCA','BOTAFOGO','CAMPO GRANDE','CENTRO','CIDADE DE DEUS','COMPLEXO DA MARE',
                     'COMPLEXO DO ALEMÃO','COPACABANA','GUARATIBA','ILHA DO GOVERNADOR','INHAUMA','IRAJA','JACAREPAGUA','JACAREZINHO','LAGOA',
                     'MADUREIRA','MEIER','PAQUETA','PAVUNA','PENHA','PORTUARIA','RAMOS','REALENGO','RIO COMPRIDO','ROCINHA','SANTA CRUZ',
                     'SANTA TEREZA','SAO CRISTOVAO','TIJUCA','VIGARIO GERAL','VILA ISABEL']
    listaconversao = [22,17,24,4,18,2,34,30,29,5,26,20,12,14,16,28,6,15,13,21,25,11,1,10,33,3,27,19,23,7,8,31,9]
    escolha = st.sidebar.selectbox(id + 'Região', listaescolha, placeholder="Filter Adm Region", index=None, label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        filtrolocal = listaconversao[indice]

    if filtrolocal != None:
        geofiltro = [filtrotplocal, filtrolocal]

    return geofiltro


def gera_geovisao(id, geofiltro):
    if geofiltro == []:
        listaescolha = ['Map divided by Adm Region', 'Map divided by Neighborhood']
        escolha = st.sidebar.selectbox(id, listaescolha, index=0, placeholder="Map Division", label_visibility="collapsed")
        indice = listaescolha.index(escolha)
        listaconversao = ['ra', 'bairro']
        geovis = listaconversao[indice]
    elif geofiltro[0] == 'codra' and geofiltro[1] != None:
        listaescolha = ['Map divided by Neighborhood']
        escolha = st.sidebar.selectbox(id, listaescolha, index=0, placeholder="Map Division", label_visibility="collapsed")
        indice = listaescolha.index(escolha)
        listaconversao = ['bairro']
        geovis = listaconversao[indice]
    else:
        listaescolha = ['Map divided by Adm Region', 'Map divided by Neighborhood']
        escolha = st.sidebar.selectbox(id, listaescolha, index=0, placeholder="Map Division", label_visibility="collapsed")
        indice = listaescolha.index(escolha)
        listaconversao = ['ra', 'bairro']
        geovis = listaconversao[indice]
    return geovis


def gera_agrupamento(id):
    listaescolha = ['Connections', 'Devices']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder="Data of Interest", label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['con', 'disp']
        agrupamento = listaconversao[indice]
    else:
        agrupamento = None

    return agrupamento


def gera_indicador(id):
    listaescolha = ['Rule Lift', 'Rule Confidence', 'Rule Support']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder="Measure of Interest", label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['lift', 'conf', 'sup']
        indicador = listaconversao[indice]
    else:
        indicador = None
    return indicador


def gera_mes(id):
    listaescolha = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder="Month", label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = [1,2,3,4,5,6,7,8,9,10,11,12]
        mes = listaconversao[indice]
    else:
        mes = None

    return mes


def gera_diasem(id):
    listaescolha = ['Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder='Day of the week', label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sab']
        diasem = listaconversao[indice]
    else:
        diasem = None
    return diasem


def gera_reg_alvo(id):
    listaescolha = ['United States','France','Italy','United Kingdom','Netherlands','Portugal','Argentina','Chile','Norway','China']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder='Country', label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['USA','France','Italy','Unit_Kingd','Netherlands','Portugal','Argentina','Chile','Norway','China']
        pais = listaconversao[indice]
        alvo = ['pais', pais]
    else:
        alvo = []

    return alvo


def gera_reg_ant(ano, mes, diasem):
    reg_ant = []
    if ano != None:
        reg_ant.append(['ano', ano])
    if mes != None:
        reg_ant.append(['mes', mes])
    if diasem != None:
        reg_ant.append(['diasem', diasem])

    return reg_ant


@st.cache_data
def geo_coordenadas(geovis):
    if geovis == 'ra':
        base = geo_ra
    else:
        base = geo_bairro
    return base

@st.cache_data
def gera_grafico(df, indicador, geovis):
    import altair as alt

    # Ajuste da variável de geovisão
    codgeovis = "cod" + geovis

    # Ajuste de dfgeovis para visualização
    df = df.loc[(df['localidade'] != '-')]
    df = df.sort_values([indicador, 'qtd_alvo'], ascending=[False, False])
    df = df[[codgeovis, 'localidade', indicador, 'clasvis']]
    df = df.reset_index(drop=True)

    # Create the bar chart with mean line using Altair
    bar = alt.Chart(df).mark_bar().encode(
        x=alt.X('localidade:N', title=geovis.upper(), sort='-y'),
        y=alt.Y(f'{indicador}:Q', title=indicador.upper()),
        color=alt.Color(f'{indicador}:Q', legend=None)
    )

    #personalisa a referência da linha mediana
    if indicador == 'lift':
        df['ref'] = 1
        ref = f'mean(ref):Q'
    elif indicador == 'conf':
        df['ref'] = 20
        ref = f'mean(ref):Q'
    else:
        ref = f'mean({indicador}):Q'

    mean_line = alt.Chart(df).mark_rule(color='red').encode(
        y=ref,
        size=alt.value(2)
    )

    chart = (bar + mean_line).properties(width=610, height=450)

    # Exibindo o gráfico na segunda coluna
    st.write("Graphic:")
    st.altair_chart(chart, theme=None, use_container_width=True)

    # Exibindo o DataFrame na primeira coluna
    st.write("Table:")
    st.dataframe(df, use_container_width=True)

@st.cache_data
def gera_regras(antenas, agp, geovis, reg_ant, reg_alvo, indicador, geofiltro, faixa_sup, conf_base, indicador_base):
    df,faixa_sup,conf_base = funcoes_antenas.gera_regras(antenas, agp, geovis, reg_ant, reg_alvo, indicador, geofiltro, faixa_sup, conf_base, indicador_base)

    return df, faixa_sup, conf_base


def gera_mapa(antenas, agp, geovis, reg_ant, reg_alvo, indicador, geofiltro, faixa_sup, conf_base, indicador_base):
    # Leitura das coordenadas geográficas, base do mapa
    base = geo_coordenadas(geovis)

    dfregras, faixa_sup, conf_base = gera_regras(antenas, agp, geovis, reg_ant, reg_alvo, indicador, geofiltro, faixa_sup, conf_base, indicador_base)

    mapa,txtrg,dfgeovis = funcoes_antenas.configura_mapa(dfregras, antenas, agp, geovis, reg_ant, reg_alvo, indicador, geofiltro, base)

    return mapa,txtrg,dfgeovis,faixa_sup,conf_base


# Gera lista de anos disponíveis
lista_anos = [2020, 2021]

# Widgets de controle para cada coluna
exibir_coluna1 = st.sidebar.checkbox("Map1")
if exibir_coluna1:
    st.sidebar.markdown(":blue[**General Parameters**]")
    geofiltro1 = gera_geofiltro('1.1')
    geovis1 = gera_geovisao('1.2', geofiltro1)
    agp1 = gera_agrupamento('1.3')
    indicador1 = gera_indicador('1.4')
    st.sidebar.markdown(":blue[**Antecedent  Attributes**]")
    ano1 = st.sidebar.selectbox('1.5', lista_anos, index=None, placeholder="Year", label_visibility="collapsed")
    mes1 = gera_mes('1.6')
    diasem1 = gera_diasem('1.7')
    reg_ant1 = gera_reg_ant(ano1,mes1,diasem1)
    st.sidebar.markdown(":blue[**Consequent Attributes**]")
    reg_alvo1 = [gera_reg_alvo('1.8')]

st.sidebar.divider()

exibir_coluna2 = st.sidebar.checkbox("Map2")
if exibir_coluna2:
    st.sidebar.markdown(":blue[**General Parameters**]")
    geofiltro2 = gera_geofiltro('2.1')
    geovis2 = gera_geovisao('2.2', geofiltro2)
    agp2 = gera_agrupamento('2.3')
    indicador2 = gera_indicador('2.4')
    st.sidebar.markdown(":blue[**Antecedent  Attributes**]")
    ano2 = st.sidebar.selectbox('2.5', lista_anos, index=None, placeholder="Year", label_visibility="collapsed")
    mes2 = gera_mes('2.6')
    diasem2 = gera_diasem('2.7')
    reg_ant2 = gera_reg_ant(ano2, mes2, diasem2)
    st.sidebar.markdown(":blue[**Consequent Attributes**]")
    reg_alvo2 = [gera_reg_alvo('2.8')]


# Função para exibir ou ocultar cada coluna dinamicamente
if exibir_coluna1 and not exibir_coluna2:
    placeholder = st.empty()
    # Se apenas a Coluna 1 for exibida, ocupará toda a tela
    col1, _ = st.columns((1000, 1))  # Define proporção para 999/1000 e 1/1000
    with col1:
        if reg_alvo1 != [[]] and indicador1 != None and agp1 != None:

            # Gera o mapa com os dados dos parâmetros passados
            antenas = dfbairro if geovis1 == 'bairro' else dfra
            faixa_sup, conf_base, indicador_base = 0,0,''
            mapa1, txtrg1, dfgeovis1, faixa_sup1, conf_base1 = gera_mapa(antenas,agp1,geovis1,reg_ant1,reg_alvo1,indicador1,geofiltro1,faixa_sup,conf_base, indicador_base)

            #st.write(faixa_sup, faixa_sup1)

            st.markdown(f'**<span style="font-size:18px;">Regra: {txtrg1}</span>**', unsafe_allow_html=True)

            st_folium(mapa1, width=1200, height=550)  # Exibe o primeiro mapa usando folium_static

            if len(dfgeovis1) > 0:
                gera_grafico(dfgeovis1, indicador1, geovis1)
elif exibir_coluna2 and not exibir_coluna1:
    placeholder = st.empty()
    # Se apenas a Coluna 2 for exibida, ocupará toda a tela
    col2, _ = st.columns((1000, 1))  # Define proporção para 999/1000 e 1/1000
    with col2:

        if reg_alvo2 != [[]] and indicador2 != None and agp2 != None:

            # Gera o mapa com os dados dos parâmetros passados
            antenas = dfbairro if geovis2 == 'bairro' else dfra
            faixa_sup, conf_base, indicador_base = 0,0,''
            mapa2, txtrg2, dfgeovis2, faixa_sup2, conf_base2 = gera_mapa(antenas, agp2, geovis2, reg_ant2, reg_alvo2, indicador2, geofiltro2, faixa_sup, conf_base, indicador_base)

            st.markdown(f'**<span style="font-size:18px;">Regra: {txtrg2}</span>**', unsafe_allow_html=True)
            st_folium(mapa2, width=1200, height=550)   # Exibe o segundo mapa usando folium_static

            if len(dfgeovis2) > 0:
                gera_grafico(dfgeovis2, indicador2, geovis2)
elif exibir_coluna2 and exibir_coluna1:
    # Criando as colunas
    col1, col2 = st.columns(2)
    mapa2 = ''
    with col1:

        if reg_alvo1 != [[]] and indicador1 != None and agp1 != None:

            # Gera o mapa com os dados dos parâmetros passados
            antenas = dfbairro if geovis1 == 'bairro' else dfra
            faixa_sup, conf_base, indicador_base = 0,0,''
            mapa1, txtrg1, dfgeovis1, faixa_sup1, conf_base1 = gera_mapa(antenas, agp1, geovis1, reg_ant1, reg_alvo1, indicador1, geofiltro1, faixa_sup, conf_base, indicador_base)

            st.markdown(f'**<span style="font-size:18px;">Regra: {txtrg1}</span>**', unsafe_allow_html=True)
            mapa1 = st_folium(mapa1, width=610, height=550)  # Exibe o primeiro mapa usando folium_static

            filtro_mapa2 = ''
            if mapa1['last_active_drawing']:
                filtro_mapa2 = mapa1['last_active_drawing']['properties']['cod'+geovis1]
                exibir_coluna2 = True

            if filtro_mapa2 != '' and geovis1 in ['ra']:
                geofiltro2 = ['cod'+geovis1, filtro_mapa2]
                if geovis1 == 'ra' and geovis2 not in ['bairro']:
                    geovis = 'bairro'
                else:
                    geovis = geovis2
                agp2 = agp1
                indicador2 = indicador1
                ano2 = ano1
                mes2 = mes1
                diasem2 = diasem1
                reg_ant2 = reg_ant1
                reg_alvo2 = reg_alvo1

                if reg_alvo2 != [[]] and indicador2 != None and agp2 != None:

                    # Gera o mapa com os dados dos parâmetros passados
                    antenas = dfbairro if geovis == 'bairro' else dfra
                    indicador_base = indicador1
                    mapa2, txtrg2, dfgeovis2, faixa_sup2, conf_base2 = gera_mapa(antenas, agp2, geovis, reg_ant2, reg_alvo2, indicador2, geofiltro2, faixa_sup1, conf_base1, indicador_base)

            else:
                if reg_alvo2 != [[]] and indicador2 != None and agp2 != None:

                    # Gera o mapa com os dados dos parâmetros passados
                    antenas = dfbairro if geovis2 == 'bairro' else dfra
                    indicador_base = indicador1
                    mapa2, txtrg2, dfgeovis2, faixa_sup2, conf_base2 = gera_mapa(antenas, agp2, geovis2, reg_ant2, reg_alvo2, indicador2, geofiltro2, faixa_sup1, conf_base1, indicador_base)

            if len(dfgeovis1) > 0:
                gera_grafico(dfgeovis1, indicador1, geovis1)

        else:
            if reg_alvo2 != [[]] and indicador2 != None and agp2 != None:

                # Gera o mapa com os dados dos parâmetros passados
                antenas = dfbairro if geovis2 == 'bairro' else dfra
                faixa_sup, conf_base, indicador_base = 0,0,''
                mapa2, txtrg2, dfgeovis2, faixa_sup2, conf_base2 = gera_mapa(antenas, agp2, geovis2, reg_ant2, reg_alvo2, indicador2, geofiltro2, faixa_sup, conf_base, indicador_base)


    with col2:
        if mapa2 != '':
            st.markdown(f'**<span style="font-size:18px;">Regra: {txtrg2}</span>**', unsafe_allow_html=True)
            st_folium(mapa2, width=610, height=550)  # Exibe o segundo mapa usando folium_static

            if len(dfgeovis2) > 0:
                gera_grafico(dfgeovis2, indicador2, geovis2)
    #filtro_mapa2 = ''

else:
    placeholder = st.empty()




