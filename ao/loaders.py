from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Identity, MapCompose, Compose, Join
from ao.items import ForumItem, ThreadItem, PostItem, UserItem, MessageItem, QuoteItem
from ao.processors import to_int, or_zero


class ForumLoader(ItemLoader):
    default_item_class = ForumItem   
    default_output_processor = TakeFirst()
    forum_id_in = MapCompose(to_int)
    forum_path_out = Identity()
    forum_path_in = MapCompose(to_int)
    #forum_path_out = Join(separator=' > ')
    forum_name_in = MapCompose(str.strip)

class PostLoader(ItemLoader):
    default_item_class = PostItem   
    default_output_processor = TakeFirst()

    thread_id_in = MapCompose(to_int)
    user_name_in = MapCompose(str.strip, Join(''))
    user_id_in = MapCompose(to_int)
    post_id_in = MapCompose(to_int)
    post_no_in = MapCompose(to_int)

class MessageLoader(ItemLoader):
    default_item_class = MessageItem
    text_in = MapCompose(str.strip)
    text_out = Join()
    post_id_in = MapCompose(to_int)
    user_id_in = MapCompose(to_int)
    quotes_out = Identity()

class ThreadLoader(ItemLoader):
    default_item_class = ThreadItem   
    default_output_processor = TakeFirst()
    
    forum_id_in = MapCompose(to_int)
    thread_id_in = MapCompose(to_int)
    thread_title_in = MapCompose(str.strip)

class UserLoader(ItemLoader):
    default_item_class = UserItem   
    default_output_processor = TakeFirst()
    user_name_in = MapCompose(str.strip, Join(''))
    user_id_in = MapCompose(to_int, or_zero)

class QuoteLoader(ItemLoader):
    default_item_class = QuoteItem
    default_output_processor = TakeFirst()
    post_id_in = MapCompose(to_int)
    user_id_in = MapCompose(to_int)
    text_in = MapCompose(str.strip)
    text_out = Join()
