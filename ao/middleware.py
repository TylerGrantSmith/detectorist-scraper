from scrapy.exceptions import IgnoreRequest
import memcache


class IgnoreDuplicateMiddleware(object):
    def process_request(self, request, spider):
        logger.info('pr...................')
        request.meta['proxy']



