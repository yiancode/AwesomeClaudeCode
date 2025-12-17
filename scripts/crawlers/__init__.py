"""
爬虫模块 / Crawlers Module

提供多源资源发现的爬虫实现。
Provides crawler implementations for multi-source resource discovery.
"""

from .base_crawler import BaseCrawler
from .reddit_crawler import RedditCrawler
from .awesome_list_crawler import AwesomeListCrawler
from .rss_crawler import RSSCrawler
from .hackernews_crawler import HackerNewsCrawler

__all__ = [
    'BaseCrawler',
    'RedditCrawler',
    'AwesomeListCrawler',
    'RSSCrawler',
    'HackerNewsCrawler',
]
