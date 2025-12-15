.PHONY: help generate validate sort migrate test test-verbose test-coverage test-all clean install

help:  ## 显示帮助信息 / Show help message
	@echo "AwesomeClaudeCode - Makefile 命令 / Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## 安装依赖 / Install dependencies
	@echo "📦 安装 Python 依赖..."
	python3 -m venv venv || true
	./venv/bin/pip install -r requirements.txt || ./venv/bin/pip install pyyaml
	@echo "✅ 依赖安装完成"

generate:  ## 生成 README.md / Generate README.md
	@echo "🚀 生成 README.md..."
	./venv/bin/python3 scripts/generate_readme.py
	@echo "✅ README.md 已生成"

validate:  ## 验证 CSV 数据 / Validate CSV data
	@echo "🔍 验证 CSV 数据..."
	./venv/bin/python3 scripts/validate_csv.py

migrate:  ## 从 README 迁移资源到 CSV / Migrate resources from README to CSV
	@echo "🔄 迁移资源到 CSV..."
	./venv/bin/python3 scripts/migrate_existing_resources.py

auto-fill:  ## 自动填充 GitHub 元数据 / Auto-fill GitHub metadata
	@echo "🤖 自动填充 GitHub 元数据..."
	./venv/bin/python3 scripts/auto_fill_github_metadata.py

sort:  ## 排序 CSV 文件 / Sort CSV file
	@echo "🔤 排序 CSV..."
	@echo "⚠️  sort 脚本尚未实现"

test:  ## 运行所有测试 / Run all tests
	@echo "🧪 运行测试..."
	@echo "📋 运行 CSV 验证测试..."
	@python3 tests/test_csv_validation.py || exit 1
	@echo ""
	@echo "📋 运行 README 生成测试..."
	@python3 tests/test_generate_readme.py || exit 1
	@echo ""
	@echo "📋 运行 SVG 生成测试..."
	@python3 tests/test_svg_generation.py || exit 1
	@echo ""
	@echo "📋 运行本地化测试..."
	@python3 tests/test_localization.py || exit 1
	@echo ""
	@echo "✅ 所有测试通过！"

test-verbose:  ## 运行测试（详细输出）/ Run tests with verbose output
	@echo "🧪 运行测试（详细模式）..."
	python3 tests/test_csv_validation.py
	python3 tests/test_generate_readme.py
	python3 tests/test_svg_generation.py
	python3 tests/test_localization.py

test-pytest:  ## 使用 pytest 运行测试 / Run tests with pytest
	@echo "🧪 使用 pytest 运行测试..."
	python3 -m pytest tests/ -v

test-coverage:  ## 运行测试并生成覆盖率报告 / Run tests with coverage
	@echo "🧪 运行测试并生成覆盖率..."
	python3 -m pytest tests/ --cov=scripts --cov-report=term-missing --cov-report=html
	@echo "📊 覆盖率报告已生成到 htmlcov/ 目录"

test-all:  ## 运行所有测试和检查 / Run all tests and checks
	@$(MAKE) test
	@echo ""
	@$(MAKE) validate

clean:  ## 清理生成的文件 / Clean generated files
	@echo "🧹 清理..."
	rm -rf __pycache__
	rm -rf scripts/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	find . -name "*.pyc" -delete
	@echo "✅ 清理完成"

check:  ## 检查所有内容 / Check everything
	@echo "🔍 运行所有检查..."
	@$(MAKE) validate
	@echo ""
	@$(MAKE) generate
	@echo ""
	@echo "✅ 所有检查完成"

# 开发相关命令 / Development commands

dev-setup:  ## 开发环境设置 / Setup development environment
	@echo "⚙️  设置开发环境..."
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install pyyaml
	@echo "尝试安装 PyGithub (可选)..."
	./venv/bin/pip install PyGithub || echo "PyGithub 安装失败，可稍后手动安装"
	@echo "✅ 开发环境设置完成"

quick:  ## 快速生成和验证 / Quick generate and validate
	@$(MAKE) generate
	@$(MAKE) validate

# Stage 相关命令 / Stage commands

stage-2:  ## Stage 2: 运行迁移 / Stage 2: Run migration
	@$(MAKE) migrate
	@$(MAKE) validate

stage-3:  ## Stage 3: 生成 README / Stage 3: Generate README
	@$(MAKE) generate
	@echo "📖 查看生成的 README.md"

# 默认目标 / Default target
.DEFAULT_GOAL := help
