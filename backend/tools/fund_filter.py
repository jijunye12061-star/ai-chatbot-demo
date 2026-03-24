"""
基金筛选工具：模板加载 + 参数校验 + SQL 渲染 + 执行
"""
import os
import re
import json
import yaml
import datetime
from functools import lru_cache
from db.connection import execute_query
from db.safety import validate_sql
from utils.serializers import json_default

_TEMPLATES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "templates", "screen_templates"
)

ALLOWED_CONDITION_FIELDS = {
    "c_ann_ret", "c_period_ret", "c_mdd", "c_sharpe",
    "c_calmar", "c_sortino", "c_ann_vol", "c_break_ratio"
}

PERIOD_MAP = {
    "近1月": "00", "近3月": "01", "近6月": "02",
    "近1年": "03", "近2年": "04", "近3年": "05",
    "近5年": "06", "年初至今": "07", "成立以来": "08",
}


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

        elif param_type == "float":
            value = float(value)

        elif param_type == "list":
            if not isinstance(value, list):
                raise ValueError(f"参数 {name} 应为列表类型")
            if not value:
                raise ValueError(f"参数 {name} 不能为空列表")

        elif param_type == "conditions":
            # {field: {min: value_or_null, max: value_or_null}}
            if not isinstance(value, dict):
                raise ValueError(f"参数 {name} 应为字典类型")
            validated_conditions = {}
            for field, bounds in value.items():
                if field not in ALLOWED_CONDITION_FIELDS:
                    raise ValueError(f"条件字段 '{field}' 不在白名单中，允许字段: {sorted(ALLOWED_CONDITION_FIELDS)}")
                if not isinstance(bounds, dict):
                    raise ValueError(f"条件字段 '{field}' 的值应为 {{min: ..., max: ...}} 格式")
                validated_conditions[field] = {
                    "min": float(bounds["min"]) if bounds.get("min") is not None else None,
                    "max": float(bounds["max"]) if bounds.get("max") is not None else None,
                }
            value = validated_conditions

        elif param_type == "cross_period_conditions":
            # {区间名称: {字段: {min, max}}}
            if not isinstance(value, dict):
                raise ValueError(f"参数 {name} 应为字典类型")
            validated_cross = {}
            for period_name, field_conditions in value.items():
                if period_name not in PERIOD_MAP:
                    raise ValueError(f"区间名称 '{period_name}' 无效，可选: {list(PERIOD_MAP.keys())}")
                if not isinstance(field_conditions, dict):
                    raise ValueError(f"区间 '{period_name}' 的条件应为字典类型")
                validated_fields = {}
                for field, bounds in field_conditions.items():
                    if field not in ALLOWED_CONDITION_FIELDS:
                        raise ValueError(f"条件字段 '{field}' 不在白名单中，允许字段: {sorted(ALLOWED_CONDITION_FIELDS)}")
                    if not isinstance(bounds, dict):
                        raise ValueError(f"字段 '{field}' 的值应为 {{min: ..., max: ...}} 格式")
                    validated_fields[field] = {
                        "min": float(bounds["min"]) if bounds.get("min") is not None else None,
                        "max": float(bounds["max"]) if bounds.get("max") is not None else None,
                    }
                validated_cross[period_name] = validated_fields
            value = validated_cross

        elif param_type == "dict":
            # {field: enum_value} - 标签字段等值匹配
            if not isinstance(value, dict):
                raise ValueError(f"参数 {name} 应为字典类型")
            allowed_fields = spec.get("allowed_tag_fields", [])
            for field in value:
                if field not in allowed_fields:
                    raise ValueError(f"标签字段 '{field}' 不在允许列表中，允许字段: {allowed_fields}")

        validated[name] = value
    return validated


_PLACEHOLDER_RE = re.compile(
    r'\{:(\w+)\}|\{\*(\w+)\}|\{\?(\w+)\}|\{@(\w+)\}|\{#sw_industry\}'
)


def _render_sql(sql_template: str, param_defs: dict, validated_params: dict):
    """
    将 SQL 模板中的具名占位符展开为参数化 SQL。
    占位符类型：
      {:name}  → %s，值追加到 params
      {*name}  → IN (%s,...) 按列表长度展开
      {?name}  → 有值时用 fragment 替换（含 %s），无值时为空串
      {@name}  → conditions 类型: AND field >= %s / AND field <= %s
                 dict 类型: AND field = %s （等值匹配）
      {#sw_industry} → SW行业码按长度分组：LEFT(c_sw_code,N) IN (...)
    单趟从左到右替换，保证 params 顺序与 SQL 中 %s 顺序一致。
    返回 (rendered_sql, params_tuple)
    """
    params = []

    def _replace(m):
        scalar_name, list_name, opt_name, at_name = m.group(1), m.group(2), m.group(3), m.group(4)

        if scalar_name is not None:
            # {:name} 标量
            if scalar_name not in validated_params:
                raise ValueError(f"渲染SQL时缺少参数: {scalar_name}")
            params.append(validated_params[scalar_name])
            return "%s"

        if list_name is not None:
            # {*name} 列表 IN
            values = validated_params.get(list_name, [])
            if not values:
                raise ValueError(f"列表参数 {list_name} 为空，无法构建 IN 子句")
            placeholders = ", ".join(["%s"] * len(values))
            params.extend(values)
            return f"IN ({placeholders})"

        if opt_name is not None:
            # {?name} 可选片段
            value = validated_params.get(opt_name)
            if not value:
                return ""
            fragment = param_defs.get(opt_name, {}).get("fragment", "")
            if not fragment:
                raise ValueError(f"可选参数 {opt_name} 未定义 fragment 字段")
            params.append(f"%{value}%")
            return fragment

        if at_name is not None:
            # {@name} conditions/dict
            value = validated_params.get(at_name)
            if not value:
                return ""
            ptype = param_defs.get(at_name, {}).get("type", "conditions")
            parts = []
            if ptype == "conditions":
                for field, bounds in value.items():
                    if bounds.get("min") is not None:
                        parts.append(f"AND {field} >= %s")
                        params.append(bounds["min"])
                    if bounds.get("max") is not None:
                        parts.append(f"AND {field} <= %s")
                        params.append(bounds["max"])
            elif ptype == "dict":
                for field, val in value.items():
                    parts.append(f"AND {field} = %s")
                    params.append(val)
            return " ".join(parts)

        # {#sw_industry}
        sw_codes = validated_params.get("sw_codes", [])
        if not sw_codes:
            return "1=0"
        groups = {}
        for code in sw_codes:
            length = len(code)
            if length not in (6, 9, 12):
                raise ValueError(f"申万行业代码 '{code}' 长度 {length} 无效，应为6/9/12位")
            groups.setdefault(length, []).append(code)
        parts = []
        for length in sorted(groups):
            codes = groups[length]
            placeholders = ", ".join(["%s"] * len(codes))
            if length == 12:
                parts.append(f"c_sw_code IN ({placeholders})")
            else:
                parts.append(f"LEFT(c_sw_code, {length}) IN ({placeholders})")
            params.extend(codes)
        return "(" + " OR ".join(parts) + ")"

    sql = _PLACEHOLDER_RE.sub(_replace, sql_template)
    return sql, tuple(params)


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
            rendered_sql, sql_params = _render_sql(
                template["sql"], template["params"], validated
            )
            ok, checked_sql = validate_sql(rendered_sql)
            if not ok:
                raise ValueError(f"SQL 安全校验失败: {checked_sql}")
            rows = execute_query(checked_sql, params=sql_params, readonly=True)
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

    result_str = json.dumps(rows, ensure_ascii=False, default=json_default, indent=2)
    return f"使用模板「{template['name']}」筛选到 {len(rows)} 支基金：\n{result_str}"
