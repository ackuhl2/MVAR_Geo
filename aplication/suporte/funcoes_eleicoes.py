import pandas as pd
import folium
from branca.element import Template, MacroElement
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

def gera_regras(eleicoes, geovis, reg_ant, reg_alvo, indicador, geofiltro, faixa_sup, conf_base, indicador_base):

    txtant, txtalvo,txtcons, classes = '','','',11

    # Cria valor de referência para o suporte
    n = eleicoes['qt_secoes'].sum()

    # Aplica a regra do antecedente
    df_ant = eleicoes.copy()
    contagem = 0
    for regra in reg_ant:
        contagem += 1
        df_ant = df_ant.loc[(df_ant[regra[0]] == regra[1])]
        if contagem == 1:
            txtant = txtant + '(' + regra[0] + '="' + str(regra[1]) + '")'
        else:
            txtant = txtant + ' ^ (' + regra[0] + '="' + str(regra[1]) + '")'

    # Aplica a regra do consequente
    df_cons = eleicoes.copy()
    contagem = 0
    for regra in reg_alvo:
        contagem += 1
        df_cons = df_cons.loc[(df_cons[regra[0]] == regra[1])]
        if contagem == 1:
            txtalvo = txtalvo + '(' + regra[0] + '="' + str(regra[1]) + '")'
            txtcons = '("' + str(regra[1]) + '")'
        else:
            txtalvo = txtalvo + ' ^ (' + regra[0] + '="' + str(regra[1]) + '")'
            txtcons = txtcons + ' ^ ("' + str(regra[1]) + '")'

    # Aplica a regra do consequente dado o antecedente
    df = df_ant.copy()
    for regra in reg_alvo:
        df = df.loc[(df[regra[0]] == regra[1])]

    # Cria o valor do suporte do consequente
    sup_cons = int(df_cons['qt_secoes'].sum() / n * 10000) / 100

    # Define o caminho dos arquivos de dados geográficos
    path = os.path.join(os.sep, 'Users', 'ANDERSON', 'PycharmProjects', 'mapa_de_calor', 'covid', 'aplicativo', 'suporte', '')

    # Gera a base do df, de acordo com a variável geovis
    localidade = pd.read_csv(os.path.join(path, geovis + ".csv"), delimiter=";", encoding='latin')
    if geovis in ['regiao', 'uf']:
        agrupador = geovis
        nomegeovis = 'NM' + geovis.upper()
    elif geovis == 'municipio':
        agrupador = 'codmun'
        nomegeovis = geovis.upper()
    else:
        agrupador = "cod" + geovis[:-6]
        nomegeovis = geovis.upper()

    # Cria valor de referência para o suporte
    df = df.groupby(by=[df[agrupador]]).agg(sup_alvo=('qt_secoes', 'sum')).reset_index()
    df_ant = df_ant.groupby(by=[df_ant[agrupador]]).agg(sup_ant=('qt_secoes', 'sum')).reset_index()
    df = df_ant.merge(df, on=[agrupador], how='left', suffixes=['1', '2'], indicator=False, sort=True)
    df = df.fillna(0)
    df['sup_alvo'] = df['sup_alvo'].astype(int)

    # Junta base com os dados da localidade e inclui geofiltro, se for o caso
    if len(geofiltro) == 0:
        localidade = localidade[[agrupador.upper(), nomegeovis, 'LAT', 'LONG']]
        localidade.columns = [agrupador, 'nm' + geovis, 'lat', 'long']
        df = df.merge(localidade, on=[agrupador], how='inner', suffixes=['1', '2'], indicator=False, sort=True)
        df.columns = [agrupador, 'qtd_ant', 'qtd_alvo', 'localidade', 'lat', 'long']
    else: #inclui coluna do geofiltro
        localidade = localidade[[agrupador.upper(), nomegeovis, 'LAT', 'LONG', geofiltro[0].upper()]]
        localidade.columns = [agrupador, 'nm' + geovis, 'lat', 'long', geofiltro[0]]
        df = df.merge(localidade, on=[agrupador], how='inner', suffixes=['1', '2'], indicator=False, sort=True)
        df.columns = [agrupador, 'qtd_ant', 'qtd_alvo', 'localidade', 'lat', 'long', geofiltro[0]]

    # Transforma as colunas lat e long em tipo float
    lista = ['lat', 'long']
    for item in lista:
        df[item] = df[item].apply(lambda x: str(x).replace('.', '').replace(',', '.')).astype(float)

    # Gera índices de suporte, confiança e lift
    df['supant'] = df.apply(lambda x: int(x['qtd_ant'] / n * 10000) / 100, axis=1)
    df['sup'] = df.apply(lambda x: int(x['qtd_alvo'] / n * 10000) / 100, axis=1)
    df['conf'] = df.apply(lambda x: int(x['qtd_alvo'] / x['qtd_ant'] * 10000) / 100, axis=1)
    df['lift'] = df.apply(lambda x: int(x['qtd_alvo'] / x['qtd_ant'] / sup_cons * 10000) / 100, axis=1)

    #Gera as classes para visualização do peso da regras
    if indicador == 'sup':
        indmax, indmin = df[indicador].max(), df[indicador].min()

        # Define as faixas de valores de acordo com o valor da variável faixa_sup
        if faixa_sup == 0 or indicador_base != indicador:
            df['clasvis'] = df.apply(lambda x: int(((x[indicador] - 0) / (indmax - 0) - 0.00049) * classes) + 1, axis=1).astype(int)
            df['faixaindicador'] = df.apply(lambda x: 'from ' + str(int((0 + (int(x['clasvis']) - 1) * (indmax - 0 + 0.000499) / classes) * 100) / 100) + ' to ' + str(int((0 + int(x['clasvis']) * (indmax - 0 + 0.000599) / classes) * 100) / 100) + '%' if x['clasvis'] < 11
                else 'Above ' + str(int((10 * (indmax - 0 + 0.00049) / classes) * 100) / 100) + '%', axis=1)
        else:
            df['clasvis'] = df.apply(lambda x: int(((x[indicador] - 0) / (faixa_sup - 0) - 0.00049) * (classes-1)) + 1 if x[indicador] <= faixa_sup else 11, axis=1).astype(int)
            df['faixaindicador'] = df.apply(lambda x: 'from ' + str(int((0 + (int(x['clasvis']) - 1) * (faixa_sup - 0 + 0.000499) / (classes-1)) * 100) / 100) + ' to ' + str(int((0 + int(x['clasvis']) * (faixa_sup - 0 + 0.000599) / (classes-1)) * 100) / 100) + '%' if x['clasvis'] < 11
                else 'Above ' + str(int((faixa_sup - 0 + 0.00049) * 100) / 100) + '%', axis=1)

    elif indicador == 'conf':
        indmax, indmin = df[indicador].max(), df[indicador].min()

        # Define as faixas de valores de acordo com o valor da variável faixa_sup
        if faixa_sup == 0 or indicador_base != indicador:
            df['clasvis'] = df.apply(lambda x: int(((x[indicador] - 0) / ((sup_cons-1) - 0) - 0.00049) * 5) + 1 if x[indicador] < (sup_cons-1) else 6, axis=1).astype(int)
            df['clasvis'] = df.apply(lambda x: int(((x[indicador] - (sup_cons+1)) / (indmax - (sup_cons+1)) - 0.00049) * 5) + 7 if x[indicador] > (sup_cons+1) else x['clasvis'], axis=1).astype(int)
            df['faixaindicador'] = df.apply(lambda x: 'from ' + str(int((0 + (int(x['clasvis']) - 1) * ((sup_cons-1) - 0) / 5) * 100) / 100) + ' to ' + str(int((0 + int(x['clasvis']) * (sup_cons-1 - 0) / 5) * 100) / 100) + '%' if x['clasvis'] < 6
                else ('from ' + str(int((sup_cons+1 + (int(x['clasvis']) - 7) * (indmax - (sup_cons+1) + 0.00049) / 5) * 100) / 100) + ' to ' + str(int((sup_cons+1 + (int(x['clasvis']) - 6) * (indmax - (sup_cons+1) + 0.00049) / 5) * 100) / 100) + '%' if x['clasvis'] > 6 and x['clasvis'] < 11
                else ('Above ' + str(int((sup_cons + 1 + (int(x['clasvis']) - 7) * (indmax - (sup_cons + 1) + 0.00049) / 5) * 100) / 100) + '%' if x['clasvis'] == 11
                else 'from ' + str(int((sup_cons-1) * 100) / 100) + ' to ' + str(sup_cons+1) + '%')), axis=1)
        else:
            df['clasvis'] = df.apply(lambda x: int(((x[indicador] - 0) / ((conf_base-1) - 0) - 0.00049) * 5) + 1 if x[indicador] < (conf_base-1) else 6, axis=1).astype(int)
            df['clasvis'] = df.apply(lambda x: int(((x[indicador] - (conf_base + 1)) / (faixa_sup - (conf_base + 1)) - 0.00049) * 4) + 7 if x[indicador] > (conf_base + 1) and x[indicador] <= faixa_sup else x['clasvis'], axis=1).astype(int)
            df['clasvis'] = df.apply(lambda x: 11 if x[indicador] > faixa_sup else x['clasvis'], axis=1).astype(int)
            df['faixaindicador'] = df.apply(lambda x: 'from ' + str(int((0 + (int(x['clasvis']) - 1) * ((conf_base - 1) - 0) / 5) * 100) / 100) + ' to ' + str(int((0 + int(x['clasvis']) * (conf_base - 1 - 0) / 5) * 100) / 100) + '%' if x['clasvis'] < 6
            else ('from ' + str(int((conf_base + 1 + (int(x['clasvis']) - 7) * (faixa_sup - (conf_base + 1) + 0.00049) / 4) * 100) / 100) + ' to ' + str(int((conf_base + 1 + (int(x['clasvis']) - 6) * (faixa_sup - (conf_base + 1) + 0.00049) / 4) * 100) / 100) + '%' if x['clasvis'] > 6 and x['clasvis'] < 11
            else ('Above ' + str(faixa_sup) + '%' if x['clasvis'] == 11
            else 'from ' + str(int((conf_base - 1) * 100) / 100) + ' to ' + str(conf_base + 1) + '%')), axis=1)


    else:  # indicador == 'lift':
        indmax, indmin = df[indicador].max(), df[indicador].min()

        # Define as faixas de valores de acordo com o valor da variável faixa_sup e do indicador_base
        if faixa_sup == 0 or indicador_base != indicador:
            df['clasvis'] = df.apply(lambda x: int(((x[indicador] - 0) / (0.95 - 0) - 0.00049) * 5) + 1 if x[indicador] < 0.95 else 6, axis=1).astype(int)
            df['clasvis'] = df.apply(lambda x: int(((x[indicador] - 1.05) / (indmax - 1.05) - 0.00049) * 5) + 7 if x[indicador] > 1.05 else x['clasvis'], axis=1).astype(int)
            df['faixaindicador'] = df.apply(lambda x: 'from ' + str(int((0 + (int(x['clasvis']) - 1) * (0.95 - 0) / 5) * 100) / 100) + ' to ' + str(int((0 + int(x['clasvis']) * (0.95 - 0) / 5) * 100) / 100) if x['clasvis'] < 6
                else ('from ' + str(int((1.05 + (int(x['clasvis']) - 7) * (indmax - 1.05 + 0.00049) / 5) * 100) / 100) + ' to ' + str(int((1.05 + (int(x['clasvis'])-6) * (indmax - 1.05 + 0.00049) / 5) * 100) / 100) if x['clasvis'] > 6 and x['clasvis'] < 11
                else ('Above ' + str(int((1.05 + (int(x['clasvis']) - 7) * (indmax - 1.05 + 0.00049) / 5) * 100) / 100)  if x['clasvis'] == 11
                else 'from ' + str(0.95) + ' to ' + str(1.05))), axis=1)
        else:
            df['clasvis'] = df.apply(lambda x: int(((x[indicador] - 0) / (0.95 - 0) - 0.00049) * 5) + 1 if x[indicador] < 0.95 else 6, axis=1).astype(int)
            df['clasvis'] = df.apply(lambda x: int(((x[indicador] - 1.05) / (faixa_sup - 1.05) - 0.00049) * 4) + 7 if x[indicador] > 1.05 and x[indicador] <= faixa_sup else x['clasvis'], axis=1).astype(int)
            df['clasvis'] = df.apply(lambda x: 11 if x[indicador] > faixa_sup else x['clasvis'], axis=1).astype(int)
            df['faixaindicador'] = df.apply(lambda x: 'from ' + str(int((0 + (int(x['clasvis']) - 1) * (0.95 - 0) / 5) * 100) / 100) + ' to ' + str(int((0 + int(x['clasvis']) * (0.95 - 0) / 5) * 100) / 100) if x['clasvis'] < 6
                else ('from ' + str(int((1.05 + (int(x['clasvis']) - 7) * (faixa_sup - 1.05 + 0.00049) / 4) * 100) / 100) + ' to ' + str(int((1.05 + (int(x['clasvis']) - 6) * (faixa_sup - 1.05 + 0.00049) / 4) * 100) / 100) if x['clasvis'] > 6 and x['clasvis'] < 11
                else ('Above ' + str(faixa_sup) if x['clasvis'] == 11
                else 'from ' + str(0.95) + ' to ' + str(1.05))), axis=1)

    #define o textos do mapa
    if txtant != '':
        df['regra'] = df.apply(lambda x: '('+ geovis + '="' + x['localidade'] + '") ^ ' + txtant + ' ==> ' + txtalvo, axis=1)
    else:
        df['regra'] = df.apply(lambda x: '(' + geovis + '="' + x['localidade'] + '")' + txtant + ' ==> ' + txtalvo,axis=1)

    df['txtsupant'] = df.apply(lambda x: str(x['supant']) + '% => Qt Ant/Tot' + ' Urnas = ' + str(x['qtd_ant']) + '/' + str(n), axis=1)
    df['txtsup'] = df.apply(lambda x: str(x['sup']) + '% => Qt Alvo/Tot' + ' Urnas = ' + str(x['qtd_alvo']) + '/' + str(n), axis=1)
    df['txtconf'] = df.apply(lambda x: str(x['conf']) + '% => Qt Alvo/Qt Ant = ' + str(x['qtd_alvo']) + '/' + str(x['qtd_ant']), axis=1)
    df['txtlift'] = df.apply(lambda x: str(x['lift']) + ' =>  Conf/Sup'+txtcons.lower()+' = '+ str(x['conf'])+' / ' + str(sup_cons) + '%', axis=1)
    df['txtconseq'] = df.apply(lambda x: 'Aumento de chances do alvo em ' + str(x['lift']) + ' vezes' if float(x['lift']) >= 1 else 'Redução de chances do alvo em ' + str(int((1 - float(x['lift'])) * 10000) / 100) + '%', axis=1)


    #Executa o geofiltro
    if len(geofiltro) > 0:
        df = df.loc[(df[geofiltro[0]] == geofiltro[1])]

    # Insere linhas de ajuste para a legenda do mapa coroplético
    for i in range(classes):
        nova_linha = pd.DataFrame()
        for coluna in df.columns:
            if coluna == 'clasvis':
                nova_linha[coluna] = [i+1]
            elif coluna == agrupador:
                nova_linha[coluna] = ['AJ'+str(i+1)]
            elif coluna == 'faixaindicador':
                if indicador == 'conf':
                    if faixa_sup == 0 or indicador_base != indicador:
                        nova_linha[coluna] = 'from ' + str(int((0 + i * ((sup_cons-1) - 0) / 5) * 100) / 100) + ' to ' + str(int((0 + (i+1) * (sup_cons-1 - 0) / 5) * 100) / 100) + '%' if (i+1) < 6 \
                            else ('from ' + str(int((sup_cons+1 + (i - 6) * (indmax - (sup_cons+1)) / 5) * 100) / 100) + ' to ' + str(int((sup_cons+1 + (i - 5) * (indmax - (sup_cons+1)) / 5) * 100) / 100) + '%' if (i+1) > 6 and (i+1) < 11
                            else ('Above ' + str(int((sup_cons+1 + (i - 6) * (indmax - (sup_cons+1)) / 5) * 100) / 100) + '%' if (i+1) == 11
                            else 'from ' + str(int((sup_cons-1) * 100) / 100) + ' to ' + str(int((sup_cons+1) * 100) / 100) + '%'))
                    else:
                        nova_linha[coluna] = 'from ' + str(int((0 + i * ((conf_base-1) - 0) / 5) * 100) / 100) + ' to ' + str(int((0 + (i+1) * (conf_base-1 - 0) / 5) * 100) / 100) + '%' if (i+1) < 6 \
                            else ('from ' + str(int((conf_base + 1 + (i - 6) * (faixa_sup - (conf_base + 1) + 0.00049) / 4) * 100) / 100) + ' to ' + str(int((conf_base + 1 + (i - 5) * (faixa_sup - (conf_base + 1) + 0.00049) / 4) * 100) / 100) + '%' if (i+1) > 6 and (i+1) < 11
                            else ('Above ' + str(faixa_sup) + '%' if (i+1) == 11
                            else 'from ' + str(int((conf_base - 1) * 100) / 100) + ' to ' + str(int((conf_base + 1) * 100) / 100) + '%'))

                elif indicador == 'lift':
                    if faixa_sup == 0 or indicador_base != indicador:
                        nova_linha[coluna] = 'from ' + str(int((0 + i * (0.95 - 0) / 5) * 100) / 100) + ' to ' + str(int((0 + (i + 1) * (0.95 - 0) / 5) * 100) / 100) if (i+1) < 6 \
                            else ('from ' + str(int((1.05 + (i - 6) * (indmax - 1.05) / 5) * 100) / 100) + ' to ' + str(int((1.05 + (i - 5) * (indmax - 1.05) / 5) * 100) / 100) if (i+1) > 6 and (i+1) < 11
                            else ('Above ' + str(int((1.05 + (i - 6) * (indmax - 1.05) / 5) * 100) / 100) if (i+1) == 11
                            else 'from ' + str(0.95) + ' to ' + str(1.05)))
                    else:
                        nova_linha[coluna] = 'from ' + str(int((0 + i * (0.95 - 0) / 5) * 100) / 100) + ' to ' + str(int((0 + (i+1) * (0.95 - 0) / 5) * 100) / 100) if (i+1) < 6 \
                            else ('from ' + str(int((1.05 + (i - 6) * (faixa_sup - 1.05 + 0.00049) / 4) * 100) / 100) + ' to ' + str(int((1.05 + (i - 5) * (faixa_sup - 1.05 + 0.00049) / 4) * 100) / 100) if (i+1) > 6 and (i+1) < 11
                            else ('Above ' + str(faixa_sup) if (i+1) == 11
                            else 'from ' + str(0.95) + ' to ' + str(1.05)))
                else:
                    if faixa_sup == 0 or indicador_base != indicador:
                        nova_linha[coluna] = 'from ' + str(int((0 + i * (indmax - 0 + 0.000499) / classes) * 100) / 100) + ' to ' + str(int((0 + (i+1) * (indmax - 0 + 0.000599) / classes) * 100) / 100) + '%' if (i+1) < 11 \
                            else 'Above ' + str(int((10 * (indmax - 0 + 0.00049) / classes) * 100) / 100) + '%'
                    else:
                        nova_linha[coluna] = 'from ' + str(int((0 + i * (faixa_sup - 0 + 0.000499) / (classes-1)) * 100) / 100) + ' to ' + str(int((0 + (i+1) * (faixa_sup - 0 + 0.000599) / (classes-1)) * 100) / 100) + '%' if (i+1) < 11 \
                            else 'Above ' + str(int((faixa_sup - 0 + 0.00049) * 100) / 100) + '%'

            elif df[coluna].dtypes in ['float64', 'float32']:
                nova_linha[coluna] = [0.0]
            elif df[coluna].dtypes in ['int64', 'int32']:
                nova_linha[coluna] = [0]
            else:
                nova_linha[coluna] = ['-']
        df = pd.concat([df, nova_linha], axis=0)

    # Define um novo valor para faixa_sup
    if indicador == 'conf':
        faixa_sup = int((sup_cons + 1 + (11 - 7) * (indmax - (sup_cons + 1) + 0.00049) / 5) * 100) / 100
    elif indicador == 'lift':
        faixa_sup = int((1.05 + (11 - 7) * (indmax - 1.05 + 0.00049) / 5) * 100) / 100
    else:
        faixa_sup = int((10 * (indmax - 0 + 0.00049) / classes) * 100) / 100

        #df.to_csv('check.csv')

    return df, faixa_sup, sup_cons


def configura_mapa(dfgeovis, geovis, reg_ant, reg_alvo, indicador, geofiltro, base, eleicao):

    # Define o caminho dos arquivos de coordenadas geográficas
    path = os.path.join(os.sep, 'Users', 'ANDERSON', 'PycharmProjects', 'mapa_de_calor', 'covid', 'aplicativo', 'suporte', '')

    # Gera a base de regras para a geovisualização dos dados
    geoclasses = 11

    # Leitura das coordenadas geográficas e gera a base do mapa
    if geovis == 'regiao':
        codgeovis = geovis
        base = base.rename(columns={'SIGLA': codgeovis})
    elif geovis == 'uf':
        codgeovis = geovis
        base = base.rename(columns={'UF': codgeovis})
    elif geovis == 'municipio':
        codgeovis = 'codmun'
        base = base.rename(columns={'CODMUN': codgeovis})
        dfgeovis[codgeovis] = dfgeovis[codgeovis].astype(str)
    else: #if geovis in ['mesoregiao', 'microregiao']:
        codgeovis = "cod" + geovis[:-6]
        dfgeovis[codgeovis] = dfgeovis[codgeovis].astype(str)
        base = base.rename(columns={'GEOCODIGO': codgeovis})
    base = base.merge(dfgeovis, on=codgeovis, how='inner')

    ######################################################################################################

    # Configura o mapa base

    # Lista de referencia de renderização de mapas com geofiltro
    listageo = [['uf', 'UF', 6], ['regiao', 'REGIAO', 5]]

    # Renderizando o mapa com algumas personalizações:
    if len(geofiltro) == 0:
        mapa = folium.Map(location=[-16.31091683, -52.01412306], zoom_start=4, tiles='OpenStreetMap', name="Título do Mapa")
    else:
        base = base.loc[(base[geofiltro[0].upper()] == geofiltro[1])]
        for geo in listageo:
            if geo[0] == geofiltro[0]:
                coord = pd.read_csv(os.path.join(path, geofiltro[0] + '.csv'), delimiter=";", encoding='latin', usecols=[geo[1].upper(), 'LAT', 'LONG'])
                coord = coord.loc[(coord[geo[1]] == geofiltro[1])]
                lat, long = coord['LAT'].max(), coord['LONG'].max()
                lat, long = lat.replace('.', '').replace(',', '.'), long.replace('.', '').replace(',', '.')
                mapa = folium.Map(location=[lat, long], zoom_start=geo[2], tiles='OpenStreetMap', name="Título do Mapa")
                break

    ##########################################################################################################

    # Cria o mapa base

    Choropleth = folium.Choropleth(
        geo_data=base,
        name="Mapa de Covid por " + codgeovis,
        data=dfgeovis,
        columns=[codgeovis, 'clasvis'],
        key_on='feature.properties.' + codgeovis,
        bins=geoclasses,
        nan_fill_color='green',
        line_color='brown',
        line_weight=2,
        fill_color="RdYlGn_r",
        fill_opacity=0.7,
        line_opacity=0.4,
        legend_name='--------------------------------------------------Escala de Cores das Áreas Geográficas(' + indicador.title() + ')',
        highlight=True,
        smooth_factor=0
    ).add_to(mapa)

    # Adiciona tooltips ao mapa
    style_function = ("font-size: 11px; font-weight: bold; color: white;  background-color: grey;")
    Choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['localidade', 'txtsupant', 'txtsup', 'txtconf', 'txtlift', 'txtconseq'],
        aliases=[geovis.title()+':', 'Sup Ant:', 'Sup Alvo:', 'Confiança:', 'Lift:', 'Resumo:'],
        style=style_function, labels=True))

    # Adiciona opções de tipos de terrenos ao mapa
    tiles = ['OpenStreetMap', 'CartoDB dark_matter', 'CartoDB positron']
    for tile in tiles:
        folium.raster_layers.TileLayer(tile).add_to(mapa)

        # Retira a legenda Original
    for key in Choropleth._children:
        if key.startswith('color_map'):
            del (Choropleth._children[key])

    ##########################################################################################################

    # Implementa legenda customizada

    # Define variáveis base
    cores, listafaixas = [], []
    coratual = ''
    classeatual = 0
    listacores = ['#006837', '#1a9850', '#66bd63', '#a6d96a', '#d9ef8b', '#ffffbf', '#fee08b', '#fdae61', '#f46d43', '#d73027', '#a50026']

    # Gera a base de regras para a geração da legenda
    dfgeovis = dfgeovis.sort_values(['clasvis', codgeovis], ascending=[False, True])

    # Cria as listas para a geração da legenda das localidades geográficas
    for row in dfgeovis.itertuples():
        if row.clasvis != classeatual:
            listafaixas.append(row.faixaindicador)
            classeatual = row.clasvis
            cor = listacores[row.clasvis - 1]
            cores.append(cor)

    # Cria legenda customizada
    listafaixas.reverse()
    cores.reverse()

    add_line_legend(mapa, title='Measure of Interest(' + indicador.title() + ')', width=140, colors=cores, labels=listafaixas)

    #########################################################################################################

    # Cria um título multilinha em HTML para o mapa

    txtrg = '(' + geovis + ')'

    # Gera informações da regra do antecedente
    for regra in reg_ant:
        txtrg = txtrg + '^(' + regra[0] + '="' + str(regra[1]).lower() + '")'

    # Gera informações da regra do consequente
    contagem = 0
    for regra in reg_alvo:
        contagem += 1
        if contagem == 1:
            txtrg = txtrg + '=>' + '(' + regra[0] + '="' + str(regra[1]).lower() + '")'
        else:
            txtrg = txtrg + '^(' + '(' + regra[0] + '="' + str(regra[1]).lower() + '")'

    # Configura o html do título
    anoeleicao = '2018 and 2022' if eleicao == None else eleicao
    titulo_multilinha = """   
    <h4><b>Elections Map</b></h4>  
    <h5><b>Election: """ + str(anoeleicao) + """</b></h5>
    <h6><b>Measure of Interest: """ + indicador.title() + """</b></h6>     
    """

    # Adiciona o Título ao mapa
    add_title(mapa, title=titulo_multilinha, width=160, color='black')

    # create a layer control
    folium.LayerControl().add_to(mapa)

    return mapa, txtrg, dfgeovis


def add_line_legend(folium_map, title, width, colors, labels):
    if len(colors) != len(labels):
        raise ValueError("colors and labels must have the same length.")

    color_by_label = dict(zip(labels, colors))

    legend_categories = ""
    for label, color in color_by_label.items():
        legend_categories += f"""<li><span style='background:{color}; opacity:0.7;'></span>{label}</li>
                              """
    m = folium_map

    template = """
    {% macro html(this, kwargs) %}

    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>jQuery UI Draggable - Default functionality</title>
      <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
      <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
      <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
      <script>
      $( function() {
        $( "#maplegend" ).draggable({
                        start: function (event, ui) {
                            $(this).css({
                                right: "auto",
                                top: "auto",
                                bottom: "auto"
                            });
                        }
                    });
    });

      </script>
    </head>
    <body>

    <div id='maplegend' class='maplegend' 
        style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
         border-radius:5px; padding: 1px; font-size:12px; right: 3px; bottom: 39px; width: """ + str(width) + """px;'>

    <div class='legend-title'>""" + str(title) + """</div>
    <div class='legend-scale'>
      <ul class='legend-labels'>""" + legend_categories + """    
      </ul>
    </div>
    </div>

    </body>
    </html>

    <style type='text/css'>
      .maplegend .legend-title {
        text-align: center;
        margin-bottom: 0px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 0px;
        padding: 5px;
        float: center;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 14px;
        margin-bottom: 3px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 1px solid #999;
        }
      .maplegend a {
        color: #777;
        }

    </style>
    {% endmacro %}"""

    macro = MacroElement()
    macro._template = Template(template)

    return m.get_root().add_child(macro)


def add_title(folium_map, title, width, color):
    m = folium_map

    template = """
    {% macro html(this, kwargs) %}

    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>jQuery UI Draggable - Default functionality</title>
      <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
      <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
      <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
      <script>
      $( function() {
        $( "#maptitle" ).draggable({
                        start: function (event, ui) {
                            $(this).css({
                                right: "auto",
                                top: "auto",
                                bottom: "auto"
                            });
                        }
                    });
    });

      </script>
    </head>
    <body>

    <div id='maptitle' class='maptitle' 
        style='position: absolute; z-index:9999; border:None; background-color:rgba(255, 255, 255, 0.0);
         border-radius:0px; padding: 0px; font-size:4px; left: 40px; top: 0px; width: """ + str(width) + """px;'>
        <div class='legend-title'>""" + str(title) + """</div>
    </div>
    </body>
    </html>

    <style type='text/css'>
      .maptitle .legend-title {
        text-align: center;
        color:{color};
        margin-bottom: 1px;
        font-weight: bold;
        font-size: 90%;
        }
      .maptitle .legend-scale ul {
        margin: 0;
        margin-bottom: 1px;
        padding: 0;
        float: top;
        list-style: none;
        }

      .maptitle a {
        color: #777;
        }

    </style>
    {% endmacro %}"""

    macrotitle = MacroElement()
    macrotitle._template = Template(template)

    return m.get_root().add_child(macrotitle)