import os
import time
import csv
import logging
import requests
import pytz
from datetime import datetime
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# =============================
# CONFIGURASI
# =============================
SHOP_ID = 37146675
OUTPUT_FILE = 'logitech2_shop_ratings.csv'
BATCH_SIZE = 100
RATE_LIMIT = 1.5
TARGET_RECORDS = 400  # target jumlah ulasan

# =============================
# LOGGER
# =============================
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =============================
# SHOPEE SCRAPER CLASS
# =============================
class ShopeeScraper:
    def __init__(self, shop_id, output_file, batch_size=20, rate_limit=1.5):
        self.shop_id = shop_id
        self.output_file = output_file
        self.batch_size = batch_size
        self.rate_limit = rate_limit
        self.session = self._setup_session()
        self.base_url = 'https://shopee.co.id/api/v2/shop/get_ratings'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36'
        }

    def _setup_session(self):
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _get_last_offset(self):
        if not os.path.exists(self.output_file):
            return 0
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                lines = sum(1 for line in f) - 1  # header dikurang
                return lines
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return 0

    def _initialize_csv(self):
        if not os.path.exists(self.output_file):
            with open(self.output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Username', 'Rating', 'Tanggal', 'Product Name', 'Message'])

    def _get_data(self, offset):
        params = {
            'limit': self.batch_size,
            'offset': offset,
            'shopid': self.shop_id,
            'type': 0
        }
        try:
            response = self.session.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data: {str(e)}")
            time.sleep(5)
            return None

    def _process_items(self, items: list) -> int:
        indonesia_tz = pytz.timezone('Asia/Jakarta')
        new_items = []
        for item in items:
            try:
                username = item.get('author_username', '')
                rating = item.get('rating_star', '')
                timestamp = item.get('submit_time', '')
                product_items = item.get('product_items', [{}])
                product_name = product_items[0].get('name', '') if product_items else ''
                comment = item.get('comment', '')   # ambil isi review

                # Convert timestamp
                utc_time = datetime.utcfromtimestamp(timestamp)
                localized_time = pytz.utc.localize(utc_time).astimezone(indonesia_tz)
                formatted_time = localized_time.strftime('%Y-%m-%d %H:%M:%S')

                new_items.append([username, rating, formatted_time, product_name, comment])
            except Exception as e:
                logger.error(f"Error processing item: {str(e)}")
                continue

        if new_items:
            with open(self.output_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(new_items)

        return len(new_items)

    def scrape(self):
        self._initialize_csv()
        offset = self._get_last_offset()
        total_processed = offset
        consecutive_empty = 0
        logger.info(f"Starting scraping from offset {offset}")
        while True:
            logger.info(f"Fetching data with offset {offset}... (Total: {total_processed})")
            time.sleep(self.rate_limit)
            response_data = self._get_data(offset)
            if not response_data:
                continue
            data = response_data.get('data', {})
            items = data.get('items', [])
            if not items:
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    logger.info("No more data available")
                    break
                continue
            consecutive_empty = 0
            new_items = self._process_items(items)
            total_processed += new_items
            next_offset = data.get('next_offset')
            if next_offset is None or next_offset == offset:
                logger.info("Next offset not found or has not changed, stopping scraping.")
                break
            offset = next_offset
        logger.info(f"Scraping completed. Total items collected: {total_processed}")

# =============================
# SCHEDULER
# =============================
def check_scraping_status():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as file:
            lines = sum(1 for line in file) - 1
            return lines
    return 0

def schedule_scraping():
    while True:
        logger.info("Checking if scraping is needed...")
        records = check_scraping_status()
        logger.info(f"Found {records} records in the file.")
        if records >= TARGET_RECORDS:
            logger.info("Scraping completed successfully. Target reached. Exiting...")
            break
        else:
            logger.info(f"Scraping needed. Records found: {records}, Target: {TARGET_RECORDS}")
            scraper = ShopeeScraper(SHOP_ID, OUTPUT_FILE, BATCH_SIZE, RATE_LIMIT)
            scraper.scrape()
        time.sleep(5)

# =============================
# MAIN
# =============================
if __name__ == "__main__":
    schedule_scraping()
