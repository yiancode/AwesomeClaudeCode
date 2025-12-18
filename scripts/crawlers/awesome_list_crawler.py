#!/usr/bin/env python3
"""
Awesome List 爬虫 / Awesome List Crawler

从 GitHub Awesome 列表中发现与 Claude Code 相关的资源。
Discovers Claude Code related resources from GitHub Awesome lists.
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from .base_crawler import BaseCrawler


class AwesomeListCrawler(BaseCrawler):
    """Awesome List 爬虫 / Awesome List crawler"""

    @property
    def name(self) -> str:
        return "Awesome Lists"

    @property
    def source_type(self) -> str:
        return "awesome-list"

    def __init__(self, config: dict, rate_limit_config: Optional[dict] = None):
        super().__init__(config, rate_limit_config)

        # Awesome List 特定配置
        self.awesome_config = config.get("awesome_lists", {})
        self.lists = self.awesome_config.get("lists", [])
        self.deep_parse = self.awesome_config.get("deep_parse", True)
        self.max_links_per_list = self.awesome_config.get("max_links_per_list", 100)

        # GitHub token
        self.github_token = os.environ.get("GITHUB_TOKEN")
        if self.github_token:
            self.session.headers["Authorization"] = f"Bearer {self.github_token}"

    def _extract_github_repo(self, url: str) -> Optional[Tuple[str, str]]:
        """
        从 URL 提取 GitHub owner/repo / Extract GitHub owner/repo from URL

        Returns: (owner, repo) or None
        """
        if "github.com" not in url:
            return None

        parts = url.rstrip("/").split("/")
        try:
            github_index = next(i for i, p in enumerate(parts) if "github.com" in p)
            if len(parts) > github_index + 2:
                owner = parts[github_index + 1]
                repo = parts[github_index + 2].replace(".git", "")
                return (owner, repo)
        except (StopIteration, IndexError):
            pass

        return None

    def _get_readme_content(self, owner: str, repo: str) -> Optional[str]:
        """
        获取仓库 README 内容 / Get repository README content

        Args:
            owner: 仓库所有者 / Repository owner
            repo: 仓库名 / Repository name

        Returns:
            README 内容 / README content
        """
        # 尝试不同的 README 文件名
        readme_names = ["README.md", "readme.md", "Readme.md", "README", "readme"]

        for readme_name in readme_names:
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{readme_name}"
            response = self._make_request(url)

            if response:
                return response.text

            # 尝试 master 分支
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/{readme_name}"
            response = self._make_request(url)

            if response:
                return response.text

        return None

    def _parse_markdown_links(self, content: str) -> List[Tuple[str, str, str]]:
        """
        解析 Markdown 中的链接 / Parse links from Markdown

        Args:
            content: Markdown 内容 / Markdown content

        Returns:
            链接列表 [(title, url, description), ...] / List of links
        """
        links = []

        # 匹配 Markdown 链接: [title](url) - description
        # 或者: - [title](url) - description
        pattern = r"[-*]?\s*\[([^\]]+)\]\(([^)]+)\)(?:\s*[-–—]\s*(.+?))?(?=\n|$)"
        matches = re.findall(pattern, content, re.MULTILINE)

        for match in matches:
            title = match[0].strip()
            url = match[1].strip()
            description = match[2].strip() if len(match) > 2 else ""

            # 过滤无效链接
            if not url or url.startswith("#") or url.startswith("mailto:"):
                continue

            # 规范化 URL
            if url.startswith("//"):
                url = "https:" + url
            elif not url.startswith("http"):
                continue

            links.append((title, url, description))

        return links

    def _filter_link(self, title: str, url: str, description: str, keywords: List[str]) -> bool:
        """
        过滤链接 / Filter link

        Args:
            title: 标题 / Title
            url: URL
            description: 描述 / Description
            keywords: 关键词列表 / Keyword list

        Returns:
            是否通过过滤 / Whether passed filter
        """
        # 排除非相关链接
        if not self._is_relevant_url(url):
            return False

        # 检查是否已存在
        if self._is_duplicate(url):
            return False

        # 如果有关键词限制，检查是否匹配
        if keywords:
            combined = f"{title} {description}".lower()
            has_keyword = any(kw.lower() in combined for kw in keywords)
            if not has_keyword:
                return False

        return True

    def _get_repo_info(self, owner: str, repo: str) -> Optional[dict]:
        """
        获取仓库信息 / Get repository info

        Args:
            owner: 仓库所有者 / Repository owner
            repo: 仓库名 / Repository name

        Returns:
            仓库信息 / Repository info
        """
        url = f"https://api.github.com/repos/{owner}/{repo}"

        headers = {"Accept": "application/vnd.github+json"}
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"

        response = self._make_request(url, headers=headers)

        if response:
            return response.json()

        return None

    def _create_resource_from_link(self, title: str, url: str, description: str, source_list: str) -> Optional[dict]:
        """
        从链接创建资源 / Create resource from link

        Args:
            title: 标题 / Title
            url: URL
            description: 描述 / Description
            source_list: 来源列表名称 / Source list name

        Returns:
            候选资源或 None / Candidate resource or None
        """
        # 如果是 GitHub 链接，尝试获取更多信息
        github_repo = self._extract_github_repo(url)
        stars = 0

        if github_repo and self.deep_parse:
            owner, repo = github_repo
            repo_info = self._get_repo_info(owner, repo)

            if repo_info:
                # 使用仓库描述补充信息
                if not description and repo_info.get("description"):
                    description = repo_info["description"]

                stars = repo_info.get("stargazers_count", 0)

                # 检查是否已归档
                if repo_info.get("archived", False):
                    return None

        return self.create_candidate_resource(
            url=url,
            title=title,
            description=description or title,
            author="",  # Awesome list 通常不提供作者信息
            author_url="",
            source_score=stars,  # 使用 star 数作为分数
            extra_metadata={
                "source_list": source_list,
                "github_stars": stars,
            },
        )

    def _crawl_awesome_list(self, list_config: dict) -> List[dict]:
        """
        爬取单个 Awesome List / Crawl single Awesome List

        Args:
            list_config: 列表配置 / List configuration

        Returns:
            发现的资源列表 / List of discovered resources
        """
        resources = []
        list_name = list_config.get("name", "Unknown")
        list_url = list_config.get("url", "")
        keywords = list_config.get("keywords", [])

        print(f"      爬取 {list_name}...")

        # 提取 GitHub repo 信息
        github_repo = self._extract_github_repo(list_url)
        if not github_repo:
            print("         ⚠️ 无效的 GitHub URL")
            return resources

        owner, repo = github_repo

        # 获取 README 内容
        readme_content = self._get_readme_content(owner, repo)
        if not readme_content:
            print("         ⚠️ 无法获取 README")
            return resources

        # 解析链接
        links = self._parse_markdown_links(readme_content)
        print(f"         找到 {len(links)} 个链接")

        # 过滤和处理链接
        processed_count = 0
        for title, url, description in links:
            if processed_count >= self.max_links_per_list:
                break

            if not self._filter_link(title, url, description, keywords):
                continue

            resource = self._create_resource_from_link(title, url, description, list_name)
            if resource:
                resources.append(resource)
                processed_count += 1

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

        print(f"   📋 爬取 {len(self.lists)} 个 Awesome Lists...")

        for list_config in self.lists:
            list_resources = self._crawl_awesome_list(list_config)

            for res in list_resources:
                url = res.get("PrimaryLink", "")
                if url not in seen_urls:
                    seen_urls.add(url)
                    resources.append(res)

        return resources
