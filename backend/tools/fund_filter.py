"""
基金筛选工具：模板加载 + 参数校验 + SQL 渲染 + 执行
"""
import os
import json
import yaml
import decimal
import datetime
from functools import lru_cache
from db.connection import execute_query
from db.safety import validate_sql

_TEMPLATES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "templates", "screen_templates"
)


@lru_cache(maxsize=64)
def _load_template(template_id: str) -> dict:
    """加载 YAML 模板文件"""
    for fname in os.listdir(_TEMPLATES_DIR):
        if fname.startswith(template_id) and fname.endswith(".yaml"):
            path = os.path.join(_TEMPLATES_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
    raise ValueError(f"模板 {template_id} 不存在")


def _resolve_trade_date(value: str, table: str = "tb_fd_perform_abs") -> str:
    """
    处理 trade_date 参数：
    - 'latest' → 查询表中最新日期
    - 具体日期字符串 → 直接返回
    """
    if value == "latest":
        rows = execute_query(
            f"SELECT MAX(c_trade_date) AS max_date FROM {table}",
            readonly=True,
        )
        if rows and rows[0]["max_date"]:
            d = rows[0]["max_date"]
            return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)
        raise ValueError(f"无法获取 {table} 的最新日期")
    return value


def _validate_params(param_defs: dict, user_params: dict) -> dict:
    """
    校验参数：类型检查、枚举映射、默认值填充。
    返回校验后的参数字典。
    """
    validated = {}
    for name, spec in param_defs.items():
        value = user_params.get(name)

        # 必填检查
        if value is None:
            if spec.get("required", False) is True and "default" not in spec:
                raise ValueError(f"缺少必填参数: {name} ({spec.get('description', '')})")
            value = spec.get("default")

        if value is None:
            continue

        # 类型处理
        param_type = spec.get("type", "string")

        if param_type == "enum":
            options = spec.get("options", {})
            # 支持传枚举名称或直接传代码
            if value in options:
                value = options[value]  # 名称 → 代码
            elif value not in options.values():
                valid = list(options.keys())
                raise ValueError(f"参数 {name} 的值 '{value}' 无效，可选: {valid}")

        elif param_type == "date":
            # 处理 latest 特殊值
            if value == "latest":
                value = _resolve_trade_date("latest")
            # 简单格式校验
            elif isinstance(value, str):
                try:
                    datetime.datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f"参数 {name} 日期格式错误，应为 YYYY-MM-DD")

        elif param_type == "int":
            value = int(value)
            if "max" in spec:
                value = min(value, spec["max"])

        validated[name] = value
    return validated


def _build_and_execute_sql(template: dict, params: dict) -> list:
    """
    根据模板和参数构建参数化 SQL 并执行。
    """
    sql_template = template["sql"]
    sql_params = []

    sql_params.append(params["trade_date"])
    sql_params.append(params["period_code"])

    category_filter = ""
    if params.get("fund_category"):
        category_filter = "AND cat.c_type1_name LIKE %s"
        sql_params.append(f"%{params['fund_category']}%")

    sql_params.append(params.get("limit", 50))

    sql = sql_template.replace("{category_filter}", category_filter)

    # safety 校验（防御层，虽然是人工写的模板，防止意外篡改）
    ok, result = validate_sql(sql)
    if not ok:
        raise ValueError(f"SQL 安全校验失败: {result}")

    return execute_query(sql, params=tuple(sql_params), readonly=True)


def _default_serializer(obj):
    """JSON 序列化辅助"""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return str(obj)
    return str(obj)


def run_screen_template(template_id: str, params: dict = None) -> str:
    """
    执行基金筛选模板。
    - template_id: 模板 ID（如 "001"）
    - params: 参数字典
    返回 JSON 格式结果字符串。
    """
    params = params or {}

    try:
        template = _load_template(template_id)
    except ValueError as e:
        return f"[错误] {e}"

    print(f"[FundScreener] 使用模板: {template['name']} (id={template_id}), 参数: {params}")

    # 参数校验
    try:
        validated = _validate_params(template["params"], params)
    except ValueError as e:
        return f"[参数错误] {e}"

    # 根据类型执行
    if template["type"] == "sql":
        try:
            rows = _build_and_execute_sql(template, validated)
        except Exception as e:
            return f"[查询失败] {type(e).__name__}: {e}"

    elif template["type"] == "python_func":
        try:
            func_path = template["func"]  # 如 "screen_functions.sector_holding.fd_bk_pct"
            module_path, func_name = func_path.rsplit(".", 1)
            import importlib
            module = importlib.import_module(f"tools.{module_path}")
            func = getattr(module, func_name)
            rows = func(**validated)
        except Exception as e:
            return f"[执行失败] {type(e).__name__}: {e}"
    else:
        return f"[错误] 不支持的模板类型: {template['type']}"

    if not rows:
        return f"模板 '{template['name']}' 未找到符合条件的基金，建议调整参数。"

    result_str = json.dumps(rows, ensure_ascii=False, default=_default_serializer, indent=2)
    return f"使用模板「{template['name']}」筛选到 {len(rows)} 支基金：\n{result_str}"
