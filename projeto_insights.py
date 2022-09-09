# Imports
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster


# Extract
@st.cache(allow_output_mutation=True)
def get_data(file):
    df = pd.read_csv(file)
    np.set_printoptions(suppress=True)
    pd.set_option('display.float_format', '{:.2f}'.format)
    return df


# Transform
def convert_date(df):
    df['date'] = pd.to_datetime(df['date'])
    df['yr_built'] = pd.to_datetime(df['yr_built'], format='%Y')
    df['yr_renovated'] = df['yr_renovated'].apply(lambda x: None if x == 0 else x)
    df['yr_renovated'] = pd.to_datetime(df['yr_renovated'], format='%Y')
    return df


def clean_data(df):
    # Eliminando valor de 33 banheiros que provavelmente esta errado
    df = df.drop(list(df[df['bedrooms'] == 33].index))

    # Eliminando valores de id duplicados mantendo os mais atuais
    df_duplicated = df[df['id'].duplicated(keep=False)].sort_values('id').reset_index()
    index_excluidos = []
    id_date_index = []
    for i, row in df_duplicated.iterrows():
        if i == 0:
            id_date_index = [row['id'], row['date'], row['index']]
        else:
            if id_date_index[0] == row['id']:
                if id_date_index[1] > row['date']:
                    index_excluidos.append(row['index'])
                else:
                    index_excluidos.append(id_date_index[2])
                    id_date_index = [row['id'], row['date'], row['index']]
            else:
                id_date_index = [row['id'], row['date'], row['index']]
    df = df.drop(index_excluidos)
    return df


# Funcao para escolher as estacoes a partir da data
def return_season(date):
    if '03-20' <= date.strftime('%m-%d') <= '06-20':
        return 'Spring'
    if '06-21' <= date.strftime('%m-%d') <= '09-21':
        return 'Summer'
    if '09-22' <= date.strftime('%m-%d') <= '12-20':
        return 'Fall'
    else:
        return 'Winter'


def create_variables(df):
    # Criando preço por área no dataset
    df['price_sqft'] = df['price'] / df['sqft_living']

    # Criando estações do ano no dataset
    df['season'] = df['date'].apply(return_season)

    # considerar imoveis dos ultimos 20 anos como atuais
    year_base = pd.to_datetime(df['yr_built'].max().year - 20, format='%Y')
    df['new'] = df.apply(lambda x: 'Sim' if x['yr_built'] > year_base or x['yr_renovated'] > year_base else 'Não',
                         axis=1)

    df['year'] = df['date'].apply(lambda x: x.year)

    return df


# Load
def inicial_settings(filename):
    st.title('Projeto de Insights')
    st.subheader('https://github.com/igormenesess')
    st.header('Leitura de Dados')
    st.markdown('Essa é uma amostra dos dados que serão utilizados.')
    df = create_variables(clean_data(convert_date(get_data(filename))))
    st.dataframe(df.head(10))

    df_numeric = df.select_dtypes(include=[int, float]).drop(
        ['id', 'zipcode', 'lat', 'long', 'waterfront', 'view', 'condition', 'grade'], axis=1)
    mean = pd.DataFrame(df_numeric.apply(np.mean)).T
    std = pd.DataFrame(df_numeric.apply(np.std)).T
    median = pd.DataFrame(df_numeric.apply(np.median)).T
    minimum = pd.DataFrame(df_numeric.apply(np.min)).T
    maximum = pd.DataFrame(df_numeric.apply(np.max)).T
    range_ = pd.DataFrame(df_numeric.apply(lambda x: np.max(x) - np.min(x))).T
    df_estatistical = pd.concat([mean, std, median, minimum, maximum, range_]).T
    df_estatistical.columns = ['Mean', 'Std', 'Median', 'Min', 'Max', 'Range']
    st.markdown('Essas são as estatiticas descritivas dos dados númericos,')
    st.dataframe(df_estatistical)

    return df


def create_map(df):
    st.sidebar.title('Visualização do Mapa')
    st.sidebar.write('Filtro para visualização dos imóveis no Mapa')
    f_price = st.sidebar.select_slider('Preço $:', df['price'].sort_values(), (df['price'].min(), df['price'].max()))
    f_bedrooms = st.sidebar.multiselect('Número de Quartos:', df['bedrooms'].sort_values().unique())
    f_bathrooms = st.sidebar.multiselect('Número de Banheiros:', df['bathrooms'].sort_values().unique())
    f_waterfront = st.sidebar.selectbox('Vista para Água:', ('Selecionar', 'Sim', 'Não'))
    price_condition = (f_price[0] < df['price']) & (df['price'] < f_price[1])
    if len(f_bathrooms) == 0:
        bath_condition = True
    else:
        bath_condition = df['bathrooms'].isin(f_bathrooms)
    if len(f_bedrooms) == 0:
        bed_condition = True
    else:
        bed_condition = df['bedrooms'].isin(f_bedrooms)
    if f_waterfront == 'Selecionar':
        water_condition = True
    elif f_waterfront == 'Sim':
        water_condition = df['waterfront'] == 1
    else:
        water_condition = df['waterfront'] == 0
    df = df[price_condition & bath_condition & bed_condition & water_condition]
    st.header('Mapa dos Imóveis')
    if st.checkbox('Mostrar Mapa'):
        try:
            st.subheader('Visão geral dos imóveis selecionados')
            density_map = folium.Map(location=[df['lat'].mean(), df['long'].mean()], default_zoom_start=20)
            marker_cluster = MarkerCluster().add_to(density_map)
            for name, row in df.iterrows():
                folium.Marker([row['lat'], row['long']],
                              popup='Preço: ${0}, Tamanho: {1} sqft, {2} Quartos, '
                                    '{3} Banheiros, Construído em: {4}'.format(
                                  row['price'],
                                  row['sqft_living'],
                                  row['bedrooms'],
                                  row['bathrooms'],
                                  row['yr_built'].year)).add_to(marker_cluster)
            folium_static(density_map)
        except:
            st.write('Não existem imóveis para a seleção indicada.')

    return None


def insights(df):
    st.header('Hipótese 1: Os imóveis com mais quartos tem o preço maior.')
    st.markdown('Os dados foram agrupados em relação ao numero de quartos:')
    df1 = df[['price', 'price_sqft', 'bedrooms']].groupby('bedrooms').mean()
    df2 = df[['price_sqft', 'bedrooms']].groupby('bedrooms').count()
    df_bedrooms = pd.concat([df1, df2], axis=1, join='inner').reset_index()
    df_bedrooms.columns = ['bedrooms', 'mean_price', 'mean_price_sqft', 'count']
    st.dataframe(df_bedrooms)
    fig1 = px.bar(df_bedrooms, x='bedrooms', y='mean_price_sqft',
                  labels={'bedrooms': 'Quartos', 'mean_price_sqft': 'Preço por Área Médio'})
    st.plotly_chart(fig1)
    st.markdown('Os imóveis com mais quartos não possuem o preço maior')

    st.header('Hipótese 2:  Os imóveis com vista para água são mais caros.')
    st.markdown('Os dados foram agrupados em relação aos imóveis que possuem ou não vista para agua:')
    df_waterfront = df[['price', 'price_sqft', 'waterfront']].groupby('waterfront').mean().reset_index()
    df_waterfront['waterfront'] = ['Não', 'Sim']
    st.dataframe(df_waterfront)
    price_variation = round(
        100 * (df_waterfront['price_sqft'][1] - df_waterfront['price_sqft'][0]) / df_waterfront['price_sqft'][0], 2)
    st.markdown(f'Os imoveis com vista para agua são em média {price_variation}% mais caros')

    st.header('Hipótese 3: O verão é a melhor época do ano para se vender imóveis.')
    st.markdown('Os dados foram agrupados em relação a estação do ano:')
    df_season = df[['season', 'price', 'price_sqft']].groupby('season').mean().reset_index()
    st.dataframe(df_season)
    fig2 = px.bar(df_season, x='season', y='price_sqft',
                  labels={'season': 'Estação do Ano', 'price_sqft': 'Preço por Área Médio'})
    st.plotly_chart(fig2)
    st.markdown('Não foram observadas variações significativas no preço em realação a Época do Ano')

    st.header('Hipótese 4: Os imoveis mais atuais ou reformados recentemente são mais caros.')
    st.markdown('Os dados foram agrupados em relação aos imóveis considerados novos:')
    df_new = df[['new', 'price', 'price_sqft']].groupby('new').mean().reset_index()
    st.dataframe(df_new)
    st.markdown('Não houve variação significativa no preço dos imóveis.')

    st.header('Hipótese 5: Imóveis com melhores condições tem preços maiores.')
    st.markdown('Os dados foram agrupados em relação as condições dos imóveis:')
    df_grouped = df[['condition', 'price', 'price_sqft']].groupby('condition')
    df_condition = pd.concat([df_grouped.mean(), df_grouped.count().drop('price_sqft', axis=1)], axis=1).reset_index()
    df_condition.columns = ['condition', 'price', 'price_sqft', 'count']
    st.dataframe(df_condition)
    fig3 = px.bar(df_condition, x='condition', y='price_sqft',
                  labels={'condition': 'Condição', 'price_sqft': 'Preço por Área Médio'})
    st.plotly_chart(fig3)
    st.markdown('Os imóveis com melhores condições são mais caros,'
                ' excluindo os imóveis da condição 1 que possuem uma baixa amostragem')
    return None


def recomendation(df):
    st.title('Recomendações de Compra')
    st.markdown('Serão feitas recomendações de compra de imóveis em boas condições, '
                'com vista para água e com o preço até 30% acima do preço médio. '
                'A recomendação de venda será pelo preço médio mais um desvio padrão.')
    df['buy'] = df.apply(lambda x: 'Sim' if x['condition'] >= 4 and 1 == x['waterfront'] and
                                            x['price_sqft'] < 1.3 * df['price_sqft'].mean() else 'Não',
                         axis=1)
    df_buy = df[['id', 'zipcode', 'condition', 'price', 'sqft_living', 'price_sqft', 'buy']]
    df_buy['selling_price'] = (df['price_sqft'].mean() + df['price_sqft'].std()) * df_buy['sqft_living']
    df_buy['profit'] = df_buy['selling_price'] - df_buy['price']
    st.dataframe(df_buy[df['buy'] == 'Sim'].reset_index().drop('buy', axis=1))
    total_profit = df_buy[df['buy'] == 'Sim']['profit'].sum()
    st.markdown(f'O lucro total obtido com esta lista de recomendações é de $ {total_profit:,.2f}')
    return None


if __name__ == '__main__':
    st.set_page_config(layout='wide')
    data = inicial_settings('kc_house_data.csv')
    create_map(data)
    insights(data)
    recomendation(data)
