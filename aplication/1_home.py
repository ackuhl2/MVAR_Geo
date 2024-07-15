import streamlit as st
import geopandas as gpd
import folium
import pandas as pd
import json
import csv
import math
import time
import branca.colormap as cm
import glob
import os
import sys
sys.path.insert(0, 'C:/Users/ANDERSON/PycharmProjects/mapa_de_calor/covid/aplication')
from suporte import funcoes_mapa

#Monta o cabeçalho
#st.sidebar.header('Filtros da Base', divider='grey')

#st.write('<style>div.reportview-container .main{padding-top:-1rem;padding-bottom: 5rem;padding-left: 0.5rem;padding-right: 0.5rem;}</style>', unsafe_allow_html=True)

# Define o caminho dos arquivos de suporte do aplicativo
path = os.path.join(os.sep, 'Users', 'ANDERSON', 'PycharmProjects', 'mapa_de_calor', 'covid', 'aplication', 'suporte', '')

# Definir o título do aplicativo
st.markdown(""" <h1 style='text-align: center; color: black;'>MVAR-Geo</h1> """, unsafe_allow_html=True )
st.markdown(""" <h2 style='text-align: center; color: red;'>A Proposal for Visualizing Georeferenced Association Rules</h2> """, unsafe_allow_html=True )

# Exibe mapa
col1, col2, col3 = st.columns([1,4,1])

with col2:
    st.image(os.path.join(path, "world.jpg"), width = 800) #use_column_width ='auto')




#Lê as bases para o mapa de antenas
@st.cache_data
def antenas(path):
    df = pd.read_csv(os.path.join(path, "dfra.csv"), encoding='utf-8', delimiter=",")
    df2 = pd.read_csv(os.path.join(path, "dfbairro.csv"), encoding='utf-8', delimiter=",")
    df3 = pd.read_csv(os.path.join(path, "dfantenas.csv"), encoding='utf-8', delimiter=",")
    return df, df2, df3

#Lê a base precovid
@st.cache_data
def precovid(path):
    df2 = pd.read_csv(os.path.join(path, "precovid.csv"), encoding='utf-8', delimiter=",")
    return df2

#Lê a base eleicoes
@st.cache_data
def eleicoes(path):
    df2 = pd.read_csv(os.path.join(path, "eleicoes.csv"), encoding='Latin 1', delimiter=",")
    return df2

precovid = precovid(path)

#Cria lista de anos
#ano = st.sidebar.selectbox('Ano', [2020,2021,2022], index=None)

#Cria lista de regiões
#regiao = st.sidebar.selectbox('Região', ['CO','N','NE','S','SE'], index=None)

#Cria lista de UF, com base na região escolhida
#if regiao != None:
#    lista = [['N', 'AC'], ['NE', 'AL'], ['N', 'AP'], ['N', 'AM'], ['NE', 'BA'], ['NE', 'CE'], ['CO', 'DF'],['SE', 'ES'], ['CO', 'GO'], ['NE', 'MA'], ['CO', 'MT'], ['CO', 'MS'], ['SE', 'MG'],
#             ['N', 'PA'], ['NE', 'PB'], ['S', 'PR'], ['NE', 'PE'], ['NE', 'PI'], ['SE', 'RJ'], ['NE', 'RN'],['S', 'RS'], ['N', 'RO'], ['N', 'RR'], ['S', 'SC'], ['SE', 'SP'], ['NE', 'SE'], ['N', 'TO']]
#    lista_uf = []
#    for item in lista:
#        if item[0] == regiao:
#            lista_uf.append(item[1])
#    uf = st.sidebar.selectbox('UF', lista_uf, index=None)
#else:
#    uf = None

#Cria o filtro base
#lista_filtro = [['ano', ano],['regiao',regiao],['uf',uf]]
#filtroBase = []
#for filtro in lista_filtro:
#    if filtro[1] != None:
#        filtroBase.append(filtro)

#@st.cache_data
#def gera_textobase(filtroBase):
#    fano, flocal = '2020 a 2022', 'Brasil'
#    for filtro in filtroBase:
#        if filtro[0] == 'ano':
#            fano = str(filtro[1])
#        else:
#            if filtro[0].upper() == 'UF':
#                flocal = (filtro[0].upper() + '(' + str(filtro[1].upper()) + ')')
#            else:
#                flocal = (filtro[0].title() + '(' + str(filtro[1].upper()) + ')')
#   txtbase = str(flocal) + ' - ' + str(fano)
#    return txtbase

@st.cache_data
def geo_coordenadas(path):
    geo_uf = gpd.read_file(os.path.join(path, "uf.geojson"), encoding='utf-8')
    geo_meso = gpd.read_file(os.path.join(path, "mesoregiao.geojson"), encoding='utf-8')
    geo_micro = gpd.read_file(os.path.join(path, "microregiao.geojson"), encoding='utf-8')
    geo_regiao = gpd.read_file(os.path.join(path, "regiao.geojson"), encoding='utf-8')
    geo_ra = gpd.read_file(os.path.join(path, "ra.geojson"), encoding='utf-8')
    geo_bairro = gpd.read_file(os.path.join(path, "bairro.geojson"), encoding='utf-8')
    geo_mun = gpd.read_file(os.path.join(path, "municipio.geojson"), encoding='utf-8')
    return geo_uf, geo_meso, geo_micro, geo_regiao, geo_ra, geo_bairro, geo_mun

@st.cache_data
def covid(precovid):
    filtroBase = []
    lista = ['MUITO BAIXA', 'BAIXA', 'MEDIA', 'ALTA', 'MUITO ALTA']
    faixas, covid = funcoes_mapa.preparaBase(filtroBase, precovid)
    faixas['ord'] = faixas.apply(lambda x: 1 if x['categoria'] == 'MUITO BAIXA' else (2 if x['categoria'] == 'BAIXA' else (3 if x['categoria'] == 'MEDIA' else (4 if x['categoria'] == 'ALTA' else 5))), axis=1)
    faixas = faixas.sort_values(['ord'], ascending=[True])
    faixas.drop(['ord'], inplace=True, axis=1)
    return faixas, covid


#Inicia rotina
inicio = time.time()

dfra, dfbairro, dfantenas = antenas(path)
eleicoes = eleicoes(path)
faixas, covid = covid(precovid)
geo_uf, geo_meso, geo_micro, geo_regiao, geo_ra, geo_bairro, geo_mun = geo_coordenadas(path)

# Gera o texto com informações da base
#txtbase = gera_textobase(filtroBase)

#st.header('Faixas de valores da Base')
#st.dataframe(faixas, hide_index = True)

st.session_state['faixas'] = faixas
st.session_state['covid'] = covid
st.session_state['precovid'] = precovid
#st.session_state['filtroBase'] = filtroBase
st.session_state['geo_uf'] = geo_uf
st.session_state['geo_meso'] = geo_meso
st.session_state['geo_micro'] = geo_micro
st.session_state['geo_regiao'] = geo_regiao
st.session_state['geo_ra'] = geo_ra
st.session_state['geo_bairro'] = geo_bairro
st.session_state['geo_mun'] = geo_mun
#st.session_state['txtbase'] = txtbase
st.session_state['dfra'] = dfra
st.session_state['dfbairro'] = dfbairro
st.session_state['dfantenas'] = dfantenas
st.session_state['eleicoes'] = eleicoes



fim = time.time()
st.write(fim - inicio)

#st.write(geo_mun)

#simplifica geojson
#geo_ra = gpd.read_file(os.path.join(path, "municipio.geojson"), encoding='utf-8')
#tolerance = 0.01
#geo_ra['geometry_simplificada'] = geo_ra.geometry.simplify(tolerance=tolerance)
#geo_ra = geo_ra.drop(columns=['geometry'])
#geo_ra['geometry'] = geo_ra['geometry_simplificada']
#geo_ra = geo_ra.drop(columns=['geometry_simplificada'])
#geo_ra = geo_ra.rename(columns={'codarea': 'CODMUN'})
#geo_ra.to_file(os.path.join(path, 'municipio_simplificado.geojson'), driver='GeoJSON')

#concatena arquivos pandas com geopandas
#geo_micro_old = gpd.read_file(os.path.join(path, "municipio.geojson"), encoding='utf-8')
#campos = pd.read_csv(os.path.join(path, "municipio.csv"), encoding='Latin 1', delimiter=";")
#campos = campos.astype(str)
#merged_gdf = geo_micro_old.merge(campos, on='CODMUN', how='inner')
#merged_gdf = merged_gdf.drop(columns=['CODMICRO','CODMESO','LAT','LONG','IDH2010','ESCALA_IDH','POP','AREA','DENSID','ESCALA_DENS','ALT'])
#merged_gdf.to_file(os.path.join(path, 'municipio_new.geojson'), driver='GeoJSON')
#st.write(merged_gdf)


#streamlit run C:\Users\ANDERSON\PycharmProjects\mapa_de_calor\covid\aplication\1_home.py --server.port 8502
