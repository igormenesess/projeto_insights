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
    # Criando pre??o por ??rea no dataset
    df['price_sqft'] = df['price'] / df['sqft_living']

    # Criando esta????es do ano no dataset
    df['season'] = df['date'].apply(return_season)

    # considerar imoveis dos ultimos 20 anos como atuais
    year_base = pd.to_datetime(df['yr_built'].max().year - 20, format='%Y')
    df['new'] = df.apply(lambda x: 'Sim' if x['yr_built'] > year_base or x['yr_renovated'] > year_base else 'N??o',
                         axis=1)

    df['year'] = df['date'].apply(lambda x: x.year)

    return df


# Load
def inicial_settings(filename):
    st.title('Projeto de Insights')
    st.subheader('https://github.com/igormenesess')
    st.header('Leitura de Dados')
    st.markdown('Essa ?? uma amostra dos dados que ser??o utilizados.')
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
    st.markdown('Essas s??o as estatiticas descritivas dos dados n??mericos,')
    st.dataframe(df_estatistical)

    return df


def create_map(df):
    st.sidebar.title('Visualiza????o do Mapa')
    st.sidebar.write('Filtro para visualiza????o dos im??veis no Mapa')
    f_price = st.sidebar.select_slider('Pre??o $:', df['price'].sort_values(), (df['price'].min(), df['price'].max()))
    f_bedrooms = st.sidebar.multiselect('N??mero de Quartos:', df['bedrooms'].sort_values().unique())
    f_bathrooms = st.sidebar.multiselect('N??mero de Banheiros:', df['bathrooms'].sort_values().unique())
    f_waterfront = st.sidebar.selectbox('Vista para ??gua:', ('Selecionar', 'Sim', 'N??o'))
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
    st.header('Mapa dos Im??veis')
    if st.checkbox('Mostrar Mapa'):
        try:
            st.subheader('Vis??o geral dos im??veis selecionados')
            density_map = folium.Map(location=[df['lat'].mean(), df['long'].mean()], default_zoom_start=20)
            marker_cluster = MarkerCluster().add_to(density_map)
            for name, row in df.iterrows():
                folium.Marker([row['lat'], row['long']],
                              popup='Pre??o: ${0}, Tamanho: {1} sqft, {2} Quartos, '
                                    '{3} Banheiros, Constru??do em: {4}'.format(
                                  row['price'],
                                  row['sqft_living'],
                                  row['bedrooms'],
                                  row['bathrooms'],
                                  row['yr_built'].year)).add_to(marker_cluster)
            folium_static(density_map)
        except:
            st.write('N??o existem im??veis para a sele????o indicada.')

    return None


def insights(df):
    st.header('Hip??tese 1: Os im??veis com mais quartos tem o pre??o maior.')
    st.markdown('Os dados foram agrupados em rela????o ao numero de quartos:')
    df1 = df[['price', 'price_sqft', 'bedrooms']].groupby('bedrooms').mean()
    df2 = df[['price_sqft', 'bedrooms']].groupby('bedrooms').count()
    df_bedrooms = pd.concat([df1, df2], axis=1, join='inner').reset_index()
    df_bedrooms.columns = ['bedrooms', 'mean_price', 'mean_price_sqft', 'count']
    st.dataframe(df_bedrooms)
    fig1 = px.bar(df_bedrooms, x='bedrooms', y='mean_price_sqft',
                  labels={'bedrooms': 'Quartos', 'mean_price_sqft': 'Pre??o por ??rea M??dio'})
    st.plotly_chart(fig1)
    st.markdown('Os im??veis com mais quartos n??o possuem o pre??o maior')

    st.header('Hip??tese 2:  Os im??veis com vista para ??gua s??o mais caros.')
    st.markdown('Os dados foram agrupados em rela????o aos im??veis que possuem ou n??o vista para agua:')
    df_waterfront = df[['price', 'price_sqft', 'waterfront']].groupby('waterfront').mean().reset_index()
    df_waterfront['waterfront'] = ['N??o', 'Sim']
    st.dataframe(df_waterfront)
    price_variation = round(
        100 * (df_waterfront['price_sqft'][1] - df_waterfront['price_sqft'][0]) / df_waterfront['price_sqft'][0], 2)
    st.markdown(f'Os imoveis com vista para agua s??o em m??dia {price_variation}% mais caros')

    st.header('Hip??tese 3: O ver??o ?? a melhor ??poca do ano para se vender im??veis.')
    st.markdown('Os dados foram agrupados em rela????o a esta????o do ano:')
    df_season = df[['season', 'price', 'price_sqft']].groupby('season').mean().reset_index()
    st.dataframe(df_season)
    fig2 = px.bar(df_season, x='season', y='price_sqft',
                  labels={'season': 'Esta????o do Ano', 'price_sqft': 'Pre??o por ??rea M??dio'})
    st.plotly_chart(fig2)
    st.markdown('N??o foram observadas varia????es significativas no pre??o em reala????o a ??poca do Ano')

    st.header('Hip??tese 4: Os imoveis mais atuais ou reformados recentemente s??o mais caros.')
    st.markdown('Os dados foram agrupados em rela????o aos im??veis considerados novos:')
    df_new = df[['new', 'price', 'price_sqft']].groupby('new').mean().reset_index()
    st.dataframe(df_new)
    st.markdown('N??o houve varia????o significativa no pre??o dos im??veis.')

    st.header('Hip??tese 5: Im??veis com melhores condi????es tem pre??os maiores.')
    st.markdown('Os dados foram agrupados em rela????o as condi????es dos im??veis:')
    df_grouped = df[['condition', 'price', 'price_sqft']].groupby('condition')
    df_condition = pd.concat([df_grouped.mean(), df_grouped.count().drop('price_sqft', axis=1)], axis=1).reset_index()
    df_condition.columns = ['condition', 'price', 'price_sqft', 'count']
    st.dataframe(df_condition)
    fig3 = px.bar(df_condition, x='condition', y='price_sqft',
                  labels={'condition': 'Condi????o', 'price_sqft': 'Pre??o por ??rea M??dio'})
    st.plotly_chart(fig3)
    st.markdown('Os im??veis com melhores condi????es s??o mais caros,'
                ' excluindo os im??veis da condi????o 1 que possuem uma baixa amostragem')
    return None


def recomendation(df):
    st.title('Recomenda????es de Compra')
    st.markdown('Ser??o feitas recomenda????es de compra de im??veis em boas condi????es, '
                'com vista para ??gua e com o pre??o at?? 30% acima do pre??o m??dio. '
                'A recomenda????o de venda ser?? pelo pre??o m??dio mais um desvio padr??o.')
    df['buy'] = df.apply(lambda x: 'Sim' if x['condition'] >= 4 and 1 == x['waterfront'] and
                                            x['price_sqft'] < 1.3 * df['price_sqft'].mean() else 'N??o',
                         axis=1)
    df_buy = df[['id', 'zipcode', 'condition', 'price', 'sqft_living', 'price_sqft', 'buy']]
    df_buy['selling_price'] = (df['price_sqft'].mean() + df['price_sqft'].std()) * df_buy['sqft_living']
    df_buy['profit'] = df_buy['selling_price'] - df_buy['price']
    st.dataframe(df_buy[df['buy'] == 'Sim'].reset_index().drop('buy', axis=1))
    total_profit = df_buy[df['buy'] == 'Sim']['profit'].sum()
    st.markdown(f'O lucro total obtido com esta lista de recomenda????es ?? de $ {total_profit:,.2f}')
    return None


if __name__ == '__main__':
    st.set_page_config(layout='wide')
    data = inicial_settings('kc_house_data.csv')
    create_map(data)
    insights(data)
    recomendation(data)
