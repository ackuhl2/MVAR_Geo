import streamlit as st
import folium
from branca.element import Template, MacroElement
from streamlit_folium import st_folium
import sys
sys.path.insert(0, 'C:/Users/ANDERSON/PycharmProjects/mapa_de_calor/covid/aplication')
from suporte import funcoes_eleicoes
import os

#Define a configuração base da página
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

#pega os dados gerados na página principal
eleicoes = st.session_state['eleicoes']
geo_uf = st.session_state['geo_uf']
geo_meso = st.session_state['geo_meso']
geo_micro = st.session_state['geo_micro']
geo_regiao = st.session_state['geo_regiao']
geo_mun = st.session_state['geo_mun']


#Gera o cabeçalho da página
st.subheader('Presidential Elections - 2018 and 2022 - 2nd Round', divider='grey')

st.write('<style>div.block-container{padding-top:2rem;padding-bottom: 1.5rem;padding-left: 0.5rem;padding-right: 0rem;}</style>', unsafe_allow_html=True)

# Define o caminho dos arquivos de suporte do aplicativo
path = os.path.join(os.sep, 'Users', 'ANDERSON', 'PycharmProjects', 'mapa_de_calor', 'covid', 'aplicativo', 'suporte', '')

# Cria funções de apoio
def gera_geofiltro(id):
    geofiltro = []
    listaescolha = ['Filter by Region', 'Filter by State']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder="Filter by Region/State", label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['regiao', 'uf']
        filtrotplocal = listaconversao[indice]
        if filtrotplocal == 'regiao':
            filtrolocal = st.sidebar.selectbox(id + 'Region', ['CO', 'N', 'NE', 'S', 'SE'], placeholder="Choose a Region", index=None, label_visibility="collapsed")
        elif filtrotplocal == 'uf':
            filtrolocal = st.sidebar.selectbox(id + 'State', ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO', ], index=None, placeholder="Escolha uma UF", label_visibility="collapsed")
        else:
            filtrolocal = None

        if filtrolocal != None:
            geofiltro = [filtrotplocal, filtrolocal]

    return geofiltro


def gera_geovisao(id, geofiltro):
    if geofiltro == []:
        listaescolha = ['Division by Region', 'Division by State', 'Division by Mesoregion', 'Division by Microregion', 'Division by City']
        escolha = st.sidebar.selectbox(id, listaescolha, index=1, placeholder="Divisão do Mapa", label_visibility="collapsed")
        indice = listaescolha.index(escolha)
        listaconversao = ['regiao', 'uf', 'mesoregiao', 'microregiao', 'municipio']
        geovis = listaconversao[indice]
    elif geofiltro[0] == 'regiao' and geofiltro[1] != None:
        listaescolha = ['Division by State', 'Division by Mesoregion', 'Division by Microregion', 'Division by City']
        escolha = st.sidebar.selectbox(id, listaescolha, index=0, placeholder="Divisão do Mapa", label_visibility="collapsed")
        indice = listaescolha.index(escolha)
        listaconversao = ['uf', 'mesoregiao', 'microregiao', 'municipio']
        geovis = listaconversao[indice]
    elif geofiltro[0] == 'uf' and geofiltro[1] != None:
        listaescolha = ['Division by Mesoregion', 'Division by Microregion', 'Division by City']
        escolha = st.sidebar.selectbox(id, listaescolha, index=0, placeholder="Divisão do Mapa", label_visibility="collapsed")
        indice = listaescolha.index(escolha)
        listaconversao = ['mesoregiao', 'microregiao', 'municipio']
        geovis = listaconversao[indice]
    else:
        listaescolha = ['Division by Region', 'Division by State', 'Division by Mesoregion', 'Division by Microregion', 'Division by City']
        escolha = st.sidebar.selectbox(id, listaescolha, index=1, placeholder="Divisão do Mapa", label_visibility="collapsed")
        indice = listaescolha.index(escolha)
        listaconversao = ['regiao', 'uf', 'mesoregiao', 'microregiao', 'municipio']
        geovis = listaconversao[indice]
    return geovis


def gera_indicador(id):
    listaescolha = ['Rule Lift', 'Rule Confidence', 'Rule Support']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder="Medida de Interesse", label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['lift', 'conf', 'sup']
        indicador = listaconversao[indice]
    else:
        indicador = None
    return indicador


def gera_densidade(id):
    listaescolha = ['Dens. VERY LOW', 'Dens. LOW', 'Dens. MEDIA', 'Dens. HIGH', 'Dens. VERY HIGH']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder="Dens. Demo. Mun.", label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['MUITO BAIXA', 'BAIXA', 'MEDIA', 'ALTA', 'MUITO ALTA']
        densidade = listaconversao[indice]
    else:
        densidade = None
    return densidade


def gera_idh(id):
    listaescolha = ['VERY LOW HDI', 'LOW HDI', 'MEDIUM HDI', 'HIGH HDI', 'VERY HIGH HDI']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder='IDH Municipal', label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['MUITO BAIXA', 'BAIXA', 'MEDIA', 'ALTA', 'MUITO ALTA']
        idh = listaconversao[indice]
    else:
        idh = None
    return idh


def gera_reg_alvo(id):
    listaescolha = ['Left','Right','Draw']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder='Winner of the Ballot Box', label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['ESQUERDA','DIREITA','EMPATE']
        vencedor = listaconversao[indice]
        alvo = ['vencedor', vencedor]
    else:
        alvo = []

    return alvo


def gera_reg_ant(eleicao, idh):
    reg_ant = []
    if eleicao != None:
        reg_ant.append(['eleicao', eleicao])
    if idh != None:
        reg_ant.append(['escala_idh', idh])
    return reg_ant


@st.cache_data
def geo_coordenadas(geovis):
    if geovis == 'regiao':
        base = geo_regiao
    elif geovis == 'uf':
        base = geo_uf
    elif geovis == 'mesoregiao':
        base = geo_meso
    elif geovis == 'microregiao':
        base = geo_micro
    else:
        base = geo_mun
    return base

@st.cache_data
def gera_grafico(df, indicador, geovis):
    import altair as alt

    # Ajuste da variável de geovisão
    if geovis in ['regiao', 'uf']:
        codgeovis = geovis
    elif geovis == 'municipio':
        codgeovis = 'codmun'
    else:
        codgeovis = "cod" + geovis[:-6]

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
        df['ref'] = 50
        ref = f'mean(ref):Q'
    else:
        ref = f'mean({indicador}):Q'

    mean_line = alt.Chart(df).mark_rule(color='red').encode(
        y=ref,
        size=alt.value(2)
    )

    chart = (bar + mean_line).properties(width=610, height=450)

    # Exibindo o gráfico na segunda coluna
    st.write("Graph:")
    st.altair_chart(chart, theme=None, use_container_width=True)

    # Exibindo o DataFrame na primeira coluna
    st.write("Table:")
    st.dataframe(df, use_container_width=True)


@st.cache_data
def gera_regras(eleicoes, geovis, reg_ant, reg_alvo, indicador, geofiltro, faixa_sup, conf_base, indicador_base):

    df,faixa_sup, conf_base = funcoes_eleicoes.gera_regras(eleicoes, geovis, reg_ant, reg_alvo, indicador, geofiltro, faixa_sup, conf_base, indicador_base)

    return df, faixa_sup, conf_base


def gera_mapa(eleicoes, eleicao, geovis, reg_ant, reg_alvo, indicador, geofiltro, faixa_sup, conf_base, indicador_base):
    # Leitura das coordenadas geográficas, base do mapa
    base = geo_coordenadas(geovis)

    #Gera dataframe base para o mapa
    dfregras, faixa_sup, conf_base = gera_regras(eleicoes, geovis, reg_ant, reg_alvo, indicador, geofiltro, faixa_sup, conf_base, indicador_base)

    mapa,txtrg,dfgeovis = funcoes_eleicoes.configura_mapa(dfregras, geovis, reg_ant, reg_alvo, indicador, geofiltro, base, eleicao)

    return mapa,txtrg,dfgeovis,faixa_sup,conf_base

# Gera lista de anos disponíveis
lista_anos = [2018, 2022]

# Widgets de controle para cada coluna
exibir_coluna1 = st.sidebar.checkbox("Map1")
if exibir_coluna1:
    st.sidebar.markdown(":blue[**General Parameters**]")
    geofiltro1 = gera_geofiltro('1.1')
    geovis1 = gera_geovisao('1.2', geofiltro1)
    indicador1 = gera_indicador('1.3')
    st.sidebar.markdown(":blue[**Antecedent Attributes**]")
    eleicao1 = st.sidebar.selectbox('1.4', lista_anos, index=None, placeholder="Election", label_visibility="collapsed")
    #densid1 = gera_densidade('1.5')
    idh1 = gera_idh('1.6')
    reg_ant1 = gera_reg_ant(eleicao1, idh1)
    st.sidebar.markdown(":blue[**Consequent Attributes**]")
    reg_alvo1 = [gera_reg_alvo('1.7')]


st.sidebar.divider()


exibir_coluna2 = st.sidebar.checkbox("Map2")

if exibir_coluna2:
    st.sidebar.markdown(":blue[**General Parameters**]")
    geofiltro2 = gera_geofiltro('2.1')
    geovis2 = gera_geovisao('2.2', geofiltro2)
    indicador2 = gera_indicador('2.3')
    st.sidebar.markdown(":blue[**Antecedent Attributes**]")
    eleicao2 = st.sidebar.selectbox('2.4', lista_anos, index=None, placeholder="Election", label_visibility="collapsed")
    #densid2 = gera_densidade('2.5')
    idh2 = gera_idh('2.6')
    reg_ant2 = gera_reg_ant(eleicao2, idh2)
    st.sidebar.markdown(":blue[**Consequent Attributes**]")
    reg_alvo2 = [gera_reg_alvo('2.7')]


# Função para exibir ou ocultar cada coluna dinamicamente
if exibir_coluna1 and not exibir_coluna2:   
    placeholder = st.empty()
    # Se apenas a Coluna 1 for exibida, ocupará toda a tela
    col1, _ = st.columns((1000, 1))  # Define proporção para 999/1000 e 1/1000
    with col1:

        if reg_alvo1 != [[]] and indicador1 != None:

            # Gera o mapa com os dados dos parâmetros passados
            faixa_sup, conf_base, indicador_base = 0,0,''
            mapa1, txtrg1, dfgeovis1, faixa_sup1, conf_base1 = gera_mapa(eleicoes, eleicao1, geovis1, reg_ant1, reg_alvo1, indicador1, geofiltro1, faixa_sup, conf_base, indicador_base)

            st.markdown(f'**<span style="font-size:16px;">Regra: {txtrg1}</span>**', unsafe_allow_html=True)
            st_folium(mapa1, width=1200, height=550)  # Exibe o primeiro mapa usando folium_static

            if len(dfgeovis1) > 0:
                gera_grafico(dfgeovis1, indicador1, geovis1)

elif exibir_coluna2 and not exibir_coluna1:
    placeholder = st.empty()
    # Se apenas a Coluna 2 for exibida, ocupará toda a tela
    col2, _ = st.columns((1000, 1))  # Define proporção para 999/1000 e 1/1000
    with col2:

        if reg_alvo2 != [[]] and indicador2 != None:

            # Gera o mapa com os dados dos parâmetros passados
            faixa_sup, conf_base, indicador_base = 0,0,''
            mapa2, txtrg2, dfgeovis2, faixa_sup2, conf_base2 = gera_mapa(eleicoes, eleicao2, geovis2, reg_ant2, reg_alvo2, indicador2, geofiltro2, faixa_sup, conf_base, indicador_base)

            st.markdown(f'**<span style="font-size:16px;">Regra: {txtrg2}</span>**', unsafe_allow_html=True)
            st_folium(mapa2, width=1200, height=550)   # Exibe o segundo mapa usando folium_static

            if len(dfgeovis2) > 0:
                gera_grafico(dfgeovis2, indicador2, geovis2)

elif exibir_coluna2 and exibir_coluna1:
    # Criando as colunas
    col1, col2 = st.columns(2)
    mapa2 = ''
    with col1:

        if reg_alvo1 != [[]] and indicador1 != None:

            # Gera o mapa com os dados dos parâmetros passados
            faixa_sup, conf_base, indicador_base = 0,0,''
            mapa1, txtrg1, dfgeovis1, faixa_sup1, conf_base1 = gera_mapa(eleicoes, eleicao1, geovis1, reg_ant1, reg_alvo1, indicador1, geofiltro1, faixa_sup, conf_base, indicador_base)

            st.markdown(f'**<span style="font-size:16px;">Regra: {txtrg1}</span>**', unsafe_allow_html=True)
            mapa1 = st_folium(mapa1, width=610, height=550)  # Exibe o primeiro mapa usando folium_static

            filtro_mapa2 = ''
            if mapa1['last_active_drawing']:
                filtro_mapa2 = mapa1['last_active_drawing']['properties'][geovis1]
                exibir_coluna2 = True

            if filtro_mapa2 != '' and geovis1 in ['regiao', 'uf']:
                geofiltro2 = [geovis1, filtro_mapa2]
                if geovis1 == 'regiao' and geovis2 not in ['mesoregiao', 'uf', 'microregiao', 'municipio']:
                    geovis = 'uf'
                elif geovis1 == 'uf' and geovis2 not in ['mesoregiao', 'microregiao', 'municipio']:
                    geovis = 'mesoregiao'
                else:
                    geovis = geovis2
                indicador2 = indicador1
                eleicao2 = eleicao1
                #densid2 = densid1
                idh2 = idh1
                reg_ant2 = reg_ant1
                reg_alvo2 = reg_alvo1

                if reg_alvo2 != [[]] and indicador2 != None:

                    # Gera o mapa com os dados dos parâmetros passados
                    indicador_base = indicador1
                    mapa2, txtrg2, dfgeovis2, faixa_sup2, conf_base2 = gera_mapa(eleicoes, eleicao2, geovis, reg_ant2, reg_alvo2, indicador2, geofiltro2, faixa_sup1, conf_base1, indicador_base)

            else:
                if reg_alvo2 != [[]] and indicador2 != None:

                    # Gera o mapa com os dados dos parâmetros passados
                    indicador_base = indicador1
                    mapa2, txtrg2, dfgeovis2, faixa_sup2, conf_base2 = gera_mapa(eleicoes, eleicao2, geovis2, reg_ant2, reg_alvo2, indicador2, geofiltro2, faixa_sup1, conf_base1, indicador_base)

            if len(dfgeovis1) > 0:
                gera_grafico(dfgeovis1, indicador1, geovis1)

        else:
            if reg_alvo2 != [[]] and indicador2 != None:

                # Gera o mapa com os dados dos parâmetros passados
                faixa_sup, conf_base, indicador_base = 0,0,''
                mapa2, txtrg2, dfgeovis2, faixa_sup2, conf_base2 = gera_mapa(eleicoes, eleicao2, geovis2, reg_ant2, reg_alvo2, indicador2, geofiltro2, faixa_sup, conf_base, indicador_base)

    with col2:
        if mapa2 != '':
            st.markdown(f'**<span style="font-size:16px;">Regra: {txtrg2}</span>**', unsafe_allow_html=True)
            st_folium(mapa2, width=610, height=550)  # Exibe o segundo mapa usando folium_static

            if len(dfgeovis2) > 0:
                gera_grafico(dfgeovis2, indicador2, geovis2)
    #filtro_mapa2 = ''

else:
    placeholder = st.empty()




