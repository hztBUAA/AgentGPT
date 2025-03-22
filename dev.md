# AgentGPT 二次开发指南

## 项目架构

### 1. 核心组件

- **FastAPI应用层**: 处理HTTP请求和路由
- **Agent服务层**: 实现智能体的核心逻辑
- **工具系统**: 可扩展的工具集合
- **数据模型层**: 定义数据结构和模式

### 2. 关键模块

- `web/api/agent/`: Agent相关的API实现
- `web/api/agent/tools/`: 工具实现
- `web/api/agent/agent_service/`: Agent服务实现
- `schemas/`: 数据模型定义
- `db/`: 数据库相关实现

### 3. 数据模型层详解

#### 3.1 SQLAlchemy Models (`db/models/`)

数据库模型使用SQLAlchemy ORM，主要包含以下模型：

1. **基础模型**
```python
class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda _: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
```

2. **核心模型**
- `User`: 用户信息模型
- `AgentRun`: Agent运行记录
- `AgentTask`: Agent任务记录
- `Organization`: 组织信息
- `OauthCredentials`: OAuth认证信息

3. **mapped_column原理**
- 使用SQLAlchemy的新式类型注解
- 自动生成数据库表结构
- 支持类型检查和验证
- 提供字段级别的配置选项

#### 3.2 Pydantic Schemas (`schemas/`)

API接口的数据模型，使用Pydantic实现：

1. **Schema定义示例**
```python
# 基础模型定义
class ModelSettings(BaseModel):
    model: LLM_Model = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=500, ge=0)
    
    # 自定义验证器
    @validator("max_tokens")
    def validate_max_tokens(cls, v: float, values: Dict[str, Any]) -> float:
        model = values["model"]
        if v > (max_tokens := LLM_MODEL_MAX_TOKENS[model]):
            raise ValueError(f"Model {model} only supports {max_tokens} tokens")
        return v

# 继承和组合
class AgentRunCreate(BaseModel):
    goal: str
    model_settings: ModelSettings = Field(default=ModelSettings())

class AgentRun(AgentRunCreate):
    run_id: str
```

2. **Schema功能特性**

a) **数据验证**
- 类型验证：自动检查数据类型
- 范围验证：使用Field约束（如ge, le）
- 自定义验证：通过validator装饰器
- 嵌套验证：支持复杂数据结构

b) **文档生成**
- 自动生成OpenAPI规范
- 字段描述和示例值
- 验证规则文档化
- 响应模型定义

c) **序列化/反序列化**
- JSON序列化
- 数据模型转换
- 别名支持（alias）
- 默认值处理

3. **使用场景**

a) **请求验证**
```python
@router.post("/analyze")
async def analyze_tasks(
    req_body: AgentTaskAnalyze = Depends(agent_analyze_validator),
) -> Analysis:
    # req_body已经经过验证和类型转换
    return await agent_service.analyze_task_agent(
        goal=req_body.goal,
        task=req_body.task,
        tool_names=req_body.tool_names,
    )
```

b) **响应格式化**
```python
class NewTasksResponse(BaseModel):
    run_id: str
    new_tasks: List[str] = Field(alias="newTasks")
    
# FastAPI自动处理响应序列化
@router.post("/start")
async def start_tasks() -> NewTasksResponse:
    return NewTasksResponse(run_id="123", new_tasks=["task1"])
```

c) **数据转换**
```python
# 模型间转换
agent_run = AgentRun(
    **agent_run_create.dict(),
    run_id=generated_id
)
```

4. **最佳实践**

- 使用类型注解
- 添加字段验证
- 提供默认值
- 使用嵌套模型
- 实现自定义验证器
- 添加字段描述

#### 3.3 模型关系

1. **继承关系**
- Base -> TrackedModel -> 具体模型
- BaseModel -> 具体Schema

2. **映射关系**
- 数据库模型 <-> Schema模型
- 请求数据 <-> 响应数据

3. **验证机制**
- Schema层：请求数据验证
- Model层：数据库约束验证

## 二次开发步骤

### 1. 自定义工具开发

1. 在 `web/api/agent/tools/` 下创建新的工具类
2. 继承 `Tool` 基类并实现必要方法:
   ```python
   class CustomTool(Tool):
       description = "工具描述"
       public_description = "公开描述"
       arg_description = "参数描述"
       
       async def call(self, goal: str, task: str, input_str: str, *args, **kwargs):
           # 实现工具逻辑
           pass
   ```
3. 在 `tools.py` 中注册工具

### 2. 自定义工作流

1. 修改 `web/api/agent/agent_service/open_ai_agent_service.py`
2. 可以自定义以下方法:
   - `start_goal_agent`: 初始化目标
   - `analyze_task_agent`: 任务分析
   - `execute_task_agent`: 任务执行
   - `create_tasks_agent`: 创建子任务

### 3. 提示词定制

1. 修改 `web/api/agent/prompts.py` 中的提示模板
2. 关键提示词包括:
   - `start_goal_prompt`: 启动目标
   - `analyze_task_prompt`: 任务分析
   - `create_tasks_prompt`: 任务创建

### 4. 数据模型扩展

1. 在 `schemas/` 下定义新的数据模型
2. 扩展现有模型以支持新功能

### 5. 服务层开发

#### 5.1 Services模块概述

Services模块提供了一系列核心服务：

1. **TokenService**: 处理文本标记化
```python
class TokenService:
    def count(self, text: str) -> int:
        return len(self.tokenize(text))

    def calculate_max_tokens(self, model: WrappedChatOpenAI, *prompts: str) -> None:
        requested_tokens = self.get_completion_space(model.model_name, *prompts)
        model.max_tokens = min(model.max_tokens, requested_tokens)
```

2. **ClaudeService**: Anthropic Claude模型集成
```python
class ClaudeService:
    async def completion(
        self,
        prompt: AbstractPrompt,
        max_tokens_to_sample: int,
        temperature: int = 0,
    ) -> str:
        # Claude API调用实现
```

3. **PineconeMemory**: 向量数据库集成
```python
class PineconeMemory(AgentMemory):
    async def get_similar_tasks(
        self, text: str, score_threshold: float = 0.95
    ) -> List[QueryResult]:
        # 相似任务检索实现
```

4. **EncryptionService**: 安全加密服务
```python
class EncryptionService:
    def encrypt(self, text: str) -> bytes:
        return self.fernet.encrypt(text.encode("utf-8"))
```

#### 5.2 二次开发场景

1. **自定义工作流集成**
   - 实现自己的Memory服务
   - 扩展TokenService支持新的模型
   - 添加新的AI模型服务

2. **向量存储定制**
   - 替换Pinecone为其他向量数据库
   - 自定义相似度计算逻辑
   - 优化检索策略

3. **模型集成**
   - 添加新的LLM模型支持
   - 自定义模型参数
   - 实现模型切换逻辑

4. **安全服务扩展**
   - 增强加密机制
   - 添加新的认证方式
   - 实现细粒度的权限控制

#### 5.3 开发示例

1. **自定义Memory服务**
```python
class CustomMemory(AgentMemory):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def get_similar_tasks(
        self, text: str, score_threshold: float
    ) -> List[QueryResult]:
        # 实现自定义的相似任务检索逻辑
        pass
```

2. **新增模型服务**
```python
class CustomModelService:
    def __init__(self, api_key: str, model_config: Dict[str, Any]):
        self.api_key = api_key
        self.config = model_config
        
    async def completion(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        # 实现自定义模型的API调用
        pass
```

#### 5.4 注意事项

1. **性能考虑**
   - 异步操作的正确使用
   - 资源的合理释放
   - 缓存策略的应用

2. **安全性**
   - API密钥的安全存储
   - 数据加密的正确使用
   - 访问控制的实现

3. **可扩展性**
   - 接口的抽象设计
   - 配置的灵活管理
   - 依赖注入的使用

4. **错误处理**
   - 优雅的异常处理
   - 完善的日志记录
   - 合理的重试机制

## 重点关注

### 1. 工具系统

- 工具注册机制
- 工具权限控制
- 工具执行上下文

### 2. Agent服务

- 任务分析逻辑
- 任务执行流程
- 错误处理机制

### 3. API接口

- 请求验证
- 响应格式
- 错误处理

### 4. 安全性

- API密钥管理
- 用户认证
- 数据验证

## FastAPI请求处理流程

1. 请求进入
   - 通过 `CORSMiddleware` 处理跨域
   - 路由到对应的API端点

2. 依赖注入
   - 验证请求参数
   - 注入必要的服务

3. 业务处理
   - Agent服务处理业务逻辑
   - 工具调用和执行

4. 响应返回
   - 格式化响应数据
   - 错误处理

## 开发建议

1. 遵循现有代码结构和风格
2. 充分测试新功能
3. 注意异步操作的正确使用
4. 保持代码文档的更新 