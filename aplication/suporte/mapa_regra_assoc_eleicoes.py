import funcoes_eleicoes
import folium
import pandas as pd
import geopandas as gpd
import json
import csv
import math
import time
import branca.colormap as cm
import glob
import os

#Inicia rotina
inicio = time.time()


#Variáveis de referência
path = os.path.join(os.sep,'Users','ANDERSON', 'PycharmProjects','mapa_de_calor','covid')

geovis = 'municipio'
reg_ant = []
reg_alvo = [['vencedor', 'ESQUERDA']]
indicador = 'sup'
geofiltro = ['uf','SP']
eleicao = 2018

base = gpd.read_file(geovis+".geojson", encoding='utf-8')

eleicoes = pd.read_csv('eleicoes.csv', delimiter=",", encoding='latin')


#Gera as bases de regras para a geovisualização e para os símbolos
dfregras, faixa_sup, conf_base = funcoes_eleicoes.gera_regras(eleicoes, eleicao, geovis, reg_ant, reg_alvo, indicador, geofiltro, 0,0,'')

mapa,txtrg,dfgeovis = funcoes_eleicoes.configura_mapa(dfregras, geovis, reg_ant, reg_alvo, indicador, geofiltro, base, eleicao)

print(dfgeovis[['clasvis','faixaindicador']])


fim = time.time()
print(fim - inicio)







