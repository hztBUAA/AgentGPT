# 创建新的 conda 环境，指定 Python 版本
# conda create -n reworkd_platform python=3.11

# 激活环境
conda activate agentGPT

# 安装主要依赖
conda install -c conda-forge \
    fastapi=0.98.0 \
    boto3=1.28.51 \
    uvicorn=0.22.0 \
    pydantic=1.10.12 \
    ujson=5.8.0 \
    sqlalchemy=2.0.21 \
    aiomysql=0.1.1 \
    mysqlclient=2.2.0 \
    sentry-sdk=1.31.0 \
    loguru=0.7.2 \
    requests=2.31.0 \
    openai=0.28.0 \
    tiktoken=0.5.1 \
    grpcio=1.58.0 \
    cryptography=41.0.4 \
    httpx=0.25.0

# 一些包可能需要用 pip 安装，因为 conda 中没有或版本不匹配
pip install \
    aiokafka==0.8.1 \
    langchain==0.0.295 \
    wikipedia==1.4.0 \
    replicate==0.8.4 \
    lanarky==0.7.15 \
    pinecone-client==2.2.4 \
    aws-secretsmanager-caching==1.1.1.5 \
    stripe==5.5.0

# 开发依赖
conda install -c conda-forge \
    pytest=7.4.2 \
    flake8=6.0.0 \
    mypy=1.5.1 \
    isort=5.12.0 \
    pre-commit=3.4.0 \
    black=23.9.1 \
    pytest-cov=4.1.0 \
    pytest-env=0.8.2