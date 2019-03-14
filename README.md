# web_trader
Web Trader is a trading website that consolidates data from Nasdaq, allowing the user to search up the ticker symbol and price of any stock. I employed HTML and CSS to format all the pages and used Python for the back end development. All of the user information, transactions, holdings, and balances are stored in a SQLite3 database. Not only can users search up stocks, they can buy and sell using their own funds. The goal is to end up with a large profit. 
This app runs using Flask. After downloading all files, type `python3 controller.py` into your terminal to run the app locally. Next, paste http://127.0.0.1:5000/login into your web browser and have fun!

![Login menu](static/login.png?raw=true "Login menu")
This is the login menu where you can login or create a new user account. 

![Login menu](static/main_menu.png?raw=true "Main menu")
This is the main menu that opens after you log in. 

![Dashboard](static/dashboard.png?raw=true "Dashboard")
The dashboard is where you can see all of your previous transactions as well as current holdings.

![Buy and Sell Menu](static/buy_sell.png?raw=true "Buy and Sell Menu")
The buy and sell menu lets the user input the ticker symbol and quantity of the stock that they want to purchase/sell.
