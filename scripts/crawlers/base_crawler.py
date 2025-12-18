#!/usr/bin/env python3
"""
爬虫基类 / Base Crawler Class

所有爬虫的抽象基类，定义通用接口和工具方法。
Abstract base class for all crawlers, defines common interface and utility methods.
"""

import csv
import hashlib
import json
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import requests
import yaml


class BaseCrawler(ABC):
    """爬虫基类 / Base crawler class"""

    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent.parent

    def __init__(self, config: dict, rate_limit_config: Optional[dict] = None):
        """
        初始化爬虫 / Initialize crawler

        Args:
            config: 爬虫配置 / Crawler configuration
            rate_limit_config: 速率限制配置 / Rate limit configuration
        """
        self.config = config
        self.rate_limit_config = rate_limit_config or {}
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "AwesomeClaudeCode-Bot/1.0 (+https://github.com/yiancode/AwesomeClaudeCode)"}
        )

        # 加载分类配置
        self._categories_prefix = self._load_categories()

        # 加载已存在的 URL
        self._existing_urls = self._load_existing_urls()

        # 速率限制状态
        self._last_request_time = 0

    @property
    @abstractmethod
    def name(self) -> str:
        """爬虫名称 / Crawler name"""
        pass

    @property
    @abstractmethod
    def source_type(self) -> str:
        """数据源类型 / Data source type"""
        pass

    @abstractmethod
    def crawl(self) -> List[dict]:
        """
        执行爬取 / Execute crawl

        Returns:
            发现的资源列表 / List of discovered resources
        """
        pass

    def _load_categories(self) -> dict:
        """加载分类定义 / Load category definitions"""
        categories_file = self.PROJECT_ROOT / "templates" / "categories.yaml"
        with open(categories_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return {cat["id"]: cat["prefix"] for cat in data["categories"]}

    def _load_existing_urls(self) -> Set[str]:
        """加载所有已存在的资源 URL / Load all existing resource URLs"""
        urls = set()

        # 从 CSV 加载
        csv_file = self.PROJECT_ROOT / "THE_RESOURCES_TABLE.csv"
        if csv_file.exists():
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = self._normalize_url(row.get("PrimaryLink", ""))
                    if url:
                        urls.add(url)

        # 从 pending 加载
        pending_file = self.PROJECT_ROOT / "candidates" / "pending_resources.json"
        if pending_file.exists():
            with open(pending_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for res in data.get("resources", []):
                    url = self._normalize_url(res.get("PrimaryLink", ""))
                    if url:
                        urls.add(url)

        # 从 rejected 加载
        rejected_file = self.PROJECT_ROOT / "candidates" / "rejected_resources.json"
        if rejected_file.exists():
            with open(rejected_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for res in data.get("resources", []):
                    url = self._normalize_url(res.get("PrimaryLink", ""))
                    if url:
                        urls.add(url)

        return urls

    def _normalize_url(self, url: str) -> str:
        """规范化 URL / Normalize URL"""
        if not url:
            return ""
        return url.strip().rstrip("/").lower()

    def _is_duplicate(self, url: str) -> bool:
        """检查 URL 是否已存在 / Check if URL already exists"""
        normalized = self._normalize_url(url)
        return normalized in self._existing_urls

    def _rate_limit(self):
        """执行速率限制 / Apply rate limiting"""
        min_interval = self.rate_limit_config.get("min_request_interval", 1.0)
        elapsed = time.time() - self._last_request_time

        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

        self._last_request_time = time.time()

    def _make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """
        发起 HTTP 请求（带速率限制）
        Make HTTP request (with rate limiting)
        """
        self._rate_limit()

        timeout = kwargs.pop("timeout", 30)

        try:
            response = self.session.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ 请求失败 [{url}]: {e}")
            return None

    def _extract_github_url(self, text: str) -> Optional[str]:
        """
        从文本中提取 GitHub URL
        Extract GitHub URL from text
        """
        # 匹配 GitHub 仓库 URL
        pattern = r"https?://github\.com/[\w\-]+/[\w\-\.]+"
        match = re.search(pattern, text)
        if match:
            url = match.group(0)
            # 清理 URL（移除 .git 等后缀）
            url = re.sub(r"\.git$", "", url)
            url = re.sub(r"[/\?#].*$", "", url)
            return url
        return None

    def _extract_urls(self, text: str) -> List[str]:
        """
        从文本中提取所有 URL
        Extract all URLs from text
        """
        pattern = r"https?://[^\s<>\"\'\)\]]+[^\s<>\"\'\)\]\.,;:!?]"
        urls = re.findall(pattern, text)
        return list(set(urls))

    def _is_relevant_url(self, url: str) -> bool:
        """
        检查 URL 是否相关（过滤掉不相关的链接）
        Check if URL is relevant (filter out irrelevant links)
        """
        # 排除常见的非资源链接
        excluded_domains = [
            "twitter.com",
            "x.com",
            "facebook.com",
            "linkedin.com",
            "youtube.com",
            "youtu.be",
            "reddit.com",
            "imgur.com",
            "medium.com",
            "dev.to",
            "news.ycombinator.com",
            "google.com",
            "bing.com",
            "amazon.com",
            "ebay.com",
        ]

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        for excluded in excluded_domains:
            if excluded in domain:
                return False

        # 优先 GitHub 链接
        if "github.com" in domain:
            return True

        # 其他技术相关域名
        relevant_domains = [
            "gitlab.com",
            "bitbucket.org",
            "npmjs.com",
            "pypi.org",
            "crates.io",
            "pkg.go.dev",
            "anthropic.com",
            "claude.ai",
        ]

        for relevant in relevant_domains:
            if relevant in domain:
                return True

        return False

    def _generate_resource_id(self, category_id: str, url: str) -> str:
        """生成资源 ID / Generate resource ID"""
        prefix = self._categories_prefix.get(category_id, "res")
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"{prefix}-{url_hash}"

    def _infer_category(self, title: str, description: str, url: str) -> str:
        """
        推断资源分类 / Infer resource category

        Args:
            title: 标题 / Title
            description: 描述 / Description
            url: URL

        Returns:
            分类 ID / Category ID
        """
        combined = f"{title} {description}".lower()

        # 基于关键词推断分类
        if "mcp" in combined or "model context protocol" in combined:
            return "mcp-servers"
        if "hook" in combined:
            return "hooks"
        if "slash" in combined or "command" in combined:
            return "slash-commands"
        if "workflow" in combined or "guide" in combined:
            return "workflows"
        if "tool" in combined or "extension" in combined or "plugin" in combined:
            return "tooling"
        if "skill" in combined:
            return "skills"
        if "status" in combined or "statusline" in combined:
            return "statusline"
        if "claude.md" in combined:
            return "claude-md-files"
        if "client" in combined or "terminal" in combined or "cli" in combined:
            return "alternative-clients"

        return "ecosystem"

    def _calculate_relevance_score(
        self,
        title: str,
        description: str,
        url: str,
        score: int = 0,  # 来源平台的分数（如 Reddit upvotes）
    ) -> int:
        """
        计算相关性评分 / Calculate relevance score

        Returns:
            相关性评分 (0-100) / Relevance score (0-100)
        """
        relevance = 0
        combined = f"{title} {description}".lower()

        # 高相关性关键词
        high_keywords = ["claude code", "claude-code", "anthropic", "mcp server", "model context protocol"]
        for keyword in high_keywords:
            if keyword in combined:
                relevance += 25

        # 中等相关性关键词
        medium_keywords = ["claude", "mcp", "llm tool", "ai assistant", "ai coding"]
        for keyword in medium_keywords:
            if keyword in combined:
                relevance += 15

        # GitHub 链接加分
        if "github.com" in url:
            relevance += 10

        # 基于来源平台分数加分
        if score >= 100:
            relevance += 20
        elif score >= 50:
            relevance += 15
        elif score >= 20:
            relevance += 10
        elif score >= 10:
            relevance += 5

        return min(100, relevance)

    def create_candidate_resource(
        self,
        url: str,
        title: str,
        description: str,
        author: str = "",
        author_url: str = "",
        source_score: int = 0,
        extra_metadata: Optional[dict] = None,
    ) -> dict:
        """
        创建候选资源 / Create candidate resource

        Args:
            url: 资源 URL / Resource URL
            title: 标题 / Title
            description: 描述 / Description
            author: 作者 / Author
            author_url: 作者主页 / Author URL
            source_score: 来源平台分数 / Source platform score
            extra_metadata: 额外元数据 / Extra metadata

        Returns:
            候选资源字典 / Candidate resource dict
        """
        category_id = self._infer_category(title, description, url)
        resource_id = self._generate_resource_id(category_id, url)
        relevance_score = self._calculate_relevance_score(title, description, url, source_score)

        today = datetime.now().strftime("%Y/%m/%d")

        # 截断过长的描述
        if len(description) > 200:
            description = description[:197] + "..."

        resource = {
            "ID": resource_id,
            "DisplayName": title,
            "DisplayName_ZH": title,  # 需要人工翻译
            "Category": category_id,
            "SubCategory": "general",
            "PrimaryLink": url,
            "SecondaryLink": "",
            "Author": author,
            "AuthorProfile": author_url,
            "IsActive": "TRUE",
            "DateAdded": today,
            "LastModified": today,
            "LastChecked": today,
            "License": "",
            "Description": description,
            "Description_ZH": "",  # 需要人工翻译
            "Tags_ZH": "",
            "IsPinned": "FALSE",
            "Section": "community",
            # 元数据
            "_source": self.source_type,
            "_source_crawler": self.name,
            "_discovered_at": datetime.now().isoformat(),
            "_status": "pending",
            "_relevance_score": relevance_score,
            "_source_score": source_score,
        }

        # 添加额外元数据
        if extra_metadata:
            for key, value in extra_metadata.items():
                resource[f"_{key}"] = value

        return resource

    def save_to_pending(self, resources: List[dict]) -> int:
        """
        保存资源到待审核队列 / Save resources to pending queue

        Args:
            resources: 资源列表 / List of resources

        Returns:
            添加的资源数量 / Number of resources added
        """
        pending_file = self.PROJECT_ROOT / "candidates" / "pending_resources.json"

        if pending_file.exists():
            with open(pending_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"_comment": "候选资源队列 - 待审核的资源", "_schema_version": "1.0", "resources": []}

        added_count = 0
        for resource in resources:
            # 再次检查重复
            url = self._normalize_url(resource.get("PrimaryLink", ""))
            if url and url not in self._existing_urls:
                data["resources"].append(resource)
                self._existing_urls.add(url)
                added_count += 1

        with open(pending_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return added_count

    def run(self, dry_run: bool = False, limit: int = 10) -> Tuple[int, int]:
        """
        运行爬虫 / Run crawler

        Args:
            dry_run: 是否为演示模式 / Whether in dry run mode
            limit: 最大资源数量 / Maximum number of resources

        Returns:
            (发现数量, 添加数量) / (discovered count, added count)
        """
        print(f"\n🕷️  运行 {self.name} 爬虫...")

        try:
            resources = self.crawl()
        except Exception as e:
            print(f"   ❌ 爬取失败: {e}")
            return 0, 0

        # 过滤重复
        unique_resources = []
        for res in resources:
            url = res.get("PrimaryLink", "")
            if not self._is_duplicate(url):
                unique_resources.append(res)

        # 按相关性排序
        unique_resources.sort(key=lambda x: x.get("_relevance_score", 0), reverse=True)

        # 限制数量
        unique_resources = unique_resources[:limit]

        discovered_count = len(unique_resources)
        print(f"   📊 发现 {discovered_count} 个新资源")

        if not unique_resources:
            return 0, 0

        # 显示发现的资源
        for res in unique_resources:
            print(f"   📌 {res['DisplayName']}")
            print(f"      URL: {res['PrimaryLink']}")
            print(f"      分类: {res['Category']}")
            print(f"      相关性: {res.get('_relevance_score', 0)}/100")

        if dry_run:
            print("   [Dry Run] 跳过保存")
            return discovered_count, 0

        # 保存到待审核队列
        added_count = self.save_to_pending(unique_resources)
        print(f"   ✅ 已添加 {added_count} 个资源到候选队列")

        return discovered_count, added_count
