# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# I don't know if it's the best way to do it, but
# every item must have a collection variable that tells the
# MongoPipeline where to put in in the mongoDB database.

# unique_fields is used by MongoPipeline to avoid adding duplicates.
# if & only if ALL unique_fields match an existing document,
# the current item is not added to the database.

class PostItem(scrapy.Item):
    collection = 'post'
    unique_fields = ['thread_id','post_no']

    thread_id = scrapy.Field()
    post_id = scrapy.Field()
    user_id = scrapy.Field()

    post_no = scrapy.Field()    
    timestamp = scrapy.Field()
    message = scrapy.Field()
    quotes = scrapy.Field()

class MessageItem(scrapy.Item):
    post_id = scrapy.Field()
    user_id = scrapy.Field()
    text = scrapy.Field()
    quotes = scrapy.Field()

class QuoteItem(scrapy.Item):
    user_name = scrapy.Field()
    post_id = scrapy.Field()
    text = scrapy.Field()
    quotes = scrapy.Field()

class UserItem(scrapy.Item):
    collection = 'user'
    unique_fields = ['user_id']

    user_id = scrapy.Field()
    user_name = scrapy.Field()

class ThreadItem(scrapy.Item):
    collection = 'thread'
    unique_fields = ['thread_id']

    forum_id = scrapy.Field()
    thread_id = scrapy.Field()
    thread_name = scrapy.Field()
    thread_title = scrapy.Field()
    thread_link = scrapy.Field()

class ForumItem(scrapy.Item):
    collection = 'forum'
    unique_fields = ['forum_id']

    forum_id = scrapy.Field()
    forum_name = scrapy.Field()
    forum_link = scrapy.Field()
    forum_path = scrapy.Field()
