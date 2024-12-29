import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-interactive plotting
import matplotlib.pyplot as plt
from src.initialize import prisma, scraper
from datetime import datetime
import io

from src.scrapePrice import DarazScraper
from src.initialize import prisma

async def generate_price_chart(product_id: int) -> io.BytesIO:

    # Fetch the price data for the given product
    prices = await prisma.price.find_many(
        where={'productId': product_id},
        order={'timestamp': 'asc'}
    )


    # Extract the timestamps and prices
    timestamps = [price.timestamp for price in prices]
    price_values = [price.price for price in prices]

    # Find the peak and bottom prices
    peak_price = max(price_values)
    bottom_price = min(price_values)
    peak_index = price_values.index(peak_price)
    bottom_index = price_values.index(bottom_price)

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, price_values, label='Price', marker='o')
    plt.scatter(timestamps[peak_index], peak_price, color='red', label='Peak Price')
    plt.scatter(timestamps[bottom_index], bottom_price, color='green', label='Bottom Price')
    plt.xlabel('Date')
    plt.ylabel('Price (Rs.)')
    plt.title('Price History')
    plt.legend()
    plt.grid(True)

    # Format the x-axis to show dates properly
    plt.gcf().autofmt_xdate()

    # Save the plot to an in-memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return buf

# Scraper function using DarazScraper
async def fetch_price(product_url, product_id=None):
    details = scraper.get_product_details(product_url)
    if product_id:
            product = await prisma.product.find_unique(where={'uniqueIdentifier': product_id})
            if product:
                current_price = int(details['Current Price'].replace('Rs. ', '').replace(',', ''))
                print(f"Creating price entry with productId: {product.id} and price: {current_price}")
                await prisma.price.create(data={
                    'productId': product.id,
                    'price': current_price
                })
                if current_price < product.lowestPrice:
                    await prisma.product.update(where={'id': product.id}, data={'lowestPrice': current_price})
                if current_price > product.highestPrice:
                    await prisma.product.update(where={'id': product.id}, data={'highestPrice': current_price})

                await prisma.product.update(where={'id': product.id}, data={'lastFetched': datetime.now()})


    return details

# Example usage
if __name__ == "__main__":
    import asyncio
    product_id = 1  # Replace with the actual product ID
    image_data = asyncio.run(generate_price_chart(product_id))
    with open('./temp/price_chart.png', 'wb') as f:
        f.write(image_data.getbuffer())
    print(f"Chart generated for product ID {product_id}")