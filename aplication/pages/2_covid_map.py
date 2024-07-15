import streamlit as st
import folium
from branca.element import Template, MacroElement
from streamlit_folium import st_folium
import os
import sys
sys.path.insert(0, 'C:/Users/ANDERSON/PycharmProjects/mapa_de_calor/covid/aplication')
from suporte import funcoes_mapa

#Define a configuração base da página
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

#pega os dados gerados na página principal
covid = st.session_state['covid']
precovid = st.session_state['precovid']
faixas = st.session_state['faixas']
#filtroBase = st.session_state['filtroBase']
geo_uf = st.session_state['geo_uf']
geo_meso = st.session_state['geo_meso']
geo_micro = st.session_state['geo_micro']
geo_regiao = st.session_state['geo_regiao']
#txtbase = st.session_state['txtbase']

st.write('<style>div.block-container{padding-top:2rem;padding-bottom: 1.5rem;padding-left: 0.5rem;padding-right: 0rem;}</style>', unsafe_allow_html=True)

# Define o caminho dos arquivos de suporte do aplicativo
path = os.path.join(os.sep, 'Users', 'ANDERSON', 'PycharmProjects', 'mapa_de_calor', 'covid', 'aplicativo', 'suporte', '')


# Cria funções de apoio
def gera_geofiltro(id):
    geofiltro = []
    listaescolha = ['Filtro por Região', 'Filtro por UF']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder="Filtrar Região/UF", label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['regiao', 'uf']
        filtrotplocal = listaconversao[indice]
        if filtrotplocal == 'regiao':
            filtrolocal = st.sidebar.selectbox(id + 'Região', ['CO', 'N', 'NE', 'S', 'SE'], placeholder="Escolha uma Região", index=None, label_visibility="collapsed")
        elif filtrotplocal == 'uf':
            filtrolocal = st.sidebar.selectbox(id + 'UF', ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO', ], index=None, placeholder="Escolha uma UF", label_visibility="collapsed")
        else:
            filtrolocal = None

        if filtrolocal != None:
            geofiltro = [filtrotplocal, filtrolocal]

    return geofiltro


def gera_geovisao(id, geofiltro):
    if geofiltro == []:
        listaescolha = ['Divisão por Região', 'Divisão por UF', 'Divisão por Mesoregião', 'Divisão por Microregião']
        escolha = st.sidebar.selectbox(id, listaescolha, index=1, placeholder="Divisão do Mapa", label_visibility="collapsed")
        indice = listaescolha.index(escolha)
        listaconversao = ['regiao', 'uf', 'mesoregiao', 'microregiao']
        geovis = listaconversao[indice]
    elif geofiltro[0] == 'regiao' and geofiltro[1] != None:
        listaescolha = ['Divisão por UF', 'Divisão por Mesoregião', 'Divisão por Microregião']
        escolha = st.sidebar.selectbox(id, listaescolha, index=0, placeholder="Divisão do Mapa", label_visibility="collapsed")
        indice = listaescolha.index(escolha)
        listaconversao = ['uf', 'mesoregiao', 'microregiao']
        geovis = listaconversao[indice]
    elif geofiltro[0] == 'uf' and geofiltro[1] != None:
        listaescolha = ['Divisão por Mesoregião', 'Divisão por Microregião']
        escolha = st.sidebar.selectbox(id, listaescolha, index=0, placeholder="Divisão do Mapa", label_visibility="collapsed")
        indice = listaescolha.index(escolha)
        listaconversao = ['mesoregiao', 'microregiao']
        geovis = listaconversao[indice]
    else:
        listaescolha = ['Divisão por Região', 'Divisão por UF', 'Divisão por Mesoregião', 'Divisão por Microregião']
        escolha = st.sidebar.selectbox(id, listaescolha, index=1, placeholder="Divisão do Mapa", label_visibility="collapsed")
        indice = listaescolha.index(escolha)
        listaconversao = ['regiao', 'uf', 'mesoregiao', 'microregiao']
        geovis = listaconversao[indice]
    return geovis


def gera_indicador(id):
    listaescolha = ['Lift da Regra', 'Confiança da Regra', 'Suporte da Regra']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder="Medida de Interesse", label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['lift', 'conf', 'sup']
        indicador = listaconversao[indice]
    else:
        indicador = None
    return indicador


def gera_densidade(id):
    listaescolha = ['Dens. MUITO BAIXA', 'Dens. BAIXA', 'Dens. MEDIA', 'Dens. ALTA', 'Dens. MUITO ALTA']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder="Dens. Demo. Mun.", label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['MUITO BAIXA', 'BAIXA', 'MEDIA', 'ALTA', 'MUITO ALTA']
        densidade = listaconversao[indice]
    else:
        densidade = None
    return densidade


def gera_idh(id):
    listaescolha = ['IDH MUITO BAIXO', 'IDH BAIXO', ' IDH MEDIO', 'IDH ALTO', 'IDH MUITO ALTO']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder='IDH Municipal', label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['MUITO BAIXA', 'BAIXA', 'MEDIA', 'ALTA', 'MUITO ALTA']
        idh = listaconversao[indice]
    else:
        idh = None
    return idh


def gera_reg_alvo(id, id2):
    listaescolha = ['taxa de óbitos/casos', 'taxa de óbitos/pop', 'taxa de casos/pop']
    escolha = st.sidebar.selectbox(id, listaescolha, index=None, placeholder='Métrica', label_visibility="collapsed")
    if escolha != None:
        indice = listaescolha.index(escolha)
        listaconversao = ['txobcasos', 'txobpop', 'txcasospop']
        metrica = listaconversao[indice]
        escala = st.sidebar.selectbox(id2, ['MUITO BAIXA', 'BAIXA', 'MEDIA', 'ALTA', 'MUITO ALTA'], index=4, placeholder='Escala', label_visibility="collapsed")
        alvo = [metrica, escala]
    else:
        alvo = []

    return alvo


def gera_reg_ant(ano, densid, idh):
    reg_ant = []
    if ano != None:
        reg_ant.append(['ano', ano])
    if densid != None:
        reg_ant.append(['escala_dens', densid])
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
    else:
        base = geo_micro
    return base

@st.cache_data
def gera_grafico(df, indicador, geovis, ano):
    import altair as alt

    # Ajuste da variável de geovisão
    if geovis in ['regiao', 'uf']:
        codgeovis = geovis
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
    st.write("Graph:")
    st.altair_chart(chart, theme=None, use_container_width=True)

    # Exibindo o DataFrame na primeira coluna
    st.write("Table:")
    st.dataframe(df, use_container_width=True)


@st.cache_data
def gera_regras(covid, geovis, reg_ant, reg_alvo, indicador, geofiltro, faixa_sup, conf_base, indicador_base):
    df,faixa_sup, conf_base = funcoes_mapa.gera_regras(covid, geovis, reg_ant, reg_alvo, indicador, geofiltro, faixa_sup, conf_base, indicador_base)

    return df, faixa_sup, conf_base


def gera_mapa(covid, geovis, reg_ant, reg_alvo, indicador, geofiltro, filtroBase, faixas, faixa_sup, conf_base, indicador_base):
    # Leitura das coordenadas geográficas, base do mapa
    base = geo_coordenadas(geovis)

    #Gera dataframe base para o mapa
    dfregras, faixa_sup, conf_base = gera_regras(covid, geovis, reg_ant, reg_alvo, indicador, geofiltro, faixa_sup, conf_base, indicador_base)

    #st.write(dfregras)

    mapa,txtrg,dfgeovis = funcoes_mapa.configura_mapa(dfregras, geovis, reg_ant, reg_alvo, indicador, geofiltro, filtroBase, faixas, base)

    return mapa,txtrg,dfgeovis,faixa_sup,conf_base


@st.cache_data
def gera_textobase(filtroBase):
    fano, flocal = '2020 to 2022', 'Brazil'
    for filtro in filtroBase:
        if filtro[0] == 'ano':
            fano = str(filtro[1])
    txtbase = str(flocal) + ' - ' + str(fano)
    return txtbase

@st.cache_data
def novocovid(filtroBase, precovid):
    lista = ['MUITO BAIXA', 'BAIXA', 'MEDIA', 'ALTA', 'MUITO ALTA']
    faixas, covid = funcoes_mapa.preparaBase(filtroBase, precovid)
    faixas['ord'] = faixas.apply(lambda x: 1 if x['categoria'] == 'MUITO BAIXA' else (2 if x['categoria'] == 'BAIXA' else (3 if x['categoria'] == 'MEDIA' else (4 if x['categoria'] == 'ALTA' else 5))), axis=1)
    faixas = faixas.sort_values(['ord'], ascending=[True])
    faixas.drop(['ord'], inplace=True, axis=1)
    return faixas, covid


st.sidebar.markdown(":blue[**Filtro da Base**]")
anobase = st.sidebar.selectbox('1.0', [2020, 2021, 2022], index=None,  placeholder="2020 to 2022", label_visibility="collapsed")

#Cria o filtro base
lista_filtro = [['ano', anobase]]
filtroBase = []
for filtro in lista_filtro:
    if filtro[1] != None:
        filtroBase.append(filtro)

# Gera o texto com informações da base
txtbase = gera_textobase(filtroBase)

#Atualiza base da covid e as faixas de valores
if anobase != None:
    faixas, covid = novocovid(filtroBase, precovid)

#Gera o cabeçalho da página
st.subheader(txtbase, divider='grey')

#st.write(filtroBase)

# Gera lista de anos disponíveis
lista_anos = [2020, 2021, 2022]
for filtro in filtroBase:
    if filtro[0] == 'ano':
        lista_anos = [filtro[1]]

# Widgets de controle para cada coluna
exibir_coluna1 = st.sidebar.checkbox("Map1")
if exibir_coluna1:
    st.sidebar.markdown(":blue[**General Parameters**]")
    geofiltro1 = gera_geofiltro('1.1')
    geovis1 = gera_geovisao('1.2', geofiltro1)
    indicador1 = gera_indicador('1.3')
    st.sidebar.markdown(":blue[**Antecedent  Attributes**]")
    ano1 = st.sidebar.selectbox('1.4', lista_anos, index=None, placeholder="2020 to 2022", label_visibility="collapsed")
    densid1 = gera_densidade('1.5')
    idh1 = gera_idh('1.6')
    reg_ant1 = gera_reg_ant(ano1,densid1,idh1)
    st.sidebar.markdown(":blue[**Consequent Attributes**]")
    reg_alvo1 = [gera_reg_alvo('1.7', '1.8')]



st.sidebar.divider()

exibir_coluna2 = st.sidebar.checkbox("Map2")
if exibir_coluna2:
    st.sidebar.markdown(":blue[**General Parameters**]")
    geofiltro2 = gera_geofiltro('2.1')
    geovis2 = gera_geovisao('2.2', geofiltro2)
    indicador2 = gera_indicador('2.3')
    st.sidebar.markdown(":blue[**Antecedent  Attributes**]")
    ano2 = st.sidebar.selectbox('2.4', lista_anos, index=None, placeholder="2020 to 2022", label_visibility="collapsed")
    densid2 = gera_densidade('2.5')
    idh2 = gera_idh('2.6')
    reg_ant2 = gera_reg_ant(ano2, densid2, idh2)
    st.sidebar.markdown(":blue[**Consequent Attributes**]")
    reg_alvo2 = [gera_reg_alvo('2.7', '2.8')]


# Função para exibir ou ocultar cada coluna dinamicamente
if exibir_coluna1 and not exibir_coluna2:   
    placeholder = st.empty()
    # Se apenas a Coluna 1 for exibida, ocupará toda a tela
    col1, _ = st.columns((1000, 1))  # Define proporção para 999/1000 e 1/1000
    with col1:

        if reg_alvo1 != [[]] and indicador1 != None:

            # Gera o mapa com os dados dos parâmetros passados
            faixa_sup, conf_base, indicador_base = 0,0,''
            mapa1, txtrg1, dfgeovis1, faixa_sup1, conf_base1 = gera_mapa(covid, geovis1, reg_ant1, reg_alvo1, indicador1, geofiltro1, filtroBase, faixas, faixa_sup, conf_base, indicador_base)

            #st.write(faixa_sup, faixa_sup1)

            st.markdown(f'**<span style="font-size:16px;">Regra: {txtrg1}</span>**', unsafe_allow_html=True)
            st_folium(mapa1, width=12000, height=5500)  # Exibe o primeiro mapa usando folium_static

            if len(dfgeovis1) > 0:
                gera_grafico(dfgeovis1, indicador1, geovis1, ano1)
elif exibir_coluna2 and not exibir_coluna1:
    placeholder = st.empty()
    # Se apenas a Coluna 2 for exibida, ocupará toda a tela
    col2, _ = st.columns((1000, 1))  # Define proporção para 999/1000 e 1/1000
    with col2:

        if reg_alvo2 != [[]] and indicador2 != None:

            # Gera o mapa com os dados dos parâmetros passados
            faixa_sup, conf_base, indicador_base = 0,0,''
            mapa2, txtrg2, dfgeovis2, faixa_sup2, conf_base2 = gera_mapa(covid, geovis2, reg_ant2, reg_alvo2, indicador2, geofiltro2, filtroBase, faixas, faixa_sup, conf_base, indicador_base)

            st.markdown(f'**<span style="font-size:16px;">Regra: {txtrg2}</span>**', unsafe_allow_html=True)
            st_folium(mapa2, width=1200, height=550)   # Exibe o segundo mapa usando folium_static

            if len(dfgeovis2) > 0:
                gera_grafico(dfgeovis2, indicador2, geovis2, ano2)
elif exibir_coluna2 and exibir_coluna1:
    # Criando as colunas
    col1, col2 = st.columns(2)
    mapa2 = ''
    with col1:

        if reg_alvo1 != [[]] and indicador1 != None:

            # Gera o mapa com os dados dos parâmetros passados
            faixa_sup, conf_base, indicador_base = 0,0,''
            mapa1, txtrg1, dfgeovis1, faixa_sup1, conf_base1 = gera_mapa(covid, geovis1, reg_ant1, reg_alvo1, indicador1, geofiltro1, filtroBase, faixas, faixa_sup, conf_base, indicador_base)

            st.markdown(f'**<span style="font-size:16px;">Regra: {txtrg1}</span>**', unsafe_allow_html=True)
            mapa1 = st_folium(mapa1, width=610, height=550)  # Exibe o primeiro mapa usando folium_static

            filtro_mapa2 = ''
            if mapa1['last_active_drawing']:
                filtro_mapa2 = mapa1['last_active_drawing']['properties'][geovis1]
                exibir_coluna2 = True

            if filtro_mapa2 != '' and geovis1 in ['regiao', 'uf']:
                geofiltro2 = [geovis1, filtro_mapa2]
                if geovis1 == 'regiao' and geovis2 not in ['mesoregiao', 'uf', 'microregiao']:
                    geovis = 'uf'
                elif geovis1 == 'uf' and geovis2 not in ['mesoregiao', 'microregiao']:
                    geovis = 'mesoregiao'
                else:
                    geovis = geovis2
                indicador2 = indicador1
                ano2 = ano1
                densid2 = densid1
                idh2 = idh1
                reg_ant2 = reg_ant1
                reg_alvo2 = reg_alvo1

                if reg_alvo2 != [[]] and indicador2 != None:

                    # Gera o mapa com os dados dos parâmetros passados
                    indicador_base = indicador1
                    mapa2, txtrg2, dfgeovis2, faixa_sup2, conf_base2 = gera_mapa(covid, geovis, reg_ant2, reg_alvo2, indicador2, geofiltro2, filtroBase, faixas, faixa_sup1, conf_base1, indicador_base)

            else:
                if reg_alvo2 != [[]] and indicador2 != None:

                    # Gera o mapa com os dados dos parâmetros passados
                    indicador_base = indicador1
                    mapa2, txtrg2, dfgeovis2, faixa_sup2, conf_base2 = gera_mapa(covid, geovis2, reg_ant2, reg_alvo2, indicador2, geofiltro2, filtroBase, faixas, faixa_sup1, conf_base1, indicador_base)

            if len(dfgeovis1) > 0:
                gera_grafico(dfgeovis1, indicador1, geovis1, ano1)

        else:
            if reg_alvo2 != [[]] and indicador2 != None:

                # Gera o mapa com os dados dos parâmetros passados
                faixa_sup, conf_base, indicador_base = 0,0,''
                mapa2, txtrg2, dfgeovis2, faixa_sup2, conf_base2 = gera_mapa(covid, geovis2, reg_ant2, reg_alvo2, indicador2, geofiltro2, filtroBase, faixas, faixa_sup, conf_base, indicador_base)



    with col2:
        if mapa2 != '':
            st.markdown(f'**<span style="font-size:16px;">Regra: {txtrg2}</span>**', unsafe_allow_html=True)
            st_folium(mapa2, width=610, height=550)  # Exibe o segundo mapa usando folium_static

            if len(dfgeovis2) > 0:
                gera_grafico(dfgeovis2, indicador2, geovis2, ano2)
    #filtro_mapa2 = ''

else:
    placeholder = st.empty()




