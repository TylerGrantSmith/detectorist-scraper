import scrapy
from scrapy.linkextractors import LinkExtractor
import re
from ao.items import PostItem, UserItem, ThreadItem, ForumItem, MessageItem, QuoteItem
from ao.loaders import PostLoader, UserLoader, ThreadLoader, ForumLoader, MessageLoader, QuoteLoader
import logging
from scrapy.shell import inspect_response

class ActuarialOutpostSpider(scrapy.Spider):
    name = 'ao'
    allowed_domains = ['actuarialoutpost.com']
    start_urls = ["http://www.actuarialoutpost.com/actuarial_discussion_forum/forumdisplay.php?f=50"]

    patterns = {
        'thread_id': re.compile('t=(\\d+)'),
        'forum_id':  re.compile('f=(\\d+)'),
        'user_id':   re.compile('u=(\\d+)'),
        'post_no':   re.compile('postcount=(\d+)'),
        'post_id':   re.compile('p=(\d+)') 
        }

    xpaths = {
        'next_page': "//*[@class='pagenav']//*[@href and contains(text(), '>')]/@href",
        'unmoved_threads': ".//a[contains(@id,'thread_title')][not(./parent::div/parent::td/preceding-sibling::td/img[@src = 'images/statusicon/thread_moved.gif'])]",
        'quotes':    '(/div[text()="Quote:"])/following::div[1]'
    }
    
    def _get_quote(self, quote):
        ql = QuoteLoader(selector=quote)
        ql.add_xpath('user_name', './tr/td/div/strong/text()')
        ql.add_xpath('post_id', './tr/td/div/a/@href', re = self.patterns['post_id'])
        ql.add_xpath('text', './tr/td/div[2]/text()')
        
        return dict(ql.load_item())

    def _get_message(self, post):
        ml = MessageLoader(selector=post)
        ml.selector = ml.selector.xpath('.//div[contains(@id, "post_message_")]')
        ml.add_xpath('text', './text()')

        for quote in ml.selector.xpath('./div/table[preceding-sibling::div/text() = "Quote:"]'):
            ml.add_value('quotes', self._get_quote(quote))
        
        return ml.load_item()

    def _get_post( self, response, post):
        pl = PostLoader(selector=post)
        pl.add_value('thread_id', response.url, re = self.patterns['thread_id'])
        pl.add_xpath('post_id', ".//a[@target='new']/@href", re = self.patterns['post_id'])
        pl.add_xpath('post_no', ".//a[@target='new']/@href", re = self.patterns['post_no'])
        pl.add_xpath('user_name', './/div[starts-with(@id, "postmenu") and not(./@class="vbmenu_popup")]/descendant-or-self::*[not(self::script)]/text()')
        pl.add_xpath('user_id', './/div[starts-with(@id, "postmenu") and not(./@class="vbmenu_popup")]/a/@href', re = self.patterns['user_id'])
        pl.add_value('message', self._get_message(post))
        return pl.load_item()

    def _get_user_from_post(self, post):
        ul = UserLoader(selector=post)
        ul.add_xpath('user_id',   './/div[starts-with(@id, "postmenu") and not(./@class="vbmenu_popup")]/a/@href', re = self.patterns['user_id'])
        ul.add_xpath('user_name', './/div[starts-with(@id, "postmenu") and not(./@class="vbmenu_popup")]/descendant-or-self::*[not(self::script)]/text()')
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
        fl.add_css('forum_path', '.navbar>a::attr(href)', re = self.patterns['forum_id'])
        fl.add_css('forum_name', '.navbar>a~::text')
        return fl.load_item()

    def paginate(self, response, callback):
        next_page = response.xpath(self.xpaths['next_page']).get()
        logging.info(f'SCRAPING NEXT PAGE: {next_page}')
        if next_page is not None:
            return response.follow(next_page, callback=callback)
        
        logging.info("NO MORE PAGES FOUND")


    def parse(self, response):
        # Parse the board (aka index) for forum URLs
        for link in LinkExtractor(restrict_xpaths='.//td[re:match(@id, "f\\d+")]').extract_links(response):
            yield response.follow(link, callback=self.parse_forum, dont_filter = True)
        
        for thread in self.parse_forum(response):
            yield thread

        yield self.paginate(response, self.parse)

    def parse_forum(self, response):
        yield self._get_forum(response)
        logging.info("STARTING NEW FORUM SCRAPE (GETTING THREADS)")
        
        for link in LinkExtractor(restrict_xpaths=self.xpaths['unmoved_threads']).extract_links(response):
            yield response.follow(link, callback=self.parse_thread, meta={'thread_title':link.text})
        
        logging.info(f"GETTING NEXT PAGE: {response.url}")
        yield self.paginate(response, self.parse_forum)
        
        
    def parse_thread(self, response):

        logging.info("GETTING THREAD")
        yield self._get_thread(response)
        
        logging.info("STARTING NEW THREAD SCRAPE (GETTING POSTS)")
    
        for post in self.parse_posts(response):
            yield post

    def parse_posts(self, response):

        for post in response.xpath("//table[contains(@id,'post')]"):
            logging.info("SCRAPING USER")
            yield self._get_user_from_post(post)
            logging.info("SCRAPING POST")
            yield self._get_post(response, post)
        
        # return the next thread page if it exists
        yield self.paginate(response, self.parse_posts)