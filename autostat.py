class AutoStatPipeline:
    def __init__(self):
        self.spider = None
        self.item_count = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider):
        self.spider = spider

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        self.item_count += 1
        self.spider.logger.info('Processing item count: %d', (self.item_count))
        return item
