from scrapy.crawler import Crawler
from scrapy import signals
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from billiard.process import Process


class CrawlerScript(Process):
    def __init__(self, spider, *args, **kwargs):
        super(CrawlerScript, self).__init__(*args, **kwargs)
        Process.__init__(self)
        settings = get_project_settings()
        self.crawler = Crawler(spider.__class__, settings)
        self.crawler.signals.connect(reactor, signal=signals.spider_closed)
        self.spider = spider

    def run(self):
        self.crawler.crawl(self.spider)
        reactor.run()

def crawl_async():
    spider = MySpider()
    crawler = CrawlerScript(spider)
    crawler.start()
    crawler.join()
