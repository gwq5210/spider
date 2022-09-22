echo "" > house.log
mirai_api_key=
es_password=
scrapy crawl house -s MIRAI_API_KEY=$mirai_api_key -s ES_PASSWORD=$es_password --logfile=house.log