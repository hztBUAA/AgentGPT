# import asyncio

# async def task():
#     print("Task started")
#     await asyncio.sleep(5)  # 模拟异步操作
#     print("Task completed")

# async def main():
#     await task()

# asyncio.run(main())



# 整理了python 与 javascript的区别  python需要asyncio的run 或者await




import asyncio

async def task():
    print("[Task] 开始执行")
    await asyncio.sleep(5)  # 挂起当前协程，事件循环可以执行其他任务
    print("[Task] 5秒等待结束，继续执行")

async def another_task():
    print("[Another Task] 开始执行")
    for i in range(1, 6):
        await asyncio.sleep(1)  # 每次等待1秒
        print(f"[Another Task] 第 {i} 秒")
    print("[Another Task] 完成")

async def main():
    # 同时调度两个协程，让它们并发执行
    await asyncio.gather(task(), another_task())

asyncio.run(main())