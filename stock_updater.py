import datetime
import urllib.request
import time

def stock_updater(tickers:list, date:tuple, interval:str='1mo', use_col:str='Adj Close', file:str='stocks.csv'):
    global download_counter
    download_counter = 1
    print('Start downloading.....')
    start = convert_date(date[0])
    end = convert_date(date[1])
    date = (start,end)
    data, title, index = data_merger(tickers,date,interval,use_col)
    data_saver(data,title,index,file)
    print(f'<{len(title)}> stocks stored in <{file}>. Data:<{use_col}>')
    
def data_merger(tickers:list,date:tuple,interval:str,use_col:str='Adj Close'):
    data,loaded_tickers,index = [], [], []
    counter = 1
    for ticker in tickers:
        while True:
            if counter % 10 == 0:
                print(f'Reaching max downloading number, waiting......')
                time.sleep(1)
            counter += 1
            try:
                stock = get_data(ticker,date,interval,use_col)   # stock is a tuple (data,title,index)
                if stock == None:
                    break
                data.append(stock[0])
                loaded_tickers.append(ticker)
                if tickers.index(ticker) == len(tickers) - 1:
                    index = stock[2]
                break
            except Exception as e:
                print(e)
                print(f'Error ocurred during downloading <{ticker}>')
    return data, loaded_tickers, index

def data_saver(data:list,title:list,index:list,file:str):
    max_length = len(index)
    for i in range(len(data)):
        while len(data[i]) < max_length:
            data[i].append(None)
    f = open(file,'w')
    if len(title) > 1:
        f.write('date'+','+','.join(title)+'\n')
    elif len(title) == 1:
        f.write('date'+','+title[0]+'\n')
    else:
        print(f'No data to save.')
        quit()
    for i in range(len(index)):
        f.write(str(index[i])+','+','.join([str(value[i]) for value in data])+'\n')

def convert_date(date:str) -> str:
    return datetime.datetime.strptime(date,'%Y-%m-%d')

def get_data(ticker:str,date:tuple,interval:str,use_col:str='Adj Close'):
    global download_counter
    data, title, index = [],[],[]
    try:
        time.sleep(0.1) # avoid overly frequent requests
        content = get_stock_data(ticker,date,interval)
        temp = content.split('\n')
        title = [s.strip() for s in temp[0].split(',')]
        col_index = title.index(use_col)
        for row in temp[1:]:
            row = [s.strip() for s in row.split(',')]
            index.append(row[0])
            if row[col_index] != 'null':
                data.append(row[col_index])
            else:
                data.append(None)
        print(f'No.<{download_counter}>, {ticker} downloaded.')
        download_counter += 1
        return data,title[col_index],index
    except Exception as e:
        print(f'Error during fetching <{ticker}>.')
        print(e)
        return None

def get_stock_data(ticker:str, date:datetime.datetime, interval:str='1d', include_adjusted_close:bool=True):
    base_url = 'https://query1.finance.yahoo.com/v7/finance/download/'

    # Encode the query parameters
    params = {
        'period1': int(date[0].timestamp()),
        'period2': int(date[1].timestamp()),
        'interval': interval,
        'events': 'history',
        'includeAdjustedClose': str(include_adjusted_close).lower()
    }
    encoded_params = urllib.parse.urlencode(params)

    # Combine the base URL with the encoded query parameters
    full_url = f"{base_url}{ticker}?{encoded_params}"

    try:
        with urllib.request.urlopen(full_url) as response:
            content = response.read().decode('utf-8')  # Decode the content to a string using UTF-8 encoding
        return content
    except urllib.error.URLError as e:
        print(f"Error while fetching data for {ticker}: {e}")
        return None
    
if __name__ == '__main__':
    import urllib.request
    #Example
    tickers = ['AAPL', 'GOOGL', 'MSFT']
    start = '2010-01-01'
    end = '2023-08-01'
    date = (start,end)
    interval = '1d' #'1wk', '1mo'
    col = 'Adj Close' # 'Open', 'High', 'Low', 'Close', 'Volume'
    file = col+'_stocks.csv'
    stock_updater(tickers,date,interval,'Adj Close',file)
    


    
