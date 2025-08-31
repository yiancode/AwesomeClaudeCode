# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an "Awesome List" documentation project that curates Claude Code resources, best practices, tools, and projects. The content is primarily in Simplified Chinese and follows community-driven open source practices.

## Content Management Commands

```bash
# Check documentation structure and organization
find docs -name "*.md" | sort

# Verify all markdown links are valid (if markdown-link-check is installed)
find . -name "*.md" -not -path "./node_modules/*" -exec markdown-link-check {} \;

# Check for broken internal links
grep -r "\[.*\](" docs/ examples/ --include="*.md"

# Format markdown files (if prettier is available)
npx prettier --write "**/*.md"

# Validate project structure matches README navigation
diff <(grep -o "docs/[^)]*\.md" README.md | sort) <(find docs -name "*.md" | sort)
```

## Project Architecture

### Content Organization
- `docs/` - Hierarchical documentation organized by topic areas:
  - `installation/` - Setup guides for different platforms
  - `getting-started/` - Beginner tutorials and first-time user guides  
  - `advanced/` - Advanced features like MCP, agents, and complex workflows
  - `case-studies/` - Real-world usage patterns and best practices
  - `ecosystem/` - Community resources and third-party integrations
  - `third-party/` - External tools and IDE integrations
  - `open-source/` - Related open source projects and contributions

- `examples/` - Practical code examples and complete tutorials:
  - Organized by technology stack (web, mobile, data-science, devops)
  - Each example includes complete working code and detailed explanations
  - Examples demonstrate real Claude Code usage patterns and workflows

### Content Standards
- All content uses Simplified Chinese with English for code examples and technical terms
- Documentation follows a consistent structure with clear headings and navigation
- Code examples include both the interaction with Claude Code and the resulting artifacts
- Each major section includes practical examples and actionable guidance

### Community Integration
- GitHub issue templates in `.github/ISSUE_TEMPLATE/` for bug reports and feature requests
- Contribution guidelines in `CONTRIBUTING.md` specify content standards and review process
- MIT license supports open collaboration and reuse

## Content Development Workflow

When adding new content:

1. **Determine appropriate location** in the docs/ hierarchy based on user skill level and topic area
2. **Follow existing content patterns** - examine similar documents for structure and style
3. **Include practical examples** - every concept should have actionable Claude Code usage examples
4. **Update navigation** - add new content to README.md table of contents and relevant cross-references
5. **Verify internal links** - ensure all references to other documentation are correct

When creating examples:

1. **Provide complete context** - include the full Claude Code conversation flow
2. **Include working code** - all code examples should be functional and tested
3. **Explain the process** - show both the user input and Claude's reasoning/approach
4. **Link to related documentation** - connect examples to relevant guides in docs/

## Key Files and Their Purposes

- `README.md` - Main project entry point with comprehensive navigation to all resources
- `CONTRIBUTING.md` - Community guidelines including content standards and review process  
- `docs/installation/configuration.md` - Central configuration reference covering all Claude Code setup options
- `docs/advanced/mcp.md` - Comprehensive guide to Model Context Protocol integration
- `examples/web/simple-todo-app.md` - Complete tutorial showing Claude Code development workflow

The project serves as both a learning resource for new Claude Code users and a comprehensive reference for advanced practitioners.