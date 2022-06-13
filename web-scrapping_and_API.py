import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

#Поиск WEB-скреппингом информации про цены на молоко

#WEB-скреппинг магазина Глобус
tovar = []
for j in range(3):
    url = "https://online.globus.ru/catalog/molochnye-produkty-syr-yaytsa/moloko-i-molochnye-produkty/moloko/?PAGEN_1=" + str(
        j + 1)
    driver.get(url)
    products = driver.find_elements(By.CLASS_NAME, value='catalog-section__item__info')
    prices = driver.find_elements(By.CLASS_NAME, value='catalog-section__item-info')
    for i in range(len(products) // 2):
        product = products[2 * i].text.split('\n')
        prices = products[2 * i + 1].text.split('\n')
        if prices[0] == 'Товар временно отсутствует':
            break
        else:
            if product[0] == 'по карте':
                product = product[2:]
            if (product != ['']) and (product[0][len(product[0]) - 1] == '%'):
                product = product[1:]
            if len(product) > 3:
                if len(product) != 1:
                    tovar.append([product[0], int(product[1]) + int(product[2]) / 100])
                if len(prices) != 1:
                    tovar.append([prices[0], int(prices[1]) + int(prices[2]) / 100])
            else:
                if (product != ['']) and (prices != ['']):
                    tovar.append([product[0], int(prices[0]) + int(prices[1]) / 100])
df_globus = pd.DataFrame(tovar, columns=['Tovar', 'Price'])
df_globus.to_csv('globus.csv', index=False)

#WEB-скреппинг магазина ОКЕЙ (был на лекции)
### FROM: лекция
url = "https://www.okeydostavka.ru/msk/molochnye-produkty-syry-iaitso/molochnye-produkty/moloko-i-slivki"
driver.get(url)
products = driver.find_elements(by=By.CSS_SELECTOR, value="div.product")
rows = []
for product in products:
    name = product.find_element(by=By.CSS_SELECTOR, value="div.product-name").text
    span_price = product.find_element(by=By.CSS_SELECTOR, value="span.price")
    price = float(span_price.get_attribute("innerHTML").strip().replace(' ₽', '').replace(',', '.'))
    rows.append([name, price])
df_okay = pd.DataFrame(rows, columns=['Tovar', 'Price'])
df_okay.to_csv('okay.csv', index=False)
### END FROM

#WEB-скреппинг магазина Лента
rows = []
for j in range(4):
    url = "https://lenta.com/catalog/moloko-syr-yajjco/molochnaya-produkciya/moloko/?page=" + str(j + 1)
    driver.get(url)
    tovar = driver.find_elements(by=By.CSS_SELECTOR, value="div.sku-card-small-container")
    for tag in tovar:
        if tag.find_elements(by=By.CSS_SELECTOR, value="div.sku-card-small__not-available-notice") == []:
            name = tag.find_elements(by=By.CSS_SELECTOR, value="div.sku-card-small-header__title")[0].text
            price_int = tag.find_elements(by=By.CSS_SELECTOR, value="span.price-label__integer")[0].text
            price_float = tag.find_elements(by=By.CSS_SELECTOR, value="small.price-label__fraction")[0].text
            rows.append([name, float(price_int + '.' + price_float)])
df_lenta = pd.DataFrame(rows, columns = ['Tovar', 'Price'])
df_lenta.to_csv('lenta.csv', index=False)

#WEB-скреппинг магазина Перекресток
rows = []
url = "https://www.perekrestok.ru/cat/c/114/moloko"
driver.get(url)
tovar = driver.find_elements(by=By.CSS_SELECTOR, value=".product-card__content")
for tag in tovar:
    name = tag.find_elements(by=By.CSS_SELECTOR, value="div.product-card-title__wrapper div")[0].text
    price = tag.find_elements(by=By.CSS_SELECTOR, value="div.product-card__pricing")[0].text
    print(name, float(price[:len(price)-5].replace(',', '.')))
    rows.append([name, float(price[:len(price)-5].replace(',', '.'))])
df_perekrestok = pd.DataFrame(rows, columns=['Tovar', 'Price'])
df_perekrestok.to_csv('perekrestok.csv', index=False)

#WEB-скреппинг магазина Metro
rows = []
for i in range(3):
    url = "https://online.metro-cc.ru/category/molochnye-prodkuty-syry-i-yayca/moloko?page=" + str(i + 1) + "&in_stock=1&eshop_order=1"
    driver.get(url)
    tovar = driver.find_elements(by=By.CSS_SELECTOR, value="div.catalog div.catalog-item__block")
    for tag in tovar:
        name = tag.find_elements(by=By.CSS_SELECTOR, value="a.catalog-item_name")[0].text
        price = tag.find_elements(by=By.CSS_SELECTOR, value="div.catalog-item_price-lvl_current")[0].text
        if (price == ''):
            price = tag.find_elements(by=By.CSS_SELECTOR, value="div.catalog-item_price-current")[0].text
        rows.append([name, float(price[:len(price) - 7])])
df_metro = pd.DataFrame(rows, columns=['Tovar', 'Price'])
df_metro.to_csv('metro.csv', index=False)


#Поиск адресов магазинов в Москве у Metro
url = "https://www.metro-cc.ru/torgovye-centry#store-locator_g=55.755826|37.6173&store-locator_o=Distance%2CAscending&store-locator_a=%D0%BC%D0%BE%D1%81%D0%BA%D0%B2%D0%B0"
driver.get(url)
tovary = driver.find_elements(by=By.CSS_SELECTOR, value="div.sl-result-body")
data = []
for tag in tovary:
    liss = tag.text.split('\n')
    if len(liss) > 2:
        liss[1] = liss[1] + liss[2]
    data.append([liss[1], 0.0, 0.0])
df_adresses_metro = pd.DataFrame(data, columns = ['Адрес', 'Широта', 'Долгота'])
#При помощи API Nominatim ищем координаты магазинов
for i in range(len(df_adresses_metro['Адрес'])):
    addres = df_adresses_metro['Адрес']
    entrypoint = "https://nominatim.openstreetmap.org/search"
    params = {'q': addres[i],
              'format': 'geojson'}
    r = requests.get(entrypoint, params=params)
    data = r.json()['features']
    if data != []:
        df_adresses_metro['Широта'][i] = float(data[0]['geometry']['coordinates'][0])
        df_adresses_metro['Долгота'][i] = float(data[0]['geometry']['coordinates'][1])
df_adresses_metro.to_csv('df_adress_metro.csv', index=False)


#Поиск адресов магазинов в Москве у Глобус
url = "https://www.globus.ru/stores/#list"
driver.get(url)
tovary = driver.find_elements(by=By.CSS_SELECTOR, value="div.address2 p")
data = []
for tag in tovary:
    liss = tag.text
    data.append([liss, 0.0, 0.0])
df_adresses_globus = pd.DataFrame(data, columns = ['Адрес', 'Широта', 'Долгота'])

#При помощи API Nominatim ищем координаты магазинов
for i in range(len(df_adresses_globus['Адрес'])):
    addres = df_adresses_globus['Адрес']
    entrypoint = "https://nominatim.openstreetmap.org/search"
    params = {'q': addres[i],
              'format': 'geojson'}
    r = requests.get(entrypoint, params=params)
    data = r.json()['features']
    if data != []:
        df_adresses_globus['Широта'][i] = float(data[0]['geometry']['coordinates'][0])
        df_adresses_globus['Долгота'][i] = float(data[0]['geometry']['coordinates'][1])
df_adresses_globus.to_csv('df_adress_globus.csv', index=False)


#Поиск адресов магазинов в Москве у Лента
url = "https://lenta.com/allmarkets/"
driver.get(url)
tovary = driver.find_elements(by=By.CSS_SELECTOR, value=".stores__column a")
data = []
for tag in tovary:
    liss = tag.text
    data.append([liss, 0.0, 0.0])
df_adresses_lenta = pd.DataFrame(data, columns = ['Адрес', 'Широта', 'Долгота'])

#При помощи API Nominatim ищем координаты магазинов
for i in range(len(df_adresses_lenta['Адрес'])):
    addres = df_adresses_lenta['Адрес']
    entrypoint = "https://nominatim.openstreetmap.org/search"
    params = {'q': addres[i],
              'format': 'geojson'}
    r = requests.get(entrypoint, params=params)
    data = r.json()['features']
    if data != []:
        df_adresses_lenta['Широта'][i] = float(data[0]['geometry']['coordinates'][0])
        df_adresses_lenta['Долгота'][i] = float(data[0]['geometry']['coordinates'][1])
df_adresses_lenta.to_csv('df_adress_lenta.csv', index=False)


#Поиск адресов магазинов в Москве у Окей
url = "https://www.be-in.ru/network/7957-okej-address/moskva/#anchor-store-locations"
driver.get(url)
tovary = driver.find_elements(by=By.CSS_SELECTOR, value="a.text-block span.text-block")
data = []
for tag in tovary:
    liss = tag.text.split('\n')[0][7:]
    print(liss)
    print()
    data.append([liss, 0.0, 0.0])
df_adresses_okay = pd.DataFrame(data, columns = ['Адрес', 'Широта', 'Долгота'])

#При помощи API Nominatim ищем координаты магазинов
for i in range(len(df_adresses_okay['Адрес'])):
    addres = df_adresses_okay['Адрес']
    entrypoint = "https://nominatim.openstreetmap.org/search"
    params = {'q': addres[i],
              'format': 'geojson'}
    r = requests.get(entrypoint, params=params)
    data = r.json()['features']
    if data != []:
        df_adresses_okay['Широта'][i] = float(data[0]['geometry']['coordinates'][0])
        df_adresses_okay['Долгота'][i] = float(data[0]['geometry']['coordinates'][1])
df_adresses_okay.to_csv('df_adresses_okay.csv', index=False)


#Поиск адресов магазинов в Москве у Перекресток
url = "https://www.vprok.ru/shops"
driver.get(url)
tovary = driver.find_elements(by=By.CSS_SELECTOR, value="span.xf-shops-list__address-text")
data = []
for tag in tovary:
    liss = tag.text
    data.append([liss, 0.0, 0.0])
df_adresses_perekrestok = pd.DataFrame(data, columns=['Адрес', 'Широта', 'Долгота'])

#При помощи API Nominatim ищем координаты магазинов
for i in range(len(df_adresses_perekrestok['Адрес'])):
    addres = df_adresses_perekrestok['Адрес']
    entrypoint = "https://nominatim.openstreetmap.org/search"
    params = {'q': addres[i],
              'format': 'geojson'}
    r = requests.get(entrypoint, params=params)
    data = r.json()['features']
    if data != []:
        df_adresses_perekrestok['Широта'][i] = float(data[0]['geometry']['coordinates'][0])
        df_adresses_perekrestok['Долгота'][i] = float(data[0]['geometry']['coordinates'][1])
df_adresses_perekrestok.to_csv('df_addresses_perekrestok.csv', index=False)


