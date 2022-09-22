echo "" > nes.log
mirai_api_key=
es_password=
scrapyd_password=
scrapy crawl nes -s MIRAI_API_KEY=$mirai_api_key -s ES_PASSWORD=$es_password --logfile=nes.log
# curl https://gwq5210:$scrapyd_password@gwq5210.com:6800/schedule.json -d project=spider_wexyx -d spider=nes -d setting=ES_PASSWORD=$es_password -d setting=MIRAI_API_KEY=$mirai_api_key -d setting=LOG_LEVEL=INFO