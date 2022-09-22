echo "" > soft.log
mirai_api_key=
es_password=
scrapy crawl soft -s MIRAI_API_KEY=$mirai_api_key -s ES_PASSWORD=$es_password --logfile=soft.log