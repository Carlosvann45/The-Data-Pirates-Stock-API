from flask import *
import datetime
import asyncio
import aiohttp
from bs4 import BeautifulSoup, SoupStrainer
from openpyxl import load_workbook
from urllib3.connectionpool import xrange

app = Flask(__name__)
tickers_workbook = load_workbook('YahooTickerSymbols.xlsx')
stock_sheet = tickers_workbook['Stock']


@app.route('/stock/tickers/all', methods=['GET'])
def get_all_stocks():
    column1 = stock_sheet['A']
    column2 = stock_sheet['B']
    symbol_objects = []

    for x in xrange(len(column1)):
        if column1[x].value and column2[x].value and column1[x].value != 'Yahoo Stock Tickers' and column1[x].value != 'Ticker':
            symbol_objects.append({
                'Name': column2[x].value,
                'Symbol': column1[x].value
            })

    return jsonify(symbol_objects), 200


@app.route('/stock/data/quote', methods=['GET'])
def get_stock_prices():
    symbols = request.args.get('symbols', '')

    if symbols == '':
        return jsonify(create_error_message(400, 'At least one symbol is required.')), 400

    symbols = symbols.split(',')

    try:
        data = asyncio.run(get_symbols(symbols))
    except Exception as err:
        return jsonify(create_error_message(400, err)), 400

    return jsonify(data), 200


async def get_page(client_session, url):
    async with client_session.get(url) as r:
        return await r.text()


async def get_all(client_session, symbols):
    new_tasks = []

    for symbol in symbols:
        url = f'https://finance.yahoo.com/quote/{symbol}'
        task = asyncio.create_task(get_page(client_session, url))
        new_tasks.append(task)

    results = await asyncio.gather(*new_tasks)

    return results


async def get_symbols(symbols):
    quote_array = []

    async with aiohttp.ClientSession() as client_session:
        data = await get_all(client_session, symbols)

        i = 0

        for html in data:
            soup = BeautifulSoup(html, 'html.parser')

            try:
                price = soup.find('fin-streamer', {'class': 'Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
            except Exception as err:
                raise Exception(f"Symbol with name: {symbols[i]} does not exist.")

            if price == '':
                raise Exception(f"Symbol with name: {symbols[i]} does not exist.")
            else:
                quote_array.append({
                    'symbol': symbols[i],
                    'price': price
                })

            i += 1

    return quote_array


def create_error_message(error_code, error_message):
    return {
        'timestamp': datetime.datetime.now(),
        'error': error_code,
        'errorMessage': error_message
    }


if __name__ == '__main__':
    app.run(debug=True)
