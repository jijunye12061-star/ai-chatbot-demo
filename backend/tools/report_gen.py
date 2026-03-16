"""
报告生成工具：按 fund_report.json 模板，按 parallel_group 并行生成各节，拼装完整 Markdown
"""
import asyncio
import decimal
import datetime
import json
import os

from db.connection import execute_query
from llm.client import chat_completion, extract_content

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")


def _load_template() -> dict:
    path = os.path.join(_TEMPLATES_DIR, "fund_report.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_prompt(filename: str) -> str:
    path = os.path.join(_PROMPTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _serialize(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return str(obj)
    return str(obj)


def _query_data(sql: str, fund_code: str) -> str:
    """执行 data_sql，返回 JSON 字符串"""
    sql = sql.replace("{fund_code}", fund_code)
    try:
        rows = execute_query(sql, readonly=True)
        if not rows:
            return "（无数据）"
        return json.dumps(rows, ensure_ascii=False, default=_serialize, indent=2)
    except Exception as e:
        return f"（查询失败：{e}）"


async def _generate_section(section: dict, fund_code: str, prior_results: dict) -> str:
    """生成单节内容"""
    section_id = section["id"]
    title = section["title"]

    # 查询数据（如有 data_sql）
    data_str = ""
    if section.get("data_sql"):
        data_str = _query_data(section["data_sql"], fund_code)

    # 加载 prompt
    prompt_template = _load_prompt(section["prompt_file"])

    # 注入变量
    format_vars = {"data": data_str, "fund_code": fund_code}
    # 注入前置节结果（用于 summary 等依赖节）
    for dep in section.get("depends_on", []):
        format_vars[dep] = prior_results.get(dep, "（未生成）")

    try:
        prompt = prompt_template.format(**format_vars)
    except KeyError:
        prompt = prompt_template  # 有未知占位符时直接使用原模板

    # 调用 LLM 生成文字
    messages = [{"role": "user", "content": prompt}]
    response = await chat_completion(messages, stream=False)
    content = extract_content(response)

    return f"## {title}\n\n{content}\n"


async def generate_fund_report(fund_code: str) -> str:
    """
    生成完整基金研究报告。
    按 parallel_group 分组，同组并行，跨组串行。
    """
    print(f"[ReportGen] 开始生成 {fund_code} 的研究报告")
    template = _load_template()
    sections = template["sections"]

    # 按 parallel_group 分组
    groups: dict[int, list] = {}
    for sec in sections:
        g = sec.get("parallel_group", 1)
        groups.setdefault(g, []).append(sec)

    results: dict[str, str] = {}
    report_parts = [f"# {template['name']} — {fund_code}\n"]

    for group_id in sorted(groups.keys()):
        group_sections = groups[group_id]
        print(f"[ReportGen] 并行生成 Group {group_id}: {[s['id'] for s in group_sections]}")

        # 并行生成本组所有节
        tasks = [_generate_section(sec, fund_code, results) for sec in group_sections]
        group_results = await asyncio.gather(*tasks)

        for sec, content in zip(group_sections, group_results):
            results[sec["id"]] = content
            report_parts.append(content)

    full_report = "\n".join(report_parts)
    print(f"[ReportGen] 报告生成完毕，共 {len(full_report)} 字符")
    return full_report
