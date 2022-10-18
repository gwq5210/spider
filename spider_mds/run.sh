echo "" > m3u8.log
mirai_api_key=
es_password=
scrapyd_password=
# scrapy crawl m3u8 -s MIRAI_API_KEY=$mirai_api_key -s ES_PASSWORD=$es_password -s PAGE_LIMIT_COUNT=-1 --logfile=m3u8.log
curl https://scrapyd.gwq5210.com/schedule.json -u gwq5210:$scrapyd_password \
  -d project=spider_mds -d spider=m3u8 -d setting=ES_PASSWORD=$es_password \
  -d setting=MIRAI_API_KEY=$mirai_api_key -d setting=LOG_LEVEL=INFO \
  -d setting=PAGE_LIMIT_COUNT=-1 -d setting=FILES_STORE=/usr/share/scrapyd/mds_m3u8