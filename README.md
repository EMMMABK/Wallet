# Crypto Prices Django Project

This is a Django project that fetches cryptocurrency prices from the Binance API and saves them to a PostgreSQL database.

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/your-username/crypto-prices-django.git

# Navigate to the project directory:

cd crypto-prices-django

# Create a virtual environment and activate it:

python -m venv env
source env/bin/activate

# Install the required dependencies:

pip install -r requirements.txt

# Set up the PostgreSQL database:

Make sure you have PostgreSQL installed and running.
Open crypto_project/settings.py and update the database settings (HOST, PORT, NAME, USER, PASSWORD) according to your PostgreSQL configuration.

# Apply database migrations:

python manage.py migrate

# Usage
To save cryptocurrency prices to the database, you can use the following URL:

http://127.0.0.1:8000/save-crypto-prices/
You can access the Django admin panel to view and manage the saved crypto prices:

http://127.0.0.1:8000/admin/crypto_prices/cryptoprice/

# Customization

The fetching of cryptocurrency prices from the Binance API and saving them to the database is implemented in the save_crypto_prices view function in crypto_prices/views.py. You can customize this function to suit your needs.
The CryptoPrice model in crypto_prices/models.py defines the fields for the cryptocurrency prices. You can modify the model to include additional fields if desired.
The CryptoPriceAdmin class in crypto_prices/admin.py customizes the admin panel display for the CryptoPrice model. You can modify this class to add more customization if needed.
 
# Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

# License

This project is licensed under the MIT License.

