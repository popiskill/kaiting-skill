#!/usr/bin/env python3
"""
开庭 Skill - Skill 加载工具
用于读取、解析、验证 Skill 目录
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_skill(skill_path: str) -> dict:
    """
    加载并解析一个 Skill 目录
    
    Args:
        skill_path: Skill 目录路径或 SKILL.md 文件路径
    
    Returns:
        包含 Skill 信息的字典
    """
    path = Path(skill_path).expanduser()
    
    # 如果是文件，取父目录
    if path.is_file():
        skill_dir = path.parent
    else:
        skill_dir = path
    
    # 检查 SKILL.md 是否存在
    skill_md_path = skill_dir / "SKILL.md"
    if not skill_md_path.exists():
        return {
            "status": "error",
            "message": f"未找到 SKILL.md: {skill_dir}"
        }
    
    result = {
        "status": "ok",
        "path": str(skill_dir),
        "name": skill_dir.name,
        "files": {},
        "structure": {}
    }
    
    # 读取 SKILL.md
    with open(skill_md_path, "r", encoding="utf-8") as f:
        result["files"]["SKILL.md"] = f.read()
    
    # 检查 README.md
    readme_path = skill_dir / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            result["files"]["README.md"] = f.read()
    
    # 检查 prompts 目录
    prompts_dir = skill_dir / "prompts"
    if prompts_dir.exists() and prompts_dir.is_dir():
        result["structure"]["prompts"] = []
        for f in prompts_dir.glob("*.md"):
            with open(f, "r", encoding="utf-8") as fp:
                result["files"][f"prompts/{f.name}"] = fp.read()
                result["structure"]["prompts"].append(f.name)
    
    # 检查 tools 目录
    tools_dir = skill_dir / "tools"
    if tools_dir.exists() and tools_dir.is_dir():
        result["structure"]["tools"] = []
        for f in tools_dir.glob("*"):
            if f.is_file() and not f.name.startswith("."):
                try:
                    with open(f, "r", encoding="utf-8") as fp:
                        result["files"][f"tools/{f.name}"] = fp.read()
                        result["structure"]["tools"].append(f.name)
                except:
                    result["structure"]["tools"].append(f"{f.name} (binary)")
    
    # 检查其他文件
    result["structure"]["other"] = []
    for f in skill_dir.iterdir():
        if f.is_file() and f.name not in ["SKILL.md", "README.md"] and not f.name.startswith("."):
            result["structure"]["other"].append(f.name)
    
    return result


def parse_frontmatter(content: str) -> dict:
    """解析 SKILL.md 的 frontmatter"""
    if not content.startswith("---"):
        return {}
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    
    frontmatter_str = parts[1].strip()
    
    # 简单解析 YAML frontmatter
    result = {}
    current_key = None
    current_dict = None
    
    for line in frontmatter_str.split("\n"):
        if not line.strip():
            continue
        
        if line.startswith("  "):
            # 嵌套字段
            if current_dict is not None:
                key_value = line.strip().split(":", 1)
                if len(key_value) == 2:
                    current_dict[key_value[0].strip()] = key_value[1].strip()
        else:
            key_value = line.split(":", 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                
                if value:
                    result[key] = value
                else:
                    result[key] = {}
                    current_key = key
                    current_dict = result[key]
    
    return result


def analyze_skill(skill_data: dict) -> dict:
    """快速分析 Skill 结构"""
    if skill_data["status"] != "ok":
        return skill_data
    
    analysis = {
        "has_skill_md": "SKILL.md" in skill_data["files"],
        "has_readme": "README.md" in skill_data["files"],
        "prompt_count": len(skill_data["structure"].get("prompts", [])),
        "tool_count": len(skill_data["structure"].get("tools", [])),
        "other_files": skill_data["structure"].get("other", [])
    }
    
    # 解析 frontmatter
    if "SKILL.md" in skill_data["files"]:
        frontmatter = parse_frontmatter(skill_data["files"]["SKILL.md"])
        analysis["frontmatter"] = frontmatter
    
    skill_data["analysis"] = analysis
    return skill_data


def main():
    """CLI 入口"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "用法: skill_loader.py <skill_path>",
            "actions": ["load", "analyze"]
        }))
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "load":
        if len(sys.argv) < 3:
            print(json.dumps({"status": "error", "message": "用法: skill_loader.py load <skill_path>"}))
            sys.exit(1)
        result = load_skill(sys.argv[2])
        
    elif action == "analyze":
        if len(sys.argv) < 3:
            print(json.dumps({"status": "error", "message": "用法: skill_loader.py analyze <skill_path>"}))
            sys.exit(1)
        result = analyze_skill(load_skill(sys.argv[2]))
        
    else:
        result = {
            "status": "error",
            "message": f"未知操作: {action}"
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
