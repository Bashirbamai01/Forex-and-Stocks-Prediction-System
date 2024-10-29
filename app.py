import streamlit as st
import pandas as pd
import yfinance as yf
from ta.volatility import BollingerBands
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.momentum import RSIIndicator
import datetime
from datetime import date
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import r2_score, mean_absolute_error



st.title('PROJECT: FOREX AND STOCKS PRICE PREDICTION SYSTEM USING TIME SERIES ALGORITHM')
st.sidebar.info("By: BASHIR BAMAI")
st.sidebar.info("Supervisor: DR. A. M. MABU")
st.sidebar.info("DATASET: YAHOO FINANCE")

st.sidebar.info('Choose your options below')

def main():
    option = st.sidebar.selectbox('Make a choice', ['Recent Data', 'Predict'])
    if option == 'Visualize':
        # tech_indicators()
    elif option == 'Recent Data':
        dataframe()
    else:
        predict()



@st.cache_resource
def download_data(op, start_date, end_date):
    df = yf.download(op, start=start_date, end=end_date, progress=False)
    return df


symbol_type = st.sidebar.selectbox('Data Type', ['Stocks', 'Forex'])
option = st.sidebar.text_input('Enter a Symbol', value='SPY')
option = option.upper()


today = datetime.date.today()
duration = 3000
before = today - datetime.timedelta(days=duration)
start_date = st.sidebar.date_input('Start Date', value=before)
end_date = st.sidebar.date_input('End date', today)
if st.sidebar.button('Send'):
    if start_date < end_date:
        st.sidebar.success('Start date: `%s`\n\nEnd date: `%s`' %(start_date, end_date))
        download_data(option, start_date, end_date)
    else:
        st.sidebar.error('Error: End date must fall after start date')




data = download_data(option, start_date, end_date)
scaler = StandardScaler()

def tech_indicators():
    st.header('Technical Indicators')
    option = st.radio('Choose a Technical Indicator to Visualize', ['Close', 'BB', 'MACD', 'RSI', 'SMA', 'EMA'])

    # Bollinger bands
    bb_indicator = BollingerBands(data.Close)
    bb = data
    bb['bb_h'] = bb_indicator.bollinger_hband()
    bb['bb_l'] = bb_indicator.bollinger_lband()
    # Creating a new dataframe
    bb = bb[['Close', 'bb_h', 'bb_l']]
    # MACD
    macd = MACD(data.Close).macd()
    # RSI
    rsi = RSIIndicator(data.Close).rsi()
    # SMA
    sma = SMAIndicator(data.Close, window=14).sma_indicator()
    # EMA
    ema = EMAIndicator(data.Close).ema_indicator()

    if option == 'Close':
        st.write('Close Price')
        st.line_chart(data.Close)
    elif option == 'BB':
        st.write('BollingerBands')
        st.line_chart(bb)
    elif option == 'MACD':
        st.write('Moving Average Convergence Divergence')
        st.line_chart(macd)
    elif option == 'RSI':
        st.write('Relative Strength Indicator')
        st.line_chart(rsi)
    elif option == 'SMA':
        st.write('Simple Moving Average')
        st.line_chart(sma)
    else:
        st.write('Expoenetial Moving Average')
        st.line_chart(ema)


def dataframe():
    st.header('Recent Data')
    st.dataframe(data.tail(10))



def predict():
    # model = st.radio('Choose a model', ['LinearRegression', 'RandomForestRegressor', 'ExtraTreesRegressor', 'KNeighborsRegressor', 'XGBoostRegressor'])
    
    num = st.number_input('How many days forecast?', value=5)
    num = int(num)
    
    if st.button('Predict'):
        engine = RandomForestRegressor()
        model_engine(engine, num)
def model_engine(model, num):
    # Getting only the closing price
    df = data[['Close']].copy()
    
    # Shifting the closing price based on number of days forecast
    df['preds'] = df['Close'].shift(-num)

    # Dropping rows with NaN values
    df.dropna(inplace=True)

    # Scaling the data
    x = df[['Close']].values  # Use only the 'Close' column
    x = scaler.fit_transform(x)

    # Storing the last num_days data for forecasting
    x_forecast = x[-num:]

    # Selecting the required values for training
    x = x[:-num]
    
    # Getting the preds column
    y = df['preds'].values
    y = y[:-num]

    # Splitting the data
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2, random_state=7)

    # Training the model
    model.fit(x_train, y_train)
    
    # Making predictions
    preds = model.predict(x_test)

    # Displaying metrics
    st.text(f'r2_score: {r2_score(y_test, preds)} \
            \nMAE: {mean_absolute_error(y_test, preds)}')
    
    # Predicting stock price based on the number of days
    forecast_pred = model.predict(x_forecast)
    day = 1
    for i in forecast_pred:
        st.text(f'Day {day}: {i}')
        day += 1



if __name__ == '__main__':
    main()
