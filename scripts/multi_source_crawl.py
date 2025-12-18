#!/usr/bin/env python3
"""
多源资源爬取脚本 / Multi-source Resource Crawl Script

统一运行所有爬虫，从多个来源发现与 Claude Code 相关的资源。
Runs all crawlers to discover Claude Code related resources from multiple sources.

用法 / Usage:
    python scripts/multi_source_crawl.py [--dry-run] [--sources SOURCE1,SOURCE2] [--limit N]
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

import yaml

# 添加项目根目录到 path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.crawlers import (
    RedditCrawler,
    AwesomeListCrawler,
    RSSCrawler,
    HackerNewsCrawler,
)


def load_config() -> dict:
    """加载爬虫配置 / Load crawler configuration"""
    config_file = PROJECT_ROOT / "config" / "crawlers.yaml"
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_available_crawlers() -> dict:
    """获取可用的爬虫 / Get available crawlers"""
    return {
        'reddit': RedditCrawler,
        'awesome': AwesomeListCrawler,
        'rss': RSSCrawler,
        'hackernews': HackerNewsCrawler,
    }


def run_crawler(
    crawler_class,
    config: dict,
    dry_run: bool = False,
    limit: int = 10
) -> tuple:
    """
    运行单个爬虫 / Run single crawler

    Args:
        crawler_class: 爬虫类 / Crawler class
        config: 配置 / Configuration
        dry_run: 是否为演示模式 / Whether in dry run mode
        limit: 最大资源数量 / Maximum number of resources

    Returns:
        (发现数量, 添加数量) / (discovered count, added count)
    """
    rate_limits = config.get('rate_limits', {})
    crawler = crawler_class(config, rate_limits)

    # 检查是否启用
    source_config = config.get(crawler.source_type, {})
    if not source_config.get('enabled', True):
        print(f"   ⏭️ {crawler.name} 已禁用，跳过")
        return 0, 0

    return crawler.run(dry_run=dry_run, limit=limit)


def main():
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(description='Multi-source resource crawl')
    parser.add_argument('--dry-run', action='store_true', help='Do not modify files')
    parser.add_argument('--sources', type=str, default='all',
                        help='Comma-separated list of sources (reddit,awesome,rss,hackernews) or "all"')
    parser.add_argument('--limit', type=int, default=10, help='Maximum resources per source')
    args = parser.parse_args()

    print("🕸️  多源资源爬取 / Multi-source Resource Crawl")
    print("=" * 50)

    # 加载配置
    print("\n📂 加载配置...")
    config = load_config()

    # 获取要运行的爬虫
    available_crawlers = get_available_crawlers()

    if args.sources == 'all':
        sources_to_run = list(available_crawlers.keys())
    else:
        sources_to_run = [s.strip().lower() for s in args.sources.split(',')]
        # 验证来源
        for source in sources_to_run:
            if source not in available_crawlers:
                print(f"❌ 未知的数据源: {source}")
                print(f"   可用: {', '.join(available_crawlers.keys())}")
                return 1

    print(f"   将运行: {', '.join(sources_to_run)}")

    if args.dry_run:
        print("   [Dry Run] 模式：不会保存任何数据")

    # 运行爬虫
    total_discovered = 0
    total_added = 0
    results = {}

    for source in sources_to_run:
        crawler_class = available_crawlers[source]

        try:
            discovered, added = run_crawler(
                crawler_class,
                config,
                dry_run=args.dry_run,
                limit=args.limit
            )

            results[source] = {'discovered': discovered, 'added': added}
            total_discovered += discovered
            total_added += added

        except Exception as e:
            print(f"   ❌ {source} 爬取失败: {e}")
            results[source] = {'discovered': 0, 'added': 0, 'error': str(e)}

    # 输出摘要
    print("\n" + "=" * 50)
    print("📊 爬取摘要 / Crawl Summary")
    print("=" * 50)

    print(f"\n{'来源':<15} {'发现':<10} {'添加':<10}")
    print("-" * 35)
    for source, result in results.items():
        discovered = result.get('discovered', 0)
        added = result.get('added', 0)
        error = result.get('error')

        if error:
            print(f"{source:<15} {'错误':<10} {error}")
        else:
            print(f"{source:<15} {discovered:<10} {added:<10}")

    print("-" * 35)
    print(f"{'总计':<15} {total_discovered:<10} {total_added:<10}")

    print("\n✅ 完成！")

    # 输出供 GitHub Actions 使用
    print(f"::set-output name=total_discovered::{total_discovered}")
    print(f"::set-output name=total_added::{total_added}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
