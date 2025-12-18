#!/usr/bin/env python3
"""
AI 增强脚本 / AI Enhancement Script

使用 AI 对候选资源进行智能增强：
1. 智能分类推断
2. 中英文描述生成
3. 相关性评估
4. 标签建议

支持 Anthropic Claude 和 OpenAI 两种 AI 提供商。

用法 / Usage:
    python scripts/ai_enhance.py [--enhance-pending] [--provider anthropic|openai]
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yaml

# 项目根目录 / Project root
PROJECT_ROOT = Path(__file__).parent.parent


def load_config() -> dict:
    """加载 AI 配置 / Load AI configuration"""
    config_file = PROJECT_ROOT / "config" / "ai_config.yaml"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def load_categories() -> List[dict]:
    """加载分类定义 / Load category definitions"""
    categories_file = PROJECT_ROOT / "templates" / "categories.yaml"
    with open(categories_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data.get('categories', [])


def load_pending_resources() -> List[dict]:
    """加载待审核资源 / Load pending resources"""
    pending_file = PROJECT_ROOT / 'candidates' / 'pending_resources.json'
    if pending_file.exists():
        with open(pending_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('resources', [])
    return []


def save_pending_resources(resources: List[dict]):
    """保存待审核资源 / Save pending resources"""
    pending_file = PROJECT_ROOT / 'candidates' / 'pending_resources.json'
    data = {
        "_comment": "候选资源队列 - 待审核的资源",
        "_schema_version": "1.0",
        "resources": resources
    }
    with open(pending_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_cache() -> dict:
    """加载 AI 缓存 / Load AI cache"""
    cache_file = PROJECT_ROOT / 'candidates' / 'ai_cache.json'
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_cache(cache: dict):
    """保存 AI 缓存 / Save AI cache"""
    cache_file = PROJECT_ROOT / 'candidates' / 'ai_cache.json'
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


class AIProvider:
    """AI 提供商基类 / AI Provider Base Class"""

    def __init__(self, config: dict):
        self.config = config

    def call(self, prompt: str) -> Optional[str]:
        """调用 AI / Call AI"""
        raise NotImplementedError


class AnthropicProvider(AIProvider):
    """Anthropic Claude 提供商 / Anthropic Claude Provider"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.model = config.get('model', 'claude-3-haiku-20240307')
        self.max_tokens = config.get('max_tokens', 1024)
        self.temperature = config.get('temperature', 0.3)

    def call(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            print("   ⚠️ ANTHROPIC_API_KEY 未设置")
            return None

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        data = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('content', [{}])[0].get('text', '')
        except Exception as e:
            print(f"   ⚠️ Anthropic API 错误: {e}")
            return None


class OpenAIProvider(AIProvider):
    """OpenAI 提供商 / OpenAI Provider"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = config.get('model', 'gpt-3.5-turbo')
        self.max_tokens = config.get('max_tokens', 1024)
        self.temperature = config.get('temperature', 0.3)

    def call(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            print("   ⚠️ OPENAI_API_KEY 未设置")
            return None

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('choices', [{}])[0].get('message', {}).get('content', '')
        except Exception as e:
            print(f"   ⚠️ OpenAI API 错误: {e}")
            return None


class LocalEnhancer:
    """本地增强器（不使用 AI）/ Local Enhancer (without AI)"""

    def __init__(self, config: dict, categories: List[dict]):
        self.config = config
        self.categories = categories
        self.category_map = {cat['id']: cat for cat in categories}

    def infer_category(self, resource: dict) -> dict:
        """基于规则推断分类 / Rule-based category inference"""
        name = resource.get('DisplayName', '').lower()
        description = (resource.get('Description', '') or '').lower()
        url = resource.get('PrimaryLink', '').lower()
        combined = f"{name} {description} {url}"

        # 分类规则
        rules = [
            ('mcp-servers', ['mcp', 'model context protocol', 'mcp-server']),
            ('hooks', ['hook', 'pre-commit', 'post-commit']),
            ('slash-commands', ['slash', 'command', '/command']),
            ('statusline', ['status', 'statusline', 'status-line']),
            ('workflows', ['workflow', 'guide', 'tutorial', 'best practice']),
            ('tooling', ['tool', 'extension', 'plugin', 'vscode', 'neovim']),
            ('skills', ['skill', 'agent skill']),
            ('claude-md-files', ['claude.md', 'claudemd']),
            ('alternative-clients', ['client', 'terminal', 'cli', 'tui']),
            ('open-source-projects', ['open source', 'project', 'framework']),
        ]

        for category_id, keywords in rules:
            for keyword in keywords:
                if keyword in combined:
                    return {
                        'category': category_id,
                        'subcategory': 'general',
                        'confidence': 0.7,
                        'reason': f'Matched keyword: {keyword}'
                    }

        return {
            'category': 'ecosystem',
            'subcategory': 'general',
            'confidence': 0.5,
            'reason': 'Default category'
        }

    def generate_description(self, resource: dict) -> dict:
        """基于现有信息生成描述 / Generate description from existing info"""
        original = resource.get('Description', '') or resource.get('Description_ZH', '')

        # 如果已有描述，直接使用
        if original:
            return {
                'description_en': original,
                'description_zh': resource.get('Description_ZH', '') or original
            }

        # 从名称生成简单描述
        name = resource.get('DisplayName', '')
        return {
            'description_en': f"A Claude Code related resource: {name}",
            'description_zh': f"Claude Code 相关资源：{name}"
        }

    def assess_relevance(self, resource: dict) -> dict:
        """基于规则评估相关性 / Rule-based relevance assessment"""
        name = resource.get('DisplayName', '').lower()
        description = (resource.get('Description', '') or '').lower()
        url = resource.get('PrimaryLink', '').lower()
        combined = f"{name} {description} {url}"

        score = 0
        tags = []

        # 高相关性关键词
        high_keywords = {
            'claude code': 30, 'claude-code': 30,
            'mcp server': 25, 'mcp-server': 25,
            'model context protocol': 25,
            'anthropic': 20,
        }

        for keyword, points in high_keywords.items():
            if keyword in combined:
                score += points

        # 中等相关性关键词
        medium_keywords = {
            'claude': 15, 'llm': 10, 'ai assistant': 10,
            'ai coding': 10, 'prompt': 5,
        }

        for keyword, points in medium_keywords.items():
            if keyword in combined:
                score += points

        # 推断标签
        tag_keywords = {
            'claude-code': ['claude', 'claude code', 'claude-code'],
            'mcp-server': ['mcp', 'model context protocol'],
            'cli-tool': ['cli', 'terminal', 'command line'],
            'vscode-extension': ['vscode', 'vs code'],
            'workflow': ['workflow', 'guide'],
        }

        for tag, keywords in tag_keywords.items():
            if any(kw in combined for kw in keywords):
                tags.append(tag)

        # 确定相关性级别
        if score >= 50:
            level = 'direct'
        elif score >= 30:
            level = 'indirect'
        elif score >= 15:
            level = 'ecosystem'
        else:
            level = 'unrelated'

        return {
            'relevance_score': min(100, score),
            'relevance_level': level,
            'reason': f'Keyword-based scoring: {score} points',
            'suggested_tags': tags[:5]
        }


class AIEnhancer:
    """AI 增强器 / AI Enhancer"""

    def __init__(self, config: dict, provider_name: str = 'anthropic'):
        self.config = config
        self.categories = load_categories()

        # 选择 AI 提供商
        provider_config = config.get('provider', {}).get(provider_name, {})

        if provider_name == 'anthropic':
            self.provider = AnthropicProvider(provider_config)
        elif provider_name == 'openai':
            self.provider = OpenAIProvider(provider_config)
        else:
            self.provider = None

        # 本地增强器作为后备
        self.local_enhancer = LocalEnhancer(config, self.categories)

        # 批处理配置
        batch_config = config.get('batch', {})
        self.request_interval = batch_config.get('request_interval', 1.0)
        self.max_retries = batch_config.get('max_retries', 3)

        # 缓存
        self.cache = load_cache()

    def _format_categories(self) -> str:
        """格式化分类列表 / Format category list"""
        lines = []
        for cat in self.categories:
            lines.append(f"- {cat['id']}: {cat['name']} ({cat['name_zh']})")
            if cat.get('subcategories'):
                for sub in cat['subcategories']:
                    lines.append(f"  - {sub['id']}: {sub['name']}")
        return '\n'.join(lines)

    def _parse_json_response(self, response: str) -> Optional[dict]:
        """解析 AI JSON 响应 / Parse AI JSON response"""
        if not response:
            return None

        # 尝试提取 JSON
        try:
            # 直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 尝试从 markdown 代码块提取
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试从花括号提取
        brace_match = re.search(r'\{[\s\S]*\}', response)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def enhance_classification(self, resource: dict) -> dict:
        """增强分类 / Enhance classification"""
        # 检查缓存
        cache_key = f"classify_{resource.get('PrimaryLink', '')}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 如果没有 AI 提供商，使用本地增强
        if not self.provider:
            return self.local_enhancer.infer_category(resource)

        # 构建提示
        prompt_template = self.config.get('classification', {}).get('prompt_template', '')
        if not prompt_template:
            return self.local_enhancer.infer_category(resource)

        prompt = prompt_template.format(
            name=resource.get('DisplayName', ''),
            url=resource.get('PrimaryLink', ''),
            description=resource.get('Description', '') or resource.get('Description_ZH', ''),
            language=resource.get('_language', ''),
            topics=', '.join(resource.get('_topics', [])),
            categories=self._format_categories()
        )

        # 调用 AI
        response = self.provider.call(prompt)
        result = self._parse_json_response(response)

        if result:
            self.cache[cache_key] = result
            return result

        # 回退到本地增强
        return self.local_enhancer.infer_category(resource)

    def enhance_description(self, resource: dict) -> dict:
        """增强描述 / Enhance description"""
        # 检查缓存
        cache_key = f"describe_{resource.get('PrimaryLink', '')}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 如果没有 AI 提供商，使用本地增强
        if not self.provider:
            return self.local_enhancer.generate_description(resource)

        # 构建提示
        prompt_template = self.config.get('description', {}).get('prompt_template', '')
        max_length = self.config.get('description', {}).get('max_length', 200)

        if not prompt_template:
            return self.local_enhancer.generate_description(resource)

        prompt = prompt_template.format(
            name=resource.get('DisplayName', ''),
            url=resource.get('PrimaryLink', ''),
            original_description=resource.get('Description', '') or resource.get('Description_ZH', ''),
            readme_summary='',  # 可以扩展为获取 README
            max_length=max_length
        )

        # 调用 AI
        response = self.provider.call(prompt)
        result = self._parse_json_response(response)

        if result:
            self.cache[cache_key] = result
            return result

        return self.local_enhancer.generate_description(resource)

    def enhance_relevance(self, resource: dict) -> dict:
        """增强相关性评估 / Enhance relevance assessment"""
        # 检查缓存
        cache_key = f"relevance_{resource.get('PrimaryLink', '')}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 如果没有 AI 提供商，使用本地增强
        if not self.provider:
            return self.local_enhancer.assess_relevance(resource)

        # 构建提示
        prompt_template = self.config.get('relevance', {}).get('prompt_template', '')

        if not prompt_template:
            return self.local_enhancer.assess_relevance(resource)

        prompt = prompt_template.format(
            name=resource.get('DisplayName', ''),
            url=resource.get('PrimaryLink', ''),
            description=resource.get('Description', '') or resource.get('Description_ZH', ''),
            resource_type=resource.get('Category', '')
        )

        # 调用 AI
        response = self.provider.call(prompt)
        result = self._parse_json_response(response)

        if result:
            self.cache[cache_key] = result
            return result

        return self.local_enhancer.assess_relevance(resource)

    def enhance_resource(self, resource: dict) -> dict:
        """完整增强单个资源 / Fully enhance single resource"""
        enhanced = resource.copy()

        print(f"   📌 增强: {resource.get('DisplayName', 'Unknown')}")

        # 1. 分类增强
        if self.config.get('classification', {}).get('enabled', True):
            classification = self.enhance_classification(resource)
            if classification.get('confidence', 0) >= \
               self.config.get('classification', {}).get('confidence_threshold', 0.7):
                enhanced['Category'] = classification.get('category', enhanced.get('Category'))
                enhanced['SubCategory'] = classification.get('subcategory', enhanced.get('SubCategory', 'general'))
            enhanced['_classification'] = classification
            time.sleep(self.request_interval)

        # 2. 描述增强
        if self.config.get('description', {}).get('enabled', True):
            description = self.enhance_description(resource)
            if description.get('description_en'):
                enhanced['Description'] = description['description_en']
            if description.get('description_zh'):
                enhanced['Description_ZH'] = description['description_zh']
            enhanced['_description_enhanced'] = True
            time.sleep(self.request_interval)

        # 3. 相关性评估
        if self.config.get('relevance', {}).get('enabled', True):
            relevance = self.enhance_relevance(resource)
            enhanced['_relevance_score'] = relevance.get('relevance_score', 0)
            enhanced['_relevance_level'] = relevance.get('relevance_level', 'unknown')
            enhanced['_suggested_tags'] = relevance.get('suggested_tags', [])
            time.sleep(self.request_interval)

        enhanced['_enhanced_at'] = datetime.now().isoformat()

        return enhanced

    def enhance_all_pending(self, limit: int = 10) -> List[dict]:
        """增强所有待审核资源 / Enhance all pending resources"""
        pending = load_pending_resources()
        enhanced_resources = []

        for i, resource in enumerate(pending[:limit]):
            print(f"\n   [{i+1}/{min(len(pending), limit)}]", end='')
            enhanced = self.enhance_resource(resource)
            enhanced_resources.append(enhanced)

        # 保存缓存
        save_cache(self.cache)

        return enhanced_resources


def main():
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(description='AI Enhancement')
    parser.add_argument('--enhance-pending', action='store_true', help='Enhance pending resources')
    parser.add_argument('--provider', choices=['anthropic', 'openai', 'local'],
                        default='local', help='AI provider')
    parser.add_argument('--limit', type=int, default=10, help='Maximum resources to enhance')
    parser.add_argument('--save', action='store_true', help='Save enhanced resources')
    args = parser.parse_args()

    print("🧠 AI 增强 / AI Enhancement")
    print("=" * 50)

    # 加载配置
    config = load_config()

    # 检查 API key
    if args.provider == 'anthropic' and not os.environ.get('ANTHROPIC_API_KEY'):
        print("⚠️  ANTHROPIC_API_KEY 未设置，将使用本地增强")
        args.provider = 'local'
    elif args.provider == 'openai' and not os.environ.get('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY 未设置，将使用本地增强")
        args.provider = 'local'

    print(f"\n📋 使用提供商: {args.provider}")

    # 创建增强器
    if args.provider == 'local':
        enhancer = AIEnhancer(config, provider_name=None)
        enhancer.provider = None
    else:
        enhancer = AIEnhancer(config, provider_name=args.provider)

    # 增强待审核资源
    if args.enhance_pending:
        print(f"\n🔄 增强待审核资源 (限制: {args.limit})...")

        enhanced = enhancer.enhance_all_pending(limit=args.limit)

        print(f"\n✅ 增强完成: {len(enhanced)} 个资源")

        # 显示结果
        for res in enhanced:
            print(f"\n   {res.get('DisplayName', 'Unknown')}")
            print(f"      分类: {res.get('Category')}/{res.get('SubCategory', 'general')}")
            print(f"      相关性: {res.get('_relevance_score', 0)}/100 ({res.get('_relevance_level', 'unknown')})")
            if res.get('_suggested_tags'):
                print(f"      标签: {', '.join(res.get('_suggested_tags', []))}")

        # 保存
        if args.save:
            # 更新 pending 资源
            pending = load_pending_resources()
            enhanced_ids = {r.get('ID') for r in enhanced}

            updated_pending = []
            for res in pending:
                if res.get('ID') in enhanced_ids:
                    # 找到对应的增强版本
                    for e in enhanced:
                        if e.get('ID') == res.get('ID'):
                            updated_pending.append(e)
                            break
                else:
                    updated_pending.append(res)

            save_pending_resources(updated_pending)
            print("\n💾 已保存增强结果")

        return 0

    # 默认显示帮助
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
