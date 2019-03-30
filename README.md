# Web Trader
Web Trader is a trading website that consolidates data from Nasdaq, allowing the user to search up the ticker symbol and price of any stock. I employed HTML and CSS to format all the pages and used Python for the back end development. All of the user information, transactions, holdings, and balances are stored in a SQLite3 database. Not only can users search up stocks, they can buy and sell using their own funds. The goal is to end up with a large profit. 

## Setup
- Clone or download the repository.
- Download all the necessary packages:

* **MacOS Users**
```ShellSession
$ pip3 install -r requirements.txt
```

* **Linux Users**
```ShellSession
$ pip install -r requirements.txt
```

- Create the sqlite3 database:
```ShellSession
$ python3 schema.py
$ python3 seed.py
```
- Run the app locally:
```ShellSession
$ python3 controller.py
```
- Paste http://127.0.0.1:5000/login into your web browser and have fun! 🤩

## Example Photos
**This is the login menu where you can login or create a new user account.**
![Login menu](static/login.png?raw=true "Login menu")

**This is the main menu that opens after you log in.**
![Login menu](static/main_menu.png?raw=true "Main menu")

**The dashboard is where you can see all of your previous transactions as well as current holdings.**
![Dashboard](static/dashboard.png?raw=true "Dashboard")

**The buy and sell menu lets the user input the ticker symbol and quantity of the stock that they want to purchase/sell.**
![Buy and Sell Menu](static/buy_sell.png?raw=true "Buy and Sell Menu")

### SQLite3 Database
The database is created using SQLite3. There are five tables in total, each serving a different purpose. For example, the transactions table is used to store the date, number of shares, and ticker symbols of all the users' purchases. This is the code for the transactions table:
```SQLite3
CREATE TABLE transactions(
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker_symbol TEXT,
    num_shares FLOAT,
    owner_username INTEGER,
    last_price FLOAT,
    date TEXT,
    FOREIGN KEY(owner_username) REFERENCES user(username)
);
```

### Issues and New Features :bug:
Feel free to create a GitHub issue for this repo if you have any new ideas/bugs you want fixed!
