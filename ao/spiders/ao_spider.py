import scrapy
from scrapy.linkextractors import LinkExtractor
import re
from ao.processors import to_int
from ao.items import PostItem, UserItem, ThreadItem, ForumItem, MessageItem, QuoteItem
from ao.loaders import PostLoader, UserLoader, ThreadLoader, ForumLoader, MessageLoader, QuoteLoader
import logging


class ActuarialOutpostSpider(scrapy.Spider):
    name = 'ao'
    allowed_domains = ['actuarialoutpost.com']
    start_urls = ["http://www.actuarialoutpost.com/actuarial_discussion_forum/forumdisplay.php?f=41"]

    patterns = {
        'thread_id': re.compile('t=(\\d+)'),
        'forum_id':  re.compile('f=(\\d+)'),
        'user_id':   re.compile('u=(\\d+)'),
        'post_no': re.compile('postcount=(\d+)'),
        'post_id':   re.compile('p=(\d+)') 
        }

    xpaths = {
        'next_page': "//*[@class='pagenav']//*[@href and contains(text(), '>')]/@href",
        'quotes':    '(/div[text()="Quote:"])/following::div[1]'
    }

    def _get_quote(self, response, quote):
        ql = QuoteLoader(response=response)
        ql.selector = quote
        ql.add_xpath('user_name', './/strong/text()')
        ql.add_xpath('post_id', './/a/@href', re = self.patterns['post_id'])
        ql.add_value('text', '')
        return dict(ql.load_item())

    def _get_message(self, response, post):
        ml = MessageLoader(response=response)
        ml.selector = post.xpath('.//div[contains(@id, "post_message_")]')
        ml.add_xpath('text', './/text()')
        for quote in post.xpath('.//div[text() = "Quote:"]/following-sibling::table'):
            ml.add_value('quotes', self._get_quote(response, quote))
        return ml.load_item()

    def _get_post( self, response, post):
        pl = PostLoader(response=response)
        pl.selector = post
        pl.add_value('thread_id', response.url, re = self.patterns['thread_id'])
        pl.add_xpath('post_id', ".//a[@target='new']/@href", re = self.patterns['post_id'])
        pl.add_xpath('post_no', ".//a[@target='new']/@href", re = self.patterns['post_no'])
        pl.add_xpath('user_id', ".//a[@class='bigusername']/@href", re = self.patterns['user_id'])
        #pl.add_xpath('message', ".//*[contains(@id,'post_message_')]")
        pl.add_value('message', self._get_message(response, post))
        return pl.load_item()

    def _get_user_from_post(self, response, post):
        ul = UserLoader(response=response)
        ul.selector = post
        ul.add_xpath('user_id',   ".//a[@class='bigusername']/@href", re = self.patterns['user_id'])
        ul.add_xpath('user_name', ".//a[@class='bigusername']//text()")
        return ul.load_item()

    def parse_quote(self, response):
        name = response.xpath('./div/strong/text()').get()
        post = response.xpath('./div/a', re = '[#post](\d+)').get()
        post_link = response.xpath('./div/a').get()

    def _get_thread(self, response):
        tl = ThreadLoader(response=response)
        tl.add_value('thread_id',    response.url, re = self.patterns['thread_id'])
        tl.add_xpath('forum_id', '(.//*[@class="navbar"]/a)[last()-1]/@href', re = self.patterns['forum_id'])
        tl.add_css('thread_title', '.navbar>a~::text')
        tl.add_value('thread_link',  response.url)
        return tl.load_item()

    def _get_forum(self, response):
        fl = ForumLoader(response=response)
        fl.add_value('forum_id',   response.url, re = self.patterns['forum_id'])
        fl.add_value('forum_link', response.url)
        fl.add_css('forum_path', '.navbar>a::text')
        fl.add_css('forum_name', '.navbar>a~::text')
        return fl.load_item()

    def paginate(self, response, callback):
        next_page = response.xpath(self.xpaths['next_page']).get()
        if next_page is not None:
            return response.follow(next_page, callback=self.parse_thread)
        else:
            logging.info("NO MORE PAGES FOUND")
            return None

    def parse(self, response):
        # Parse the board (aka index) for forum URLs
        for link in LinkExtractor(restrict_xpaths='.//td[re:match(@id, "f\\d+")]').extract_links(response):
            yield response.follow(link, callback=self.parse_forum)

    def parse_forum(self, response):
        logging.info("STARTING NEW FORUM SCRAPE (GETTING THREADS)")
        
        yield self._get_forum(response)

        for link in LinkExtractor(restrict_xpaths='.//a[contains(@id,"thread_title")]').extract_links(response):
            yield response.follow(link, callback=self.parse_thread, meta={'thread_title':link.text})

        # return the next forum page if it exists
        yield self.paginate(response, self.parse_forum)
        
    def parse_thread(self, response):

        logging.info("STARTING NEW THREAD SCRAPE (GETTING POSTS)")
        
        yield self._get_thread(response)

        for post in response.xpath("//table[contains(@id,'post')]"):
            yield self._get_user_from_post(response, post)
            yield self._get_post(response, post)
            
        # return the next thread page if it exists
        yield self.paginate(response, self.parse_thread)
        
        
    