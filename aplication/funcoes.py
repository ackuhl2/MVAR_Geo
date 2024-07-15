import pandas as pd
import folium
import json
import csv
import math
import time
import branca.colormap as cm
import glob
import os
import geopandas as gpd
from folium import Choropleth, StepColormap
import webbrowser


def preparaBase(filtroBase, df2):

    #Executa eventuais filtros na base de dados
    for filtro in filtroBase:
        df2 = df2.loc[(df2[filtro[0]] == filtro[1])]

    lista = [['obcasos', 'obitos', 'pop'],['obpop', 'obitos', 'pop'],['casospop', 'casos', 'pop']]
    faixas = ['MUITO BAIXA', 'BAIXA', 'MEDIA', 'ALTA', 'MUITO ALTA']
    tuplas = len(df2)

    for item in lista:
        df2 = df2.sort_values(by=item, ascending=[True, True, True]).reset_index()
        df2['Posicao'] = df2.apply(lambda x: x.name, axis=1)
        for i in range(len(faixas)):
            df2['tx'+item[0]] = df2.apply(lambda x: faixas[i] if x['Posicao'] >= i*tuplas/len(faixas) else x['tx'+item[0]], axis=1)
        df2.drop(['index', 'Posicao'], inplace=True, axis=1)

    #Gera faixas de valores por métrica
    df3 = df2.groupby(['txobcasos']).agg(minimo=('obcasos', 'min'), maximo=('obcasos', 'max'), qtd=('codmun', 'size')).reset_index()
    df3['fxobcasos'] = df3.apply(lambda x: '> '+str(x['minimo'])+'%' if x['txobcasos'] == 'MUITO ALTA' else '>= '+str(x['minimo'])+' e < '+str(x['maximo'])+'%', axis=1)
    df3 = df3.rename(columns={'txobcasos': 'categoria', 'fxobcasos': 'txobcasos'})
    df3 = df3[['categoria', 'txobcasos']]

    df4 = df2.groupby(['txobpop']).agg(minimo=('obpop', 'min'), maximo=('obpop', 'max'), qtd=('codmun', 'size')).reset_index()
    df4['fxobpop'] = df4.apply(lambda x: '> '+str(x['minimo'])+'%' if x['txobpop'] == 'MUITO ALTA' else '>= '+str(x['minimo'])+' e < '+str(x['maximo'])+'%', axis=1)
    df4 = df4.rename(columns={'txobpop': 'categoria', 'fxobpop': 'txobpop'})
    df4 = df4[['categoria', 'txobpop']]

    df5 = df2.groupby(['txcasospop']).agg(minimo=('casospop', 'min'), maximo=('casospop', 'max'), qtd=('codmun', 'size')).reset_index()
    df5['fxcasospop'] = df5.apply(lambda x: '> '+str(x['minimo'])+'%' if x['txcasospop'] == 'MUITO ALTA' else '>= '+str(x['minimo'])+' e < '+str(x['maximo'])+'%', axis=1)
    df5 = df5.rename(columns={'txcasospop': 'categoria', 'fxcasospop': 'txcasospop'})
    df5 = df5[['categoria', 'txcasospop']]

    #Prepara o dataframe das faixas de valores
    df6 = pd.merge(df3,df4, how="inner", on="categoria")
    df6 = pd.merge(df6,df5, how="inner", on="categoria")

    #Salva os dataframes finais
    df6.to_csv('faixas.csv')
    df2.to_csv('covid.csv')

    return df6, df2


