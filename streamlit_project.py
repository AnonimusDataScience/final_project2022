import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px
import werkzeug
from selenium.webdriver.common.by import By

werkzeug.cached_property = werkzeug.utils.cached_property
from robobrowser import RoboBrowser

with st.echo(code_location='below'):
     st.title('Итоговый проект по курсу Data Science')
     """В данном проекте сделан сбор данных о ценах на молочную продукцию (в основном товар "молоко") в пяи основных супермаркетах Москвы: Глобус, Окей, Лента, Metro и Перекресток. Приведено сравнение цен в разных супермаркетах, их магазины и расположение в Москве и соседних округах, а также предскажания относительно того, как на цены на молоко влияет количество магазинов в сети и количество предложенной молочной продукциию"""



     col1, col2, col3 = st.columns(3)
     with col1:
          st.header('"Globus"')
          df_globus = pd.read_csv('globus.csv')
          df_globus
     with col2:
          st.header('"Okay"')
          df_okay = pd.read_csv('okay.csv')
          df_okay
     with col3:
          st.header('"Lenta"')
          df_lenta = pd.read_csv('lenta.csv')
          df_lenta
     col4, col5 = st.columns(2)
     with col4:
          st.header('"Metro"')
          df_metro = pd.read_csv('metro.csv')
          df_metro
     with col5:
          st.header('"Perekrestok"')
          df_perekrestok = pd.read_csv('perekrestok.csv')
          df_perekrestok

     """
     Для сбора данных был сделан отдельный файл, который называется web-scrapping_and_API.py (его можно найти в той же директории на GitHub, где и сам проект).
     
     Теперь при помощи средств Srtreamlit и библиотеки seaborn построим гистограмму, отражающую распределение цен в выбораных вами магазинах.
     """
     options = st.multiselect(
          'Какие магазины вы бы хотели рассмотреть',
          ['Перекресток', 'Окей', 'Лента', 'Metro', 'Глобус'])

     df_perekrestok['Place'] = 'Перекресток'
     df_okay['Place'] = 'Окей'
     df_metro['Place'] = 'Metro'
     df_lenta['Place'] = 'Лента'
     df_globus['Place'] = 'Глобус'

     df = pd.concat([df_perekrestok, df_globus, df_okay, df_metro, df_lenta])
     df_selection = pd.DataFrame([], columns=['Tovar', 'Price', 'Place'])
     for option in options:
          df_selection = pd.concat([df[df['Place'] == option], df_selection])

     df = px.data.tips()
     fig = px.histogram(df_selection, x="Price", color="Place", marginal="rug",  # can be `box`, `violin`
                        hover_data=df_selection.columns, nbins=120)
     st.plotly_chart(fig, use_container_width=True)

     """
     Мы можем также посчитать среднее значение цены в каждом магазине и посмотреть на его корреляцию с количеством магазинов в сети.
     """

     df_addresses_perek = pd.read_csv('df_adress_perekrestok.csv')
     df_addresses_metro = pd.read_csv('df_adress_metro.csv')
     df_addresses_lenta = pd.read_csv('df_adress_lenta.csv')
     df_addresses_okay = pd.read_csv('df_adress_okay.csv')
     df_addresses_globus = pd.read_csv('df_adress_globus.csv')

     df_mean = pd.DataFrame([[int(df_perekrestok['Price'].mean()), len(df_addresses_perek), 'Перекресток'],
                            [int(df_globus['Price'].mean()), len(df_addresses_globus), 'Глобус'],
                            [int(df_lenta['Price'].mean()), len(df_addresses_lenta), 'Лента'],
                            [int(df_okay['Price'].mean()), len(df_addresses_okay), 'Окей'],
                            [int(df_metro['Price'].mean()), len(df_addresses_metro), 'Metro']],
                            columns=['Средняя цена', "Количество магазинов", 'Название'])
     df_mean
     points = alt.Chart(df_mean).mark_point().encode(
          x='Количество магазинов:Q',
          y='Средняя цена:Q',
          color='Количество магазинов:Q'
     )
     text = points.mark_text(
          align='right',
          baseline='top',
          dx=9
     ).encode(
          text='Название'
     )
     st.altair_chart(points + text, use_container_width=True)


     """
     Теперь, пусть данных и мало, попробуем предсказать, сколько будет средняя цена для сети с определенным количеством магазинов. Для этого исполдьзуем библиотеку sklearn и из нее воспользуемся линейной регрессией:
     
     Имеющиеся данные:
     """
     fig, ax = plt.subplots()
     df_mean.plot.scatter(x="Количество магазинов", y="Средняя цена", ax=ax)
     st.pyplot(fig)

     model = LinearRegression()
     model.fit(df_mean[["Количество магазинов"]], df_mean["Средняя цена"])
     """
     редсказывающая модель:
     """
     fig, ax = plt.subplots()
     df_mean.plot.scatter(x="Количество магазинов", y="Средняя цена", ax=ax)
     x = pd.DataFrame(np.linspace(0, 447))
     x.columns = ['Количество магазинов']
     plt.plot(x["Количество магазинов"], model.predict(x), color="C1", lw=2)
     st.pyplot(fig)

     a = st.number_input('Введите предполагаемое количество магазинов:')
     pr_a = int(model.predict(pd.DataFrame([a], columns=["Средняя цена"])))
     st.text('Ваше предсказание - это ' + str(pr_a) + ' магазинов')



