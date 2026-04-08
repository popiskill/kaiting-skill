#!/usr/bin/env python3
"""
开庭 Skill - 审判档案管理工具
用于保存、读取、列出审判档案
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 档案存储目录
VERDICTS_DIR = Path(__file__).parent.parent / "verdicts"


def ensure_dir():
    """确保档案目录存在"""
    VERDICTS_DIR.mkdir(parents=True, exist_ok=True)


def save_verdict(skill_name: str, verdict_data: dict) -> dict:
    """保存审判档案"""
    ensure_dir()
    
    # 添加时间戳
    verdict_data["judged_at"] = datetime.now().isoformat()
    
    # 文件名安全处理
    safe_name = "".join(c for c in skill_name if c.isalnum() or c in "._-").strip()
    if not safe_name:
        safe_name = f"verdict_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    filepath = VERDICTS_DIR / f"{safe_name}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(verdict_data, f, ensure_ascii=False, indent=2)
    
    return {
        "status": "ok",
        "name": skill_name,
        "path": str(filepath),
        "message": f"审判档案 '{skill_name}' 已保存"
    }


def load_verdict(skill_name: str) -> dict:
    """读取审判档案"""
    ensure_dir()
    
    # 尝试精确匹配
    filepath = VERDICTS_DIR / f"{skill_name}.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "status": "ok",
            "data": data
        }
    
    return {
        "status": "error",
        "message": f"未找到审判档案: {skill_name}"
    }


def list_verdicts() -> dict:
    """列出所有审判档案"""
    ensure_dir()
    
    verdicts = []
    for f in VERDICTS_DIR.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                verdicts.append({
                    "name": data.get("name", f.stem),
                    "total_score": data.get("scores", {}).get("total", 0),
                    "level": data.get("level", "未知"),
                    "judged_at": data.get("judged_at", "未知")
                })
        except Exception as e:
            verdicts.append({
                "name": f.stem,
                "error": str(e)
            })
    
    # 按分数排序
    verdicts.sort(key=lambda x: x.get("total_score", 0), reverse=True)
    
    return {
        "status": "ok",
        "count": len(verdicts),
        "verdicts": verdicts
    }


def compare_verdicts(name1: str, name2: str) -> dict:
    """对比两个审判档案"""
    result1 = load_verdict(name1)
    result2 = load_verdict(name2)
    
    if result1["status"] != "ok":
        return {"status": "error", "message": f"未找到档案: {name1}"}
    if result2["status"] != "ok":
        return {"status": "error", "message": f"未找到档案: {name2}"}
    
    data1 = result1["data"]
    data2 = result2["data"]
    
    return {
        "status": "ok",
        "comparison": {
            "name1": name1,
            "name2": name2,
            "scores": {
                "实用性": [data1.get("scores", {}).get("实用性", 0), data2.get("scores", {}).get("实用性", 0)],
                "文档质量": [data1.get("scores", {}).get("文档质量", 0), data2.get("scores", {}).get("文档质量", 0)],
                "代码质量": [data1.get("scores", {}).get("代码质量", 0), data2.get("scores", {}).get("代码质量", 0)],
                "创新性": [data1.get("scores", {}).get("创新性", 0), data2.get("scores", {}).get("创新性", 0)],
                "完整性": [data1.get("scores", {}).get("完整性", 0), data2.get("scores", {}).get("完整性", 0)],
                "total": [data1.get("scores", {}).get("total", 0), data2.get("scores", {}).get("total", 0)]
            },
            "winner": name1 if data1.get("scores", {}).get("total", 0) >= data2.get("scores", {}).get("total", 0) else name2
        }
    }


def main():
    """CLI 入口"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "用法: verdict_writer.py <action> [args...]",
            "actions": ["save", "load", "list", "compare"]
        }))
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "save":
        if len(sys.argv) < 4:
            print(json.dumps({"status": "error", "message": "用法: verdict_writer.py save <name> <json_data>"}))
            sys.exit(1)
        name = sys.argv[2]
        data = json.loads(sys.argv[3])
        result = save_verdict(name, data)
        
    elif action == "load":
        if len(sys.argv) < 3:
            print(json.dumps({"status": "error", "message": "用法: verdict_writer.py load <name>"}))
            sys.exit(1)
        result = load_verdict(sys.argv[2])
        
    elif action == "list":
        result = list_verdicts()
        
    elif action == "compare":
        if len(sys.argv) < 4:
            print(json.dumps({"status": "error", "message": "用法: verdict_writer.py compare <name1> <name2>"}))
            sys.exit(1)
        result = compare_verdicts(sys.argv[2], sys.argv[3])
        
    else:
        result = {
            "status": "error",
            "message": f"未知操作: {action}"
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
