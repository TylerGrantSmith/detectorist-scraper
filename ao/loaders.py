from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Identity, Compose, MapCompose, Join
from ao.items import ForumItem, ThreadItem, PostItem, UserItem, MessageItem, QuoteItem

class ForumLoader(ItemLoader):
    default_item_class = ForumItem   
    default_output_processor = TakeFirst()
    forum_path_in = Join(separator=' > ')
    forum_name_in = MapCompose(str.strip)

class ThreadLoader(ItemLoader):
    default_item_class = ThreadItem   
    default_output_processor = TakeFirst()
    thread_title_in = MapCompose(str.strip)

class PostLoader(ItemLoader):
    default_item_class = PostItem   
    default_output_processor = TakeFirst()

class UserLoader(ItemLoader):
    default_item_class = UserItem   
    default_output_processor = TakeFirst()

class MessageLoader(ItemLoader):
    default_item_class = MessageItem
    text_out = Join()
    quotes_out = Identity()

class QuoteLoader(ItemLoader):
    default_item_class = QuoteItem
    default_output_processor = TakeFirst()
    quotes_out = Identity()
