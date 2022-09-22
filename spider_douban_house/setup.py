# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'project',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = spider_douban_house.settings']},
    package_data = {'spider_douban_house': ['mapping.json']}
)

