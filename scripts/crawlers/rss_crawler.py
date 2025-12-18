#!/usr/bin/env python3
"""
RSS 爬虫 / RSS Crawler

从 RSS 订阅源中发现与 Claude Code 相关的资源。
Discovers Claude Code related resources from RSS feeds.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from email.utils import parsedate_to_datetime

try:
    import feedparser

    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False

from .base_crawler import BaseCrawler


class RSSCrawler(BaseCrawler):
    """RSS 爬虫 / RSS crawler"""

    @property
    def name(self) -> str:
        return "RSS"

    @property
    def source_type(self) -> str:
        return "rss"

    def __init__(self, config: dict, rate_limit_config: Optional[dict] = None):
        super().__init__(config, rate_limit_config)

        # RSS 特定配置
        self.rss_config = config.get("rss", {})
        self.feeds = self.rss_config.get("feeds", [])
        self.entries_per_feed = self.rss_config.get("entries_per_feed", 30)
        self.max_age_days = self.rss_config.get("max_age_days", 14)

        if not HAS_FEEDPARSER:
            print("   ⚠️ feedparser 未安装，RSS 爬虫功能受限")

    def _parse_feed(self, feed_url: str) -> List[dict]:
        """
        解析 RSS feed / Parse RSS feed

        Args:
            feed_url: Feed URL

        Returns:
            条目列表 / List of entries
        """
        if HAS_FEEDPARSER:
            return self._parse_with_feedparser(feed_url)
        else:
            return self._parse_with_requests(feed_url)

    def _parse_with_feedparser(self, feed_url: str) -> List[dict]:
        """使用 feedparser 解析 / Parse with feedparser"""
        entries = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[: self.entries_per_feed]:
                entries.append(
                    {
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "description": entry.get("summary", entry.get("description", "")),
                        "published": entry.get("published", ""),
                        "author": entry.get("author", ""),
                    }
                )

        except Exception as e:
            print(f"      ⚠️ 解析 feed 失败: {e}")

        return entries

    def _parse_with_requests(self, feed_url: str) -> List[dict]:
        """使用 requests 手动解析 / Parse manually with requests"""
        entries = []

        response = self._make_request(feed_url)
        if not response:
            return entries

        content = response.text

        # 简单的 XML 解析（不依赖外部库）
        # 匹配 <item> 或 <entry> 标签
        item_pattern = r"<(?:item|entry)>(.*?)</(?:item|entry)>"
        items = re.findall(item_pattern, content, re.DOTALL)

        for item in items[: self.entries_per_feed]:
            title = self._extract_xml_value(item, "title")
            link = self._extract_xml_value(item, "link")
            description = (
                self._extract_xml_value(item, "description")
                or self._extract_xml_value(item, "summary")
                or self._extract_xml_value(item, "content")
            )
            published = (
                self._extract_xml_value(item, "pubDate")
                or self._extract_xml_value(item, "published")
                or self._extract_xml_value(item, "updated")
            )
            author = self._extract_xml_value(item, "author") or self._extract_xml_value(item, "dc:creator")

            # 处理 Atom 格式的 link
            if not link:
                link_match = re.search(r'<link[^>]*href=["\']([^"\']+)["\']', item)
                if link_match:
                    link = link_match.group(1)

            if title and link:
                entries.append(
                    {
                        "title": self._clean_html(title),
                        "link": link,
                        "description": self._clean_html(description),
                        "published": published,
                        "author": self._clean_html(author),
                    }
                )

        return entries

    def _extract_xml_value(self, xml: str, tag: str) -> str:
        """从 XML 中提取标签值 / Extract tag value from XML"""
        # 处理 CDATA
        pattern = rf"<{tag}[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>"
        match = re.search(pattern, xml, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _clean_html(self, text: str) -> str:
        """清理 HTML 标签 / Clean HTML tags"""
        if not text:
            return ""
        # 移除 HTML 标签
        clean = re.sub(r"<[^>]+>", "", text)
        # 解码 HTML 实体
        clean = clean.replace("&amp;", "&")
        clean = clean.replace("&lt;", "<")
        clean = clean.replace("&gt;", ">")
        clean = clean.replace("&quot;", '"')
        clean = clean.replace("&#39;", "'")
        clean = clean.replace("&nbsp;", " ")
        # 清理多余空白
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串 / Parse date string"""
        if not date_str:
            return None

        try:
            # 尝试 RFC 2822 格式
            return parsedate_to_datetime(date_str)
        except Exception:
            pass

        try:
            # 尝试 ISO 格式
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            pass

        return None

    def _filter_entry(self, entry: dict, keywords: List[str]) -> bool:
        """
        过滤条目 / Filter entry

        Args:
            entry: 条目数据 / Entry data
            keywords: 关键词列表 / Keyword list

        Returns:
            是否通过过滤 / Whether passed filter
        """
        title = entry.get("title", "")
        description = entry.get("description", "")
        link = entry.get("link", "")

        # 检查是否已存在
        github_url = self._extract_github_url(f"{title} {description} {link}")
        target_url = github_url or link

        if self._is_duplicate(target_url):
            return False

        # 检查年龄
        published = entry.get("published", "")
        if published:
            pub_date = self._parse_date(published)
            if pub_date:
                # 确保时区感知
                now = datetime.now(timezone.utc)
                if pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)

                max_age = now - timedelta(days=self.max_age_days)
                if pub_date < max_age:
                    return False

        # 如果有关键词限制，检查是否匹配
        if keywords:
            combined = f"{title} {description}".lower()
            has_keyword = any(kw.lower() in combined for kw in keywords)
            if not has_keyword:
                return False

        return True

    def _create_resource_from_entry(self, entry: dict, feed_name: str) -> Optional[dict]:
        """
        从条目创建资源 / Create resource from entry

        Args:
            entry: 条目数据 / Entry data
            feed_name: Feed 名称 / Feed name

        Returns:
            候选资源或 None / Candidate resource or None
        """
        title = entry.get("title", "")
        description = entry.get("description", "")
        link = entry.get("link", "")
        author = entry.get("author", "")

        # 优先提取 GitHub 链接
        github_url = self._extract_github_url(f"{title} {description} {link}")
        target_url = github_url or link

        if not target_url or not self._is_relevant_url(target_url):
            # 如果不是相关链接，检查是否有 GitHub 链接
            if not github_url:
                return None
            target_url = github_url

        return self.create_candidate_resource(
            url=target_url,
            title=title,
            description=description or title,
            author=author,
            author_url="",
            source_score=0,
            extra_metadata={
                "rss_feed": feed_name,
                "original_link": link,
                "published": entry.get("published", ""),
            },
        )

    def _crawl_feed(self, feed_config: dict) -> List[dict]:
        """
        爬取单个 feed / Crawl single feed

        Args:
            feed_config: Feed 配置 / Feed configuration

        Returns:
            发现的资源列表 / List of discovered resources
        """
        resources = []
        feed_name = feed_config.get("name", "Unknown")
        feed_url = feed_config.get("url", "")
        keywords = feed_config.get("keywords", [])

        print(f"      爬取 {feed_name}...")

        entries = self._parse_feed(feed_url)
        print(f"         获取 {len(entries)} 个条目")

        for entry in entries:
            if not self._filter_entry(entry, keywords):
                continue

            resource = self._create_resource_from_entry(entry, feed_name)
            if resource:
                resources.append(resource)

        print(f"         发现 {len(resources)} 个相关资源")

        return resources

    def crawl(self) -> List[dict]:
        """
        执行爬取 / Execute crawl

        Returns:
            发现的资源列表 / List of discovered resources
        """
        resources = []
        seen_urls = set()

        print(f"   📋 爬取 {len(self.feeds)} 个 RSS feeds...")

        for feed_config in self.feeds:
            feed_resources = self._crawl_feed(feed_config)

            for res in feed_resources:
                url = res.get("PrimaryLink", "")
                if url not in seen_urls:
                    seen_urls.add(url)
                    resources.append(res)

        return resources
