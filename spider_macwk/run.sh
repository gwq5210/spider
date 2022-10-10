echo "" > soft.log
mirai_api_key=
es_password=
scrapyd_password=
# scrapy crawl soft -s MIRAI_API_KEY=$mirai_api_key -s ES_PASSWORD=$es_password --logfile=soft.log
curl https://scrapyd.gwq5210.com/schedule.json -u gwq5210:$scrapyd_password -d project=spider_macwk -d spider=soft -d setting=ES_PASSWORD=$es_password -d setting=MIRAI_API_KEY=$mirai_api_key -d setting=LOG_LEVEL=INFO
