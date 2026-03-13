from fastapi import APIRouter

router = APIRouter()


@router.get("/models")
def list_models():
    """返回所有可用模型的元数据"""
    return {
        "models": [
            {
                "id": "yield-curve",
                "name": "收益率曲线模型",
                "description": "追踪国债收益率曲线的形态与走势变化",
                "category": "利率",
                "update_frequency": "日频",
                "status": "active",
                "path": "/models/yield-curve",
            },
            {
                "id": "asset-allocation",
                "name": "基金资产配置分析",
                "description": "分析基金的资产配置结构与历史变化",
                "category": "基金分析",
                "update_frequency": "季频",
                "status": "coming_soon",
            },
            {
                "id": "portfolio-analysis",
                "name": "基金持仓分析",
                "description": "深度解析基金的股票和债券持仓明细",
                "category": "基金分析",
                "update_frequency": "季频",
                "status": "coming_soon",
            },
            {
                "id": "style-tracking",
                "name": "市场风格跟踪",
                "description": "追踪市场风格轮动，识别主导风格因子",
                "category": "市场分析",
                "update_frequency": "日频",
                "status": "coming_soon",
            },
        ]
    }


@router.get("/models/{model_id}/data")
def get_model_data(model_id: str):
    """获取指定模型的数据（占位，后续接入 DB）"""
    return {"model_id": model_id, "data": [], "message": "数据接口待接入数据库"}
