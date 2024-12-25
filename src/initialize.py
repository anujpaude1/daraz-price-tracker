from prisma import Prisma
from src.scrapePrice import DarazScraper
from src.logger import setup_logger
import datetime
from pytz import timezone

prisma = Prisma()
# Initialize Prisma client
prisma = Prisma()
scraper = DarazScraper()
tz = timezone("Asia/Kathmandu")
log=setup_logger(__name__)