import requests
from xml.etree import ElementTree
import mysql.connector

# URL для SOAP-запроса
url = "http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?op=FullCountryInfoAllCountries"

# Структурированный XML
payload = """<?xml version="1.0" encoding="utf-8"?>
            <soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
            <soap12:Body>
                <FullCountryInfoAllCountries xmlns="http://www.oorsprong.org/websamples.countryinfo">
                </FullCountryInfoAllCountries>
            </soap12:Body>
            </soap12:Envelope>"""

# Заголовки
headers = {
    'Content-Type': 'text/xml; charset=utf-8'
}

# Выполнение POST-запроса
response = requests.request("POST", url, headers=headers, data=payload)


response_xml = response.text.replace('soap:', '').replace('m:', '')
print(response_xml)
xml_text = ElementTree.fromstring(response_xml)
countries = xml_text.findall('.//tCountryInfo')

# Подключение к базе данных MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password=''
)

# Создание пользователя с полным доступом
cursor = conn.cursor()
cursor.execute("CREATE USER IF NOT EXISTS 'dbcountries'@'localhost' IDENTIFIED BY 'dbcountries'")
cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'dbcountries'@'localhost' WITH GRANT OPTION")
cursor.execute("FLUSH PRIVILEGES")

cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS dbcountries")

# Использование базы данных dbcountries
cursor.execute("USE dbcountries")   

# Создание таблицы, если она не существует
cursor.execute('''CREATE TABLE IF NOT EXISTS countries (
                    iso_code VARCHAR(255),
                    name VARCHAR(255),
                    capital VARCHAR(255),
                    phone_code VARCHAR(255),
                    continent_code VARCHAR(255),
                    currency_iso_code VARCHAR(255),
                    country_flag VARCHAR(255)
                )''')

# Запись данных о странах в таблицу
for country in countries:
    iso_code = country.find('.//sISOCode').text
    name = country.find('.//sName').text
    capital = country.find('.//sCapitalCity').text
    phone_code = country.find('.//sPhoneCode').text
    continent_code = country.find('.//sContinentCode').text
    currency_iso_code = country.find('.//sCurrencyISOCode').text
    country_flag = country.find('.//sCountryFlag').text

    cursor.execute("INSERT INTO countries (iso_code, name, capital, phone_code, continent_code, currency_iso_code, country_flag) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (iso_code, name, capital, phone_code, continent_code, currency_iso_code, country_flag))

# Фиксация изменений и закрытие соединения с базой данных
conn.commit()
conn.close()
