#!/usr/bin/env python3
"""
Hacker News 爬虫 / Hacker News Crawler

从 Hacker News 搜索和发现与 Claude Code 相关的资源。
Discovers Claude Code related resources from Hacker News search.

使用 Algolia HN Search API。
Uses Algolia HN Search API.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from urllib.parse import quote_plus

from .base_crawler import BaseCrawler


class HackerNewsCrawler(BaseCrawler):
    """Hacker News 爬虫 / Hacker News crawler"""

    # Algolia HN Search API
    SEARCH_API = "https://hn.algolia.com/api/v1/search"
    SEARCH_BY_DATE_API = "https://hn.algolia.com/api/v1/search_by_date"

    @property
    def name(self) -> str:
        return "Hacker News"

    @property
    def source_type(self) -> str:
        return "hackernews"

    def __init__(self, config: dict, rate_limit_config: Optional[dict] = None):
        super().__init__(config, rate_limit_config)

        # HN 特定配置
        self.hn_config = config.get('hackernews', {})
        self.keywords = self.hn_config.get('keywords', ['claude code'])
        self.search_type = self.hn_config.get('search_type', 'story')  # story, comment, all
        self.min_score = self.hn_config.get('min_score', 5)
        self.results_per_keyword = self.hn_config.get('results_per_keyword', 20)
        self.max_age_days = self.hn_config.get('max_age_days', 30)
        self.sort_by = self.hn_config.get('sort_by', 'popularity')  # popularity, date

    def _search(self, query: str) -> List[dict]:
        """
        执行搜索 / Execute search

        Args:
            query: 搜索查询 / Search query

        Returns:
            搜索结果列表 / List of search results
        """
        results = []

        # 选择 API 端点
        if self.sort_by == 'date':
            api_url = self.SEARCH_BY_DATE_API
        else:
            api_url = self.SEARCH_API

        # 构建请求参数
        params = {
            'query': query,
            'hitsPerPage': self.results_per_keyword,
        }

        # 设置搜索类型
        if self.search_type == 'story':
            params['tags'] = 'story'
        elif self.search_type == 'comment':
            params['tags'] = 'comment'
        # 'all' 不需要 tags 参数

        # 设置时间范围
        if self.max_age_days:
            timestamp = int((datetime.now(timezone.utc) - timedelta(days=self.max_age_days)).timestamp())
            params['numericFilters'] = f'created_at_i>{timestamp}'

        response = self._make_request(api_url, params=params)

        if not response:
            return results

        try:
            data = response.json()
            hits = data.get('hits', [])

            for hit in hits:
                results.append(hit)

        except Exception as e:
            print(f"      ⚠️ 解析响应失败: {e}")

        return results

    def _filter_hit(self, hit: dict) -> bool:
        """
        过滤搜索结果 / Filter search result

        Args:
            hit: 搜索结果 / Search result

        Returns:
            是否通过过滤 / Whether passed filter
        """
        # 检查分数
        points = hit.get('points', 0) or 0
        if points < self.min_score:
            return False

        # 检查是否有 URL
        url = hit.get('url', '')
        story_url = hit.get('story_url', '')
        target_url = url or story_url

        if not target_url:
            return False

        # 检查是否已存在
        github_url = self._extract_github_url(target_url)
        check_url = github_url or target_url

        if self._is_duplicate(check_url):
            return False

        return True

    def _create_resource_from_hit(self, hit: dict) -> Optional[dict]:
        """
        从搜索结果创建资源 / Create resource from search result

        Args:
            hit: 搜索结果 / Search result

        Returns:
            候选资源或 None / Candidate resource or None
        """
        title = hit.get('title', '') or hit.get('story_title', '')
        url = hit.get('url', '') or hit.get('story_url', '')
        author = hit.get('author', '')
        points = hit.get('points', 0) or 0
        num_comments = hit.get('num_comments', 0) or 0
        object_id = hit.get('objectID', '')
        created_at = hit.get('created_at', '')

        # 优先提取 GitHub 链接
        github_url = self._extract_github_url(url)
        target_url = github_url or url

        if not target_url or not self._is_relevant_url(target_url):
            return None

        # 构建描述
        description = title
        if hit.get('story_text'):
            # 如果是评论，使用评论文本
            description = hit['story_text'][:500]

        return self.create_candidate_resource(
            url=target_url,
            title=title,
            description=description,
            author=author,
            author_url=f"https://news.ycombinator.com/user?id={author}" if author else '',
            source_score=points,
            extra_metadata={
                'hn_id': object_id,
                'hn_url': f"https://news.ycombinator.com/item?id={object_id}",
                'hn_points': points,
                'hn_comments': num_comments,
                'original_url': url,
                'created_at': created_at,
            }
        )

    def crawl(self) -> List[dict]:
        """
        执行爬取 / Execute crawl

        Returns:
            发现的资源列表 / List of discovered resources
        """
        resources = []
        seen_urls = set()

        print(f"   📋 搜索 {len(self.keywords)} 个关键词...")

        for keyword in self.keywords:
            print(f"      搜索 \"{keyword}\"...")

            hits = self._search(keyword)
            print(f"         找到 {len(hits)} 个结果")

            for hit in hits:
                if not self._filter_hit(hit):
                    continue

                resource = self._create_resource_from_hit(hit)
                if resource:
                    url = resource.get('PrimaryLink', '')
                    if url not in seen_urls:
                        seen_urls.add(url)
                        resources.append(resource)

        return resources
