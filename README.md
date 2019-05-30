# dividend-screener
Python program that screens an ecosystem of dividend stocks using yfinance and the Dividend Champions Spreadsheet

yfinance: https://github.com/ranaroussi/yfinance

Dividend Champions: https://www.dripinvesting.org/tools/tools.asp

How to use the program

1. Clone the repository onto your local machine
2. Go into the dividend_settings.txt file and update your preferred screening criteria
3. Run dividend-screener.py

The program will download the Dividend Champions spreadsheet, parse the stocks, download
the latest pricing data, adjust dividend data based on up to date pricing, then create a screened list
of dividend stocks in the same folder.
