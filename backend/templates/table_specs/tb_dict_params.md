# tb_dict_params — 通用参数字典表

**主键**: (c_param_type, c_param_code) | **更新频率**: 低频（字典变动时手动触发）

## 字段清单（CSV 导出列）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| c_param_type | VARCHAR(50) | 参数类型（命名空间，区分不同字典，见枚举） |
| c_param_code | VARCHAR(50) | 参数代码（类型内唯一，层级代码） |
| c_param_name | VARCHAR(200) | 参数名称（中文名称） |
| c_parent_code | VARCHAR(50) | 父节点代码（树形结构，顶级节点为空字符串） |
| c_remark | VARCHAR(500) | 备注说明 |

## 注意事项

- 本表主要存储**行业分类体系**的代码→名称映射
- 代码长度规律（行业分类）：6位=一级行业，9位=二级行业，12位=三级行业
- 父子关系通过 c_parent_code 关联（c_parent_code 为空字符串表示顶级）
- CSV 导入后空值为空字符串，查询一级代码用 `c_parent_code = ''` 或 `LENGTH(c_param_code) = 6`

## 已录入参数类型（c_param_type 取值）

| c_param_type | 说明 | 代码前缀 |
|---|---|---|
| 中信行业分类 | 中信行业2020，Barra模型使用 | 025 |
| 申万行业分类 | 2021-07-30起启用，含港美 | 029 |
| 申万行业分类(旧) | 2021-07-30前使用 | 011 |
| 中证行业分类 | 2021版 | 033 |
| 证监会行业分类 | 监管口径 | 002 |
| GICS行业分类 | 全球标准 | 003 |
| 港交所行业分类 | 港股本地分类 | 403 |
| 港股申万行业分类 | 申万对港股的覆盖 | 408 |
| 港股中信行业分类 | 中信对港股的覆盖 | 407 |

## 常用查询示例

```sql
-- 查询中信一级行业列表（6位代码=一级）
SELECT c_param_code, c_param_name
FROM tb_dict_params
WHERE c_param_type = '中信行业分类'
  AND LENGTH(c_param_code) = 6
ORDER BY c_param_code
LIMIT 30;

-- 查询申万一级行业列表
SELECT c_param_code, c_param_name
FROM tb_dict_params
WHERE c_param_type = '申万行业分类'
  AND LENGTH(c_param_code) = 6
ORDER BY c_param_code
LIMIT 30;

-- 查询某行业分类体系的完整层级（通过 parent_code 关联）
SELECT a.c_param_code AS l1_code, a.c_param_name AS l1_name,
       b.c_param_code AS l2_code, b.c_param_name AS l2_name
FROM tb_dict_params a
JOIN tb_dict_params b ON b.c_param_type = a.c_param_type
  AND b.c_parent_code = a.c_param_code
WHERE a.c_param_type = '中信行业分类'
  AND LENGTH(a.c_param_code) = 6
ORDER BY a.c_param_code, b.c_param_code
LIMIT 50;
```
