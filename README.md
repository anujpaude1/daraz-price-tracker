# Daraz Price Tracker
Link : https://t.me/DarazTrackPriceBot

This project is a Telegram bot that helps users track prices of products on Daraz. Users can receive notifications about price changes and view price history charts.

## Features

- Track the price of any product on Daraz
- Receive daily or weekly notifications about price changes
- View price history charts
- Set custom minimum price notifications

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/daraz-price-tracker.git
    cd daraz-price-tracker
    ```

2. Create a virtual environment and activate it:
    ```sh
    python3 -m venv myenv
    source myenv/bin/activate
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    ```sh
    cp .env.example .env
    # Edit the .env file to include your Telegram bot token and other necessary configurations
    ```

5. Initialize the Prisma client:
    ```sh
    prisma generate
    prisma migrate dev
    ```

## Usage

1. Run the bot:
    ```sh
    python main.py
    ```

2. Interact with the bot on Telegram:
    - Use the `/start` command to begin.
    - Send a product link to start tracking its price.
    - Use the provided inline keyboard to navigate through options.

## Development

### Code Structure

- `main.py`: Contains the main logic for the bot, including command and message handlers.
- `scrapePrice.py`: Contains the scraper logic to fetch product details from Daraz.
- `utils.py`: Contains utility functions, including generating price charts.
- `logger.py`: Contains the setup for logging.
- `prisma/`: Contains the Prisma schema and migration files.

### Adding New Features

1. Create a new branch for your feature:
    ```sh
    git checkout -b feature-name
    ```

2. Make your changes and commit them:
    ```sh
    git add .
    git commit -m "Add new feature"
    ```

3. Push your branch and create a pull request:
    ```sh
    git push origin feature-name
    ```

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Python Telegram Bot](https://python-telegram-bot.org/)
- [Prisma Client Python](https://github.com/RobertCraigie/prisma-client-py)
- [Undetected Chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
