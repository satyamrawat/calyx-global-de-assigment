# Scrapy settings for assigment_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "assigment_scrapy"

SPIDER_MODULES = ["assigment_scrapy.spiders"]
NEWSPIDER_MODULE = "assigment_scrapy.spiders"

CONCURRENT_REQUESTS = 10
DOWNLOAD_DELAY = 0.1

# Obey robots.txt rules
ROBOTSTXT_OBEY = True


# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
