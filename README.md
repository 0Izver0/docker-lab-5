# Конвертер валют (Docker, Python)

Практична робота №5, варіант 3. Підтримує USD, EUR, UAH, GBP з фіксованими курсами.

## Docker
    docker build -t currency-converter .
    docker run --rm -e AMOUNT=100 -e FROM=USD -e TO=EUR currency-converter
    docker run --rm -e AMOUNT=2500 -e FROM=UAH -e TO=ALL currency-converter

`TO=ALL` переводить суму в усі інші валюти. Некоректний вхід: повідомлення в stderr і код 2.