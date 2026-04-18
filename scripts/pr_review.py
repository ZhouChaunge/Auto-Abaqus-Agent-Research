#!/usr/bin/env python3
"""
AI PR Review Script / AI 代码审查脚本

This script analyzes PR diffs and generates code review comments using LLM.
支持多种国产大模型进行代码审查。

Usage:
    python pr_review.py --diff-file pr_diff.txt --output review.md
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

import litellm


# Model mapping (same as client.py)
MODEL_MAPPING = {
    # OpenAI
    "gpt-4o": "gpt-4o",
    "gpt-4-turbo": "gpt-4-turbo",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    
    # Anthropic
    "claude-3-opus": "claude-3-opus-20240229",
    "claude-3-sonnet": "claude-3-sonnet-20240229",
    
    # 智谱 GLM
    "glm-4": "zhipu/glm-4",
    "glm-3-turbo": "zhipu/glm-3-turbo",
    
    # 通义千问
    "qwen-max": "dashscope/qwen-max",
    "qwen-plus": "dashscope/qwen-plus",
    
    # DeepSeek
    "deepseek-chat": "deepseek/deepseek-chat",
    "deepseek-coder": "deepseek/deepseek-coder",
    
    # 月之暗面 Moonshot
    "moonshot-v1-8k": "moonshot/moonshot-v1-8k",
    "moonshot-v1-32k": "moonshot/moonshot-v1-32k",
    
    # 硅基流动 SiliconFlow
    "siliconflow-deepseek": "openai/deepseek-ai/DeepSeek-V2.5",
}


REVIEW_PROMPT_EN = """You are an expert code reviewer. Analyze the following PR diff and provide a comprehensive code review.

## PR Information
- Title: {pr_title}
- Description: {pr_body}

## Code Diff
```diff
{diff_content}
```

## Review Guidelines
Please review the code changes and provide feedback on:

1. **Code Quality** - Clean code, readability, maintainability
2. **Potential Bugs** - Logic errors, edge cases, null checks
3. **Performance** - Efficiency, unnecessary operations
4. **Security** - Input validation, sensitive data handling
5. **Best Practices** - Design patterns, conventions, documentation

## Output Format
Provide your review in the following format:

### ✅ Strengths
- List positive aspects of the code

### ⚠️ Issues Found
- List issues with severity (🔴 Critical, 🟡 Warning, 🔵 Suggestion)
- Include file path and line number if applicable

### 💡 Suggestions
- Provide actionable improvement suggestions

### 📊 Overall Assessment
- Brief summary and recommendation (Approve / Request Changes / Comment)
"""

REVIEW_PROMPT_BILINGUAL = """You are an expert code reviewer. Analyze the following PR diff and provide a comprehensive code review in both English and Chinese.

## PR Information
- Title: {pr_title}
- Description: {pr_body}

## Code Diff
```diff
{diff_content}
```

## Review Guidelines / 审查指南
Please review the code and provide feedback on / 请审查代码并提供以下方面的反馈:

1. **Code Quality / 代码质量** - Clean code, readability / 代码整洁性、可读性
2. **Potential Bugs / 潜在问题** - Logic errors, edge cases / 逻辑错误、边界情况
3. **Performance / 性能** - Efficiency / 效率优化
4. **Security / 安全性** - Input validation / 输入验证
5. **Best Practices / 最佳实践** - Conventions, documentation / 规范、文档

## Output Format / 输出格式

### ✅ Strengths / 优点
- [EN] List positive aspects
- [中文] 列出优点

### ⚠️ Issues Found / 发现的问题
- 🔴 Critical / 严重: [description]
- 🟡 Warning / 警告: [description]  
- 🔵 Suggestion / 建议: [description]

### 💡 Suggestions / 改进建议
- [EN] Actionable suggestions
- [中文] 可操作的建议

### 📊 Overall Assessment / 总体评估
- [EN] Summary and recommendation
- [中文] 总结和建议 (Approve 通过 / Request Changes 需修改 / Comment 仅评论)
"""

REVIEW_PROMPT_CN = """你是一位专业的代码审查专家。请分析以下 PR 的代码变更，并提供全面的代码审查意见。

## PR 信息
- 标题: {pr_title}
- 描述: {pr_body}

## 代码变更
```diff
{diff_content}
```

## 审查指南
请审查代码并提供以下方面的反馈：

1. **代码质量** - 代码整洁性、可读性、可维护性
2. **潜在问题** - 逻辑错误、边界情况、空值检查
3. **性能** - 效率、不必要的操作
4. **安全性** - 输入验证、敏感数据处理
5. **最佳实践** - 设计模式、代码规范、文档

## 输出格式

### ✅ 优点
- 列出代码的优点

### ⚠️ 发现的问题
- 🔴 严重: [描述问题，包含文件路径和行号]
- 🟡 警告: [描述问题]
- 🔵 建议: [描述建议]

### 💡 改进建议
- 提供可操作的改进建议

### 📊 总体评估
- 简要总结和建议 (通过 / 需修改 / 仅评论)
"""


def setup_api_keys():
    """Configure API keys from environment."""
    # LiteLLM will automatically pick up these env vars
    env_keys = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", 
        "ZHIPUAI_API_KEY",
        "DASHSCOPE_API_KEY",
        "DEEPSEEK_API_KEY",
        "MOONSHOT_API_KEY",
        "SILICONFLOW_API_KEY",
    ]
    
    # Map GitHub Secrets naming to LiteLLM expected names
    if os.getenv("ZHIPU_API_KEY"):
        os.environ["ZHIPUAI_API_KEY"] = os.getenv("ZHIPU_API_KEY")
    
    configured = [k for k in env_keys if os.getenv(k)]
    if not configured:
        print("Warning: No LLM API keys configured", file=sys.stderr)
        return False
    
    print(f"Configured API keys: {', '.join(configured)}", file=sys.stderr)
    return True


def truncate_diff(diff_content: str, max_chars: int = 30000) -> str:
    """Truncate diff if too long to fit in context window."""
    if len(diff_content) <= max_chars:
        return diff_content
    
    # Keep first and last parts
    half = max_chars // 2
    truncated = diff_content[:half] + "\n\n... [TRUNCATED - diff too long] ...\n\n" + diff_content[-half:]
    return truncated


def review_pr(
    diff_content: str,
    model: str = "gpt-4o",
    language: str = "bilingual",
    pr_title: str = "",
    pr_body: str = "",
) -> str:
    """
    Review PR diff using LLM.
    
    Args:
        diff_content: The git diff content
        model: LLM model to use
        language: Review language (en, cn, bilingual)
        pr_title: PR title
        pr_body: PR description
        
    Returns:
        Review markdown content
    """
    # Select prompt based on language
    if language == "cn":
        prompt_template = REVIEW_PROMPT_CN
    elif language == "en":
        prompt_template = REVIEW_PROMPT_EN
    else:
        prompt_template = REVIEW_PROMPT_BILINGUAL
    
    # Truncate diff if needed
    diff_content = truncate_diff(diff_content)
    
    # Format prompt
    prompt = prompt_template.format(
        pr_title=pr_title or "N/A",
        pr_body=pr_body or "No description provided",
        diff_content=diff_content,
    )
    
    # Get model name for LiteLLM
    litellm_model = MODEL_MAPPING.get(model, model)
    
    print(f"Using model: {litellm_model}", file=sys.stderr)
    print(f"Diff size: {len(diff_content)} chars", file=sys.stderr)
    
    try:
        # Call LLM
        litellm.drop_params = True
        response = litellm.completion(
            model=litellm_model,
            messages=[
                {"role": "system", "content": "You are an expert code reviewer."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        error_msg = f"Error calling LLM: {str(e)}"
        print(error_msg, file=sys.stderr)
        
        # Return error message as review
        return f"""### ❌ Review Failed / 审查失败

Unable to complete AI review due to an error:
无法完成 AI 审查，原因：

```
{str(e)}
```

Please check:
- LLM API key is configured in GitHub Secrets
- The selected model ({model}) is available
- API quota is not exceeded

请检查：
- GitHub Secrets 中是否配置了 LLM API Key
- 所选模型 ({model}) 是否可用
- API 配额是否超限
"""


def main():
    parser = argparse.ArgumentParser(description="AI PR Review Script")
    parser.add_argument(
        "--diff-file",
        type=Path,
        required=True,
        help="Path to the diff file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("review_result.md"),
        help="Output file path",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("REVIEW_MODEL", "gpt-4o"),
        help="LLM model to use",
    )
    parser.add_argument(
        "--language",
        type=str,
        choices=["en", "cn", "bilingual"],
        default=os.getenv("REVIEW_LANGUAGE", "bilingual"),
        help="Review language",
    )
    
    args = parser.parse_args()
    
    # Setup API keys
    setup_api_keys()
    
    # Read diff
    if not args.diff_file.exists():
        print(f"Error: Diff file not found: {args.diff_file}", file=sys.stderr)
        sys.exit(1)
    
    diff_content = args.diff_file.read_text(encoding="utf-8", errors="ignore")
    
    if not diff_content.strip():
        review = "### ℹ️ No Changes / 无变更\n\nNo code changes detected in this PR.\n此 PR 没有检测到代码变更。"
    else:
        # Get PR info from environment
        pr_title = os.getenv("PR_TITLE", "")
        pr_body = os.getenv("PR_BODY", "")
        
        # Run review
        review = review_pr(
            diff_content=diff_content,
            model=args.model,
            language=args.language,
            pr_title=pr_title,
            pr_body=pr_body,
        )
    
    # Write output
    args.output.write_text(review, encoding="utf-8")
    print(f"Review written to: {args.output}", file=sys.stderr)
    
    # Also print to stdout for logging
    print(review)


if __name__ == "__main__":
    main()
