echo "" > images.log
mirai_api_key=
es_password=
scrapyd_password=
# scrapy crawl images -s MIRAI_API_KEY=$mirai_api_key -s ES_PASSWORD=$es_password --logfile=images.log
curl https://scrapyd.gwq5210.com/schedule.json -u gwq5210:$scrapyd_password -d project=spider2048 -d spider=images -d setting=ES_PASSWORD=$es_password -d setting=MIRAI_API_KEY=$mirai_api_key -d setting=LOG_LEVEL=INFO -d setting=PAGE_LIMIT_COUNT=100