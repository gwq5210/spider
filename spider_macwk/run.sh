echo "" > soft.log
mirai_api_key=
es_user=
es_passwd=
scrapy crawl soft -s MIRAI_API_KEY=$mirai_api_key -s ES_URL=https://$es_user:$es_passwd@gwq5210.com/es --logfile=soft.log