#!/usr/bin/env python3
"""
Reddit 爬虫 / Reddit Crawler

从 Reddit 搜索和发现与 Claude Code 相关的资源。
Discovers Claude Code related resources from Reddit search.

支持两种模式：
1. 使用 Reddit API（需要 OAuth）
2. 使用公开 JSON 端点（无需认证，但有速率限制）
"""

import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import quote_plus

from .base_crawler import BaseCrawler


class RedditCrawler(BaseCrawler):
    """Reddit 爬虫 / Reddit crawler"""

    @property
    def name(self) -> str:
        return "Reddit"

    @property
    def source_type(self) -> str:
        return "reddit"

    def __init__(self, config: dict, rate_limit_config: Optional[dict] = None):
        super().__init__(config, rate_limit_config)

        # Reddit 特定配置
        self.reddit_config = config.get('reddit', {})
        self.subreddits = self.reddit_config.get('subreddits', ['ClaudeAI'])
        self.keywords = self.reddit_config.get('keywords', ['claude code'])
        self.min_score = self.reddit_config.get('min_score', 10)
        self.max_age_days = self.reddit_config.get('max_age_days', 30)
        self.posts_per_subreddit = self.reddit_config.get('posts_per_subreddit', 25)
        self.sort = self.reddit_config.get('sort', 'relevance')
        self.time_filter = self.reddit_config.get('time_filter', 'month')

        # 检查是否有 Reddit API 凭证
        self.client_id = os.environ.get('REDDIT_CLIENT_ID')
        self.client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        self.use_api = bool(self.client_id and self.client_secret)

        if self.use_api:
            self._setup_oauth()

    def _setup_oauth(self):
        """设置 Reddit OAuth / Setup Reddit OAuth"""
        try:
            auth = (self.client_id, self.client_secret)
            data = {
                'grant_type': 'client_credentials',
                'device_id': 'DO_NOT_TRACK_THIS_DEVICE'
            }
            headers = {'User-Agent': self.session.headers['User-Agent']}

            response = self.session.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                data=data,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                self.session.headers['Authorization'] = f'Bearer {access_token}'
                print("   ✅ Reddit OAuth 认证成功")
            else:
                print(f"   ⚠️ Reddit OAuth 失败，使用公开端点")
                self.use_api = False

        except Exception as e:
            print(f"   ⚠️ Reddit OAuth 错误: {e}")
            self.use_api = False

    def _search_subreddit(self, subreddit: str, query: str) -> List[dict]:
        """
        搜索特定 subreddit / Search specific subreddit

        Args:
            subreddit: Subreddit 名称 / Subreddit name
            query: 搜索查询 / Search query

        Returns:
            帖子列表 / List of posts
        """
        posts = []

        if self.use_api:
            url = f"https://oauth.reddit.com/r/{subreddit}/search"
        else:
            url = f"https://www.reddit.com/r/{subreddit}/search.json"

        params = {
            'q': query,
            'sort': self.sort,
            't': self.time_filter,
            'limit': self.posts_per_subreddit,
            'restrict_sr': 'true',
        }

        response = self._make_request(url, params=params)

        if not response:
            return posts

        try:
            data = response.json()
            children = data.get('data', {}).get('children', [])

            for child in children:
                post_data = child.get('data', {})
                posts.append(post_data)

        except Exception as e:
            print(f"      ⚠️ 解析响应失败: {e}")

        return posts

    def _get_hot_posts(self, subreddit: str) -> List[dict]:
        """
        获取热门帖子 / Get hot posts

        Args:
            subreddit: Subreddit 名称 / Subreddit name

        Returns:
            帖子列表 / List of posts
        """
        posts = []

        if self.use_api:
            url = f"https://oauth.reddit.com/r/{subreddit}/hot"
        else:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json"

        params = {
            'limit': self.posts_per_subreddit,
        }

        response = self._make_request(url, params=params)

        if not response:
            return posts

        try:
            data = response.json()
            children = data.get('data', {}).get('children', [])

            for child in children:
                post_data = child.get('data', {})
                posts.append(post_data)

        except Exception as e:
            print(f"      ⚠️ 解析响应失败: {e}")

        return posts

    def _filter_post(self, post: dict) -> bool:
        """
        过滤帖子 / Filter post

        Args:
            post: 帖子数据 / Post data

        Returns:
            是否通过过滤 / Whether passed filter
        """
        # 检查分数
        score = post.get('score', 0)
        if score < self.min_score:
            return False

        # 检查年龄
        created_utc = post.get('created_utc', 0)
        if created_utc:
            post_date = datetime.fromtimestamp(created_utc)
            max_age = datetime.now() - timedelta(days=self.max_age_days)
            if post_date < max_age:
                return False

        # 排除自我推广/广告类
        if post.get('is_self', False) and not post.get('selftext'):
            return False

        return True

    def _extract_resource_from_post(self, post: dict) -> Optional[dict]:
        """
        从帖子中提取资源 / Extract resource from post

        Args:
            post: 帖子数据 / Post data

        Returns:
            候选资源或 None / Candidate resource or None
        """
        title = post.get('title', '')
        selftext = post.get('selftext', '')
        url = post.get('url', '')
        score = post.get('score', 0)
        author = post.get('author', '')
        permalink = post.get('permalink', '')

        # 优先提取 GitHub 链接
        github_url = self._extract_github_url(f"{title} {selftext} {url}")

        if github_url and not self._is_duplicate(github_url):
            # 清理描述
            description = selftext[:500] if selftext else title

            return self.create_candidate_resource(
                url=github_url,
                title=title,
                description=description,
                author=author,
                author_url=f"https://reddit.com/u/{author}" if author else '',
                source_score=score,
                extra_metadata={
                    'reddit_permalink': f"https://reddit.com{permalink}",
                    'reddit_score': score,
                    'subreddit': post.get('subreddit', ''),
                }
            )

        # 如果帖子 URL 本身是相关链接
        if url and self._is_relevant_url(url) and not self._is_duplicate(url):
            description = selftext[:500] if selftext else title

            return self.create_candidate_resource(
                url=url,
                title=title,
                description=description,
                author=author,
                author_url=f"https://reddit.com/u/{author}" if author else '',
                source_score=score,
                extra_metadata={
                    'reddit_permalink': f"https://reddit.com{permalink}",
                    'reddit_score': score,
                    'subreddit': post.get('subreddit', ''),
                }
            )

        return None

    def crawl(self) -> List[dict]:
        """
        执行爬取 / Execute crawl

        Returns:
            发现的资源列表 / List of discovered resources
        """
        resources = []
        seen_urls = set()

        print(f"   📋 搜索 {len(self.subreddits)} 个 subreddits...")

        # 按关键词搜索
        for subreddit in self.subreddits:
            print(f"      搜索 r/{subreddit}...")

            for keyword in self.keywords:
                posts = self._search_subreddit(subreddit, keyword)

                for post in posts:
                    if not self._filter_post(post):
                        continue

                    resource = self._extract_resource_from_post(post)
                    if resource:
                        url = resource.get('PrimaryLink', '')
                        if url not in seen_urls:
                            seen_urls.add(url)
                            resources.append(resource)

            # 也获取热门帖子
            hot_posts = self._get_hot_posts(subreddit)
            for post in hot_posts:
                if not self._filter_post(post):
                    continue

                # 检查标题/内容是否包含关键词
                title = post.get('title', '').lower()
                selftext = post.get('selftext', '').lower()
                combined = f"{title} {selftext}"

                has_keyword = any(kw.lower() in combined for kw in self.keywords)
                if not has_keyword:
                    continue

                resource = self._extract_resource_from_post(post)
                if resource:
                    url = resource.get('PrimaryLink', '')
                    if url not in seen_urls:
                        seen_urls.add(url)
                        resources.append(resource)

        return resources
