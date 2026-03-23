"""
公共序列化辅助，处理 DB 查询结果中的 Decimal / datetime 类型。
"""
import decimal
import datetime

_DB_TYPES = (decimal.Decimal, datetime.date, datetime.datetime)


def json_default(obj):
    """json.dumps default= 回调，供 tools 层序列化查询结果用。"""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return str(obj)
    return str(obj)


def serialize_row(row: dict) -> dict:
    """将 DB 查询行的 Decimal/date 字段转为 Python 原生类型，其他值保持不变。"""
    return {
        k: json_default(v) if isinstance(v, _DB_TYPES) else v
        for k, v in row.items()
    }
