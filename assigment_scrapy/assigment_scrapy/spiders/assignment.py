import scrapy
import json
import time
from scrapy.exceptions import CloseSpider

class GoldStandardSpider(scrapy.Spider):
    name = "gold_standard"
    start_urls = [
        'https://public-api.goldstandard.org/projects?query=&page=1',
    ]
    page = 1
    # Initialize a counter for requests
    request_count = 0
    max_requests_before_pause = 10  # Max requests before pausing
    pause_duration = 30  # 30 seconds pause after 10 requests

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'origin': 'https://registry.goldstandard.org',
        'referer': 'https://registry.goldstandard.org/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }
    def parse(self, response):
        # Extracting each project listing
        request = scrapy.Request(self.start_urls[0], callback=self.parse_api, headers=self.headers)
        yield request


    def parse_api(self, response):
        # base_url = 'https://public-api.goldstandard.org/projects?query=&page=1'


        if response.status == 429:
            self.logger.warning("Rate limit reached, will retry.")
            return  # Let Scrapy handle the retry


        # Increment the request counter
        self.request_count += 1
        raw_data = response.body
        all_data = json.loads(raw_data)
        if not all_data:
            raise CloseSpider('No more data to scrape, stopping the spider.')
        # print(f'Project --> {data}')
        for data in all_data:
            yield{
                'id': data['id'],
                'gs_id': data['sustaincert_id'],
                'project_details': data['name'],
                'status': data['status'],
                'project_type': data['type'],
                'country': data['country'],
                'actions': data['sustaincert_url'],
                'description': data['description'],

            }

        # Check if we've made 10 requests
        if self.request_count >= 10:
            self.logger.info("Sleeping for 30 seconds after 10 requests...")
            time.sleep(30)  # Sleep for 30 seconds
            self.request_count = 0  # Reset the counter
        
        url_parts = self.start_urls[0].split('page=')

        # Increment the page number
        current_page = int(url_parts[1])
        self.page = self.page + 1

        # Join the parts together with the updated page number
        updated_url = f'{url_parts[0]}page={self.page}'
        self.logger.info(f'Fetching page {self.page}: {updated_url}')

        print(updated_url)
        yield scrapy.Request(updated_url, callback=self.parse_api, headers=self.headers, dont_filter=True)