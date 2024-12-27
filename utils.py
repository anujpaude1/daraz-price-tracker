import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-interactive plotting
import matplotlib.pyplot as plt
from prisma import Prisma
import datetime
import io

prisma = Prisma()

async def generate_price_chart(product_id: int) -> io.BytesIO:
    # Connect to the Prisma client
    await prisma.connect()

    # Fetch the price data for the given product
    prices = await prisma.price.find_many(
        where={'productId': product_id},
        order={'timestamp': 'asc'}
    )

    # Disconnect the Prisma client
    await prisma.disconnect()

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

# Example usage
if __name__ == "__main__":
    import asyncio
    product_id = 1  # Replace with the actual product ID
    image_data = asyncio.run(generate_price_chart(product_id))
    with open('./temp/price_chart.png', 'wb') as f:
        f.write(image_data.getbuffer())
    print(f"Chart generated for product ID {product_id}")