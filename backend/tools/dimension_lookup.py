"""
维度查询工具：拉取概念板块/申万行业分类码列表，供 FundScreenerAgent 使用
"""
import json
from db.connection import execute_query
from utils.serializers import json_default


def get_dimension_list(dim_type: str) -> str:
    """
    全量拉取指定维度的分类码列表。

    参数：
      dim_type: 维度类型名称，对应 tb_dict_params.c_param_type，
                如 "概念板块" 或 "申万行业分类"

    返回 JSON 字符串，数组，每条包含：
      code       → c_param_code
      name       → c_param_name
      parent_code → c_parent_code（行业分类有层级，概念板块一般为空）
      remark     → c_remark（概念板块的描述，行业分类为空字符串）
    """
    rows = execute_query(
        "SELECT c_param_code AS code, c_param_name AS name, "
        "c_parent_code AS parent_code, c_remark AS remark "
        "FROM tb_dict_params "
        "WHERE c_param_type = %s "
        "ORDER BY c_param_code",
        params=(dim_type,),
        readonly=True,
    )
    if not rows:
        return json.dumps([], ensure_ascii=False)
    return json.dumps(rows, ensure_ascii=False, default=json_default)
