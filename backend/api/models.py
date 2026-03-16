from fastapi import APIRouter, Query, HTTPException
from typing import Optional

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
def get_model_data(
    model_id: str,
    trade_date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD"),
    fund_code: Optional[str] = Query(None, description="基金代码"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
):
    """获取指定模型的数据"""
    try:
        from services.model_data_service import get_yield_curve_data, get_nav_history

        if model_id == "yield-curve":
            return get_yield_curve_data(trade_date=trade_date)

        elif model_id == "nav-history":
            if not fund_code:
                raise HTTPException(status_code=400, detail="nav-history 需要 fund_code 参数")
            return get_nav_history(fund_code=fund_code, start_date=start_date, end_date=end_date)

        else:
            return {"model_id": model_id, "data": [], "message": "该模型数据接口尚未实现"}

    except HTTPException:
        raise
    except Exception as e:
        # DB 不可用时降级返回空数据，不影响页面加载
        print(f"[Models API] 数据查询失败: {type(e).__name__}: {e}")
        return {"model_id": model_id, "data": [], "error": str(e)}
