import asyncio

async def task():
    print("Task started")
    await asyncio.sleep(5)  # 模拟异步操作
    print("Task completed")

async def main():
    await task()

asyncio.run(main())