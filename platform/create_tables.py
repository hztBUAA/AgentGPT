#!/usr/bin/env python
"""
初始化脚本，用于创建数据库表。
"""

import asyncio

from reworkd_platform.db.meta import meta
from reworkd_platform.db.models import load_all_models
from reworkd_platform.db.utils import create_engine


async def create_tables() -> None:
    """创建数据库表"""
    print("开始加载模型...")
    load_all_models()

    print("开始创建数据库引擎...")
    engine = create_engine()
    
    print("开始创建数据库表...")
    async with engine.begin() as connection:
        await connection.run_sync(meta.create_all)
    
    print("清理连接...")
    await engine.dispose()
    
    print("数据库表创建完成!")


if __name__ == "__main__":
    print("开始初始化数据库表...")
    asyncio.run(create_tables()) 