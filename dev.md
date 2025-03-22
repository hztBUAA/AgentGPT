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

## 测试驱动开发

### 1. 测试架构

#### 1.1 核心测试模块

1. **任务分析测试** (`test_analysis.py`)
```python
def test_analysis_model() -> None:
    valid_tool_name = get_tool_name(get_default_tool())
    analysis = Analysis(action=valid_tool_name, arg="arg", reasoning="reasoning")
    assert analysis.action == valid_tool_name
```
- 验证任务分析的正确性
- 测试工具选择逻辑
- 验证参数验证机制

2. **任务输出解析测试** (`test_task_output_parser.py`)
```python
def test_parse_success(input_text: str, expected_output: List[str]) -> None:
    parser = TaskOutputParser(completed_tasks=[])
    result = parser.parse(input_text)
    assert result == expected_output
```
- 测试任务格式解析
- 验证任务提取逻辑
- 处理各种输入格式

3. **模型工厂测试** (`test_model_factory.py`)
```python
def test_create_model(streaming, use_azure):
    result = create_model(settings, model_settings, user, streaming)
    assert issubclass(result.__class__, WrappedChatOpenAI)
```
- 测试模型创建逻辑
- 验证模型配置
- 检查API集成

### 2. 测试场景分析

#### 2.1 任务解析场景

1. **基础任务解析**
```python
@pytest.mark.parametrize(
    "task_input, expected_output",
    [
        ("Task: This is a sample task", "This is a sample task"),
        ("Step 1: Perform analysis", "Perform analysis"),
    ]
)
```
- 处理不同任务格式
- 移除前缀和标记
- 标准化输出

2. **复杂任务处理**
```python
def test_parse_with_completed_tasks() -> None:
    input_text = '["One", "Two", "Three"]'
    completed = ["One"]
    expected = ["Two", "Three"]
```
- 处理任务依赖
- 跟踪完成状态
- 维护任务队列

#### 2.2 模型集成测试

1. **模型配置验证**
```python
def test_custom_model_settings(model_settings: ModelSettings, streaming: bool):
    model = create_model(Settings(), model_settings, UserBase(), streaming)
    assert model.temperature == model_settings.temperature
```
- 验证模型参数
- 检查配置继承
- 测试自定义设置

2. **API集成测试**
```python
def test_helicone_enabled_without_custom_api_key():
    base, headers, use_helicone = get_base_and_headers(settings, model_settings, user)
```
- 测试API连接
- 验证认证机制
- 检查错误处理

### 3. 二次开发指南

#### 3.1 测试驱动开发流程

1. **编写测试用例**
```python
def test_custom_workflow():
    workflow = CustomWorkflow(config)
    result = workflow.execute(task)
    assert result.status == "completed"
```

2. **实现功能代码**
```python
class CustomWorkflow:
    def execute(self, task: Task) -> Result:
        # 实现自定义工作流逻辑
        pass
```

3. **验证和迭代**
- 运行测试套件
- 修复失败的测试
- 重构和优化

#### 3.2 测试覆盖场景

1. **工作流测试**
- 任务创建和分解
- 执行流程控制
- 结果验证

2. **工具集成测试**
- 工具调用机制
- 参数传递
- 错误处理

3. **模型交互测试**
- 提示词处理
- 响应解析
- 上下文管理

#### 3.3 最佳实践

1. **测试组织**
- 按功能模块组织测试
- 使用参数化测试
- 维护测试数据

2. **异常处理**
- 测试边界条件
- 验证错误响应
- 检查恢复机制

3. **性能考虑**
- 模拟外部依赖
- 优化测试执行
- 监控资源使用

### 4. 核心功能函数解析

#### 4.1 任务输出解析器 (TaskOutputParser)

```python
class TaskOutputParser(BaseOutputParser[List[str]]):
    def parse(self, text: str) -> List[str]:
        array_str = extract_array(text)
        all_tasks = [
            remove_prefix(task) for task in array_str if real_tasks_filter(task)
        ]
        return [task for task in all_tasks if task not in self.completed_tasks]
```

功能流程：
1. 接收模型输出的文本
2. 提取任务数组
3. 移除任务前缀
4. 过滤无效任务
5. 排除已完成任务

关键辅助函数：
- `extract_array`: 从文本中提取任务数组
- `remove_prefix`: 移除任务前缀（如"Task 1:", "Step 1:"等）
- `real_tasks_filter`: 过滤无效或完成的任务

#### 4.2 任务分析器 (Analysis)

```python
class Analysis(AnalysisArguments):
    action: str

    @validator("action")
    def action_must_be_valid_tool(cls, v: str) -> str:
        if v not in get_available_tools_names():
            raise ValueError(f"Analysis action '{v}' is not a valid tool")
        return v
```

功能特点：
1. 验证工具动作的有效性
2. 处理搜索动作的特殊要求
3. 提供默认分析结果

使用场景：
- 任务分析阶段
- 工具选择验证
- 参数验证

#### 4.3 工具管理 (Tool System)

```python
def get_tool_name(tool: Type[Tool]) -> str:
    return format_tool_name(tool.__name__)

def get_tool_from_name(tool_name: str) -> Type[Tool]:
    for tool in get_available_tools():
        if get_tool_name(tool) == format_tool_name(tool_name):
            return tool
    return get_default_tool()
```

核心功能：
1. 工具名称标准化
2. 工具查找和获取
3. 默认工具回退机制

工具注册流程：
1. 继承Tool基类
2. 实现必要方法
3. 注册到工具系统

#### 4.4 Agent服务实现

```python
class OpenAIAgentService(AgentService):
    async def analyze_task_agent(
        self, *, goal: str, task: str, tool_names: List[str]
    ) -> Analysis:
        user_tools = await get_user_tools(tool_names, self.user, self.oauth_crud)
        functions = list(map(get_tool_function, user_tools))
        # ... 实现分析逻辑
```

主要流程：
1. 目标初始化
2. 任务分析
3. 工具选择
4. 任务执行
5. 结果汇总

#### 4.5 开发注意事项

1. **任务解析**
   - 处理各种输入格式
   - 维护任务状态
   - 处理边界情况

2. **工具系统**
   - 工具注册机制
   - 权限控制
   - 错误处理

3. **服务集成**
   - 异步操作
   - 状态管理
   - 资源释放

4. **测试覆盖**
   - 单元测试
   - 集成测试
   - 性能测试

#### 4.6 自定义开发示例

1. **自定义任务解析器**
```python
class CustomTaskParser(TaskOutputParser):
    def parse(self, text: str) -> List[str]:
        # 实现自定义解析逻辑
        pass
```

2. **自定义分析器**
```python
class CustomAnalysis(Analysis):
    additional_field: str
    
    @validator("additional_field")
    def validate_field(cls, v: str) -> str:
        # 实现自定义验证
        pass
```

3. **自定义工具**
```python
class CustomTool(Tool):
    description = "自定义工具描述"
    
    async def call(self, goal: str, task: str, input_str: str, *args, **kwargs):
        # 实现工具逻辑
        pass
```

## Agent模块核心组件

### 1. 流式响应处理 (Stream Mock)

#### 1.1 基本组件
```python
def stream_string(data: str, delayed: bool = False) -> FastAPIStreamingResponse:
    return FastAPIStreamingResponse(
        stream_generator(data, delayed),
    )
```

功能说明：
- 提供流式响应能力
- 支持延迟模式模拟真实API响应
- 用于工具执行结果的实时返回

使用场景：
1. 工具执行结果返回
2. 任务分析过程展示
3. 代码生成实时反馈

#### 1.2 延迟处理
```python
async def stream_generator(data: str, delayed: bool) -> AsyncGenerator[bytes, None]:
    if delayed:
        encoding = tiktoken.get_encoding("cl100k_base")
        token_data = encoding.encode(data)
        for token in token_data:
            yield encoding.decode([token]).encode("utf-8")
            await asyncio.sleep(0.025)
    else:
        yield data.encode()
```

### 2. 提示词系统 (Prompts)

#### 2.1 核心提示词模板

1. **任务启动提示词** (`start_goal_prompt`)
```python
start_goal_prompt = PromptTemplate(
    template="""You are a task creation AI called AgentGPT. 
    You answer in the "{language}" language. You have the following objective "{goal}". 
    Return a list of search queries...""",
    input_variables=["goal", "language"],
)
```

2. **任务分析提示词** (`analyze_task_prompt`)
```python
analyze_task_prompt = PromptTemplate(
    template="""High level objective: "{goal}"
    Current task: "{task}"...""",
    input_variables=["goal", "task", "language"],
)
```

3. **代码生成提示词** (`code_prompt`)
```python
code_prompt = PromptTemplate(
    template="""You are a world-class software engineer...""",
    input_variables=["goal", "language", "task"],
)
```

#### 2.2 提示词使用流程

1. 任务初始化
   - 使用`start_goal_prompt`创建初始任务列表
   - 支持多语言响应
   - 生成搜索查询

2. 任务分析
   - 使用`analyze_task_prompt`分析具体任务
   - 选择合适的工具
   - 生成执行计划

3. 任务执行
   - 使用特定工具的提示词
   - 生成执行结果
   - 处理后续任务

### 3. 路由与请求处理

#### 3.1 核心路由

1. **启动任务** (`/start`)
```python
@router.post("/start")
async def start_tasks(
    req_body: AgentRun,
    agent_service: AgentService
) -> NewTasksResponse:
    new_tasks = await agent_service.start_goal_agent(goal=req_body.goal)
    return NewTasksResponse(newTasks=new_tasks, run_id=req_body.run_id)
```

2. **分析任务** (`/analyze`)
```python
@router.post("/analyze")
async def analyze_tasks(
    req_body: AgentTaskAnalyze,
    agent_service: AgentService
) -> Analysis
```

3. **执行任务** (`/execute`)
```python
@router.post("/execute")
async def execute_tasks(
    req_body: AgentTaskExecute,
    agent_service: AgentService
) -> FastAPIStreamingResponse
```

#### 3.2 服务流程

1. **请求验证**
   - 使用依赖注入进行请求验证
   - 检查必要参数
   - 验证用户权限

2. **服务处理**
   - 通过`AgentService`处理业务逻辑
   - 支持同步和异步操作
   - 处理错误和异常

3. **响应生成**
   - 使用`StreamingResponse`返回结果
   - 支持实时反馈
   - 处理长时间运行的任务

### 4. 二次开发指南

#### 4.1 扩展流程

1. **添加新的提示词模板**
```python
custom_prompt = PromptTemplate(
    template="""Your custom prompt template""",
    input_variables=["your_variables"],
)
```

2. **创建新的路由处理器**
```python
@router.post("/your_endpoint")
async def your_handler(
    req_body: YourRequestModel,
    agent_service: AgentService
) -> YourResponseModel:
    # Your implementation
    pass
```

3. **扩展Agent服务**
```python
class CustomAgentService(AgentService):
    async def your_custom_method(self, **kwargs: Any) -> Any:
        # Your implementation
        pass
```

#### 4.2 开发步骤

1. **理解现有组件**
   - 学习提示词系统
   - 了解路由处理流程
   - 掌握服务实现方式

2. **实现新功能**
   - 添加必要的提示词
   - 创建对应的路由
   - 实现服务逻辑

3. **测试和验证**
   - 单元测试
   - 集成测试
   - 性能测试

#### 4.3 注意事项

1. **提示词开发**
   - 保持语言一致性
   - 考虑多语言支持
   - 优化提示效果

2. **路由处理**
   - 合理使用依赖注入
   - 处理异常情况
   - 优化响应时间

3. **服务实现**
   - 遵循现有模式
   - 保持代码质量
   - 注意性能优化 