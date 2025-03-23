# AgentGPT 前端架构分析

## 架构概述

AgentGPT 前端使用 Next.js 框架实现，主要负责处理用户界面和与后端 API 的交互。前端部分的核心功能是创建和管理 Agent，执行任务，并展示执行结果。

## 核心组件

### 1. 主要类
- **AutonomousAgent**: 代理的主要实现，负责运行任务和处理工作流程
- **MessageService**: 负责消息的创建、更新和显示
- **AgentApi**: 处理与后端 API 的通信
- **DefaultAgentRunModel**: 管理代理运行状态和任务列表
- **AgentWork 系列类**: 实现不同类型的工作项（如任务分析、执行等）

### 2. 工作流实现类
- **StartGoalWork**: 开始目标任务，获取初始任务列表
- **AnalyzeTaskWork**: 分析任务，确定执行方法
- **ExecuteTaskWork**: 执行具体任务
- **CreateTaskWork**: 根据执行结果创建新任务
- **SummarizeWork**: 总结所有完成的任务
- **ChatWork**: 处理用户与 Agent 的聊天功能
## 数据流

### 1. Agent 创建流程
1. 用户在界面输入目标 → 触发 `handlePlay()` 函数
2. 如果是新的 Agent：创建 `DefaultAgentRunModel` 实例
3. 创建 `MessageService` 实例管理消息渲染
4. 创建 `AgentApi` 实例处理与后端通信
5. 创建 `AutonomousAgent` 实例，传入上述组件
6. 调用 `newAgent.run()` 开始执行

### 2. Agent 执行流程
1. Agent 执行 `run()` 方法
2. 初始化时加入 `StartGoalWork` 到工作队列
3. 循环处理工作队列中的工作项:
   - 执行工作项的 `run()` 方法
   - 工作完成后执行 `conclude()` 方法
   - 获取 `next()` 返回的下一个工作项（如果有）添加到队列
4. 如果工作队列为空，检查是否有待处理任务
5. 如果有，则创建 `AnalyzeTaskWork` 分析任务

### 3. 任务处理流程
1. `StartGoalWork`: 调用 API 获取初始任务列表，发送目标消息
2. `AnalyzeTaskWork`: 分析任务，确定执行方法（搜索、代码等）
3. `ExecuteTaskWork`: 执行任务，流式获取结果
4. `CreateTaskWork`: 根据执行结果创建新任务

## 状态管理

AgentGPT 使用自定义 store 来管理状态:
- **useAgentStore**: 管理 Agent 实例和生命周期状态
- **useMessageStore**: 管理消息列表
- **useTaskStore**: 管理任务列表
- **useAgentInputStore**: 管理用户输入

## 生命周期管理

Agent 的生命周期状态包括:
- **offline**: 未连接状态
- **running**: 正在运行
- **pausing**: 准备暂停
- **paused**: 已暂停
- **stopped**: 已停止

## 关键数据结构

### 1. Agent 模型
```typescript
interface AgentRunModel {
  getId(): string;
  getGoal(): string;
  getLifecycle(): AgentLifecycle;
  setLifecycle(AgentLifecycle): void;
  getRemainingTasks(): Task[];
  getCurrentTask(): Task | undefined;
  updateTaskStatus(task: Task, status: TaskStatus): Task;
  updateTaskResult(task: Task, result: string): Task;
  getCompletedTasks(): Task[];
  addTask(taskValue: string): void;
}
```

### 2. 任务分析结构
```typescript
type Analysis = {
  reasoning: string;
  action: "reason" | "search" | "wikipedia" | "image" | "code";
  arg: string;
};
```

### 3. 消息结构
```typescript
interface Message {
  type: string;
  value: string;
  status?: string;
  info?: string;
  id?: string;
  taskId?: string;
}
```

## 与后端交互

AgentGPT 前端通过 `AgentApi` 类与后端 API 交互，主要调用的接口有:
1. `/api/agent/start`: 获取初始任务列表
2. `/api/agent/analyze`: 分析任务
3. `/api/agent/execute`: 执行任务
4. `/api/agent/create`: 创建新任务
5. `/api/agent/summarize`: 总结任务结果

## 总结

AgentGPT 前端采用了模块化的设计，通过 AutonomousAgent 协调各类工作项的执行，实现了一个灵活的任务处理框架。系统通过工作队列管理不同类型的工作项，形成了一个完整的工作流程。前端与后端通过 API 接口进行交互，将用户目标转化为具体任务并执行，最终展示结果给用户。

这种设计使得系统能够灵活地处理各种类型的任务，并且可以方便地扩展新的功能。

## 详细工作流程解析

### Agent 完整工作流程与后端交互

AgentGPT 的任务处理是一个循环迭代的过程，前端与后端通过一系列 API 调用进行交互，下面详细说明整个流程：

#### 1. 用户输入目标，创建 Agent

**前端操作**：
- 用户在界面输入目标，点击开始按钮
- 前端调用 `handlePlay()` 函数，创建 Agent 实例

**代码实现**：
```typescript
// next/src/pages/index.tsx
const handleNewAgent = (goal: string) => {
  // 创建模型实例
  const model = new DefaultAgentRunModel(goal.trim());
  // 创建消息服务
  const messageService = new MessageService(addMessage);
  // 创建AgentApi
  const agentApi = new AgentApi({
    model_settings: toApiModelSettings(settings, session),
    goal: goal,
    session: session,
    agentUtils: agentUtils,
  });
  // 创建Agent实例
  const newAgent = new AutonomousAgent(
    model,
    messageService,
    settings,
    agentApi,
    session ?? undefined
  );
  // 存储Agent实例
  setAgent(newAgent);
  // 执行Agent
  newAgent?.run().then(console.log).catch(console.error);
};
```

#### 2. 初始化目标，获取初始任务

**前端流程**：
- `AutonomousAgent.run()` 方法启动执行
- 向工作队列添加 `StartGoalWork` 工作项
- 执行 `StartGoalWork.run()` 方法

**后端交互**：
- 前端调用 `/api/agent/start` 接口
- 后端使用 `start_goal_prompt` 提示词，让 LLM 分解目标生成初始任务列表
- 响应返回初始任务列表

**提示词示例**：
```
start_goal_prompt = PromptTemplate(
  template="""You are a task creation AI called AgentGPT. 
  You answer in the "{language}" language. You have the following objective "{goal}". 
  Create a list of zero to three tasks to help you fulfill your objective.""",
  input_variables=["goal", "language"],
)
```

**前端处理**：
```typescript
// agent-work/start-task-work.ts
run = async () => {
  const goalMessage = this.parent.messageService.sendGoalMessage(this.parent.model.getGoal());
  // 调用后端API获取初始任务
  this.tasksValues = await this.parent.api.getInitialTasks();
  await this.parent.api.createAgent();
  this.parent.api.saveMessages([goalMessage]);
};

conclude = async () => {
  // 创建任务消息并显示在界面上
  const messages = await this.parent.createTaskMessages(this.tasksValues);
  this.parent.api.saveMessages(messages);
};
```

#### 3. 分析任务

**前端流程**：
- 工作队列为空时，检查是否有未处理的任务
- 获取当前任务并创建 `AnalyzeTaskWork` 工作项
- 执行 `AnalyzeTaskWork.run()` 方法

**后端交互**：
- 前端调用 `/api/agent/analyze` 接口
- 后端使用 `analyze_task_prompt` 提示词，让 LLM 分析任务并选择合适的工具
- 响应返回任务分析结果 (Analysis 对象)

**提示词示例**：
```
analyze_task_prompt = PromptTemplate(
  template="""High level objective: "{goal}"
  Current task: "{task}"
  You can use tools to help you complete the task. Select the most suitable tool to use.""",
  input_variables=["goal", "task", "language"],
)
```

**前端处理**：
```typescript
// agent-work/analyze-task-work.ts
run = async () => {
  this.task = this.parent.model.updateTaskStatus(this.task, "executing");
  // 调用后端API分析任务
  this.analysis = await this.parent.api.analyzeTask(this.task.value);
};

conclude = async () => {
  // 发送分析消息
  let message: Message | undefined = undefined;
  if (this.analysis) {
    message = this.parent.messageService.sendAnalysisMessage(this.analysis);
  } else {
    message = this.parent.messageService.skipTaskMessage(this.task);
  }
  this.parent.api.saveMessages([message]);
};

next = () => {
  // 如果分析成功，创建执行任务工作项
  if (!this.analysis) return undefined;
  return new ExecuteTaskWork(this.parent, this.task, this.analysis);
};
```

#### 4. 执行任务

**前端流程**：
- 分析完成后，执行 `ExecuteTaskWork.run()` 方法
- 创建执行消息并显示在界面上

**后端交互**：
- 前端调用 `/api/agent/execute` 接口
- 后端根据分析结果选择对应的工具执行任务
- 响应以流式方式返回执行结果

**前端处理**：
```typescript
// agent-work/execute-task-work.ts
run = async () => {
  const executionMessage: Message = {
    ...this.task,
    id: v1(),
    status: "completed",
    info: "Loading...",
  };
  this.parent.messageService.sendMessage({ ...executionMessage, status: "completed" });

  // 调用后端API执行任务，流式获取结果
  await streamText(
    "/api/agent/execute",
    {
      run_id: this.parent.api.runId,
      goal: this.parent.model.getGoal(),
      task: this.task.value,
      analysis: this.analysis,
      model_settings: toApiModelSettings(this.parent.modelSettings, this.parent.session),
    },
    this.parent.api.props.session?.accessToken || "",
    () => {
      executionMessage.info = "";
    },
    (text) => {
      executionMessage.info += text;
      this.task = this.parent.model.updateTaskResult(this.task, executionMessage.info || "");
      this.parent.messageService.updateMessage(executionMessage);
    },
    () => this.parent.model.getLifecycle() === "stopped"
  );
  this.result = executionMessage.info || "";
  this.parent.api.saveMessages([executionMessage]);
  this.task = this.parent.model.updateTaskStatus(this.task, "completed");
};
```

#### 5. 创建新任务

**前端流程**：
- 任务执行完成后，如果没有更多的待处理任务，创建 `CreateTaskWork` 工作项
- 执行 `CreateTaskWork.run()` 方法

**后端交互**：
- 前端调用 `/api/agent/create` 接口
- 后端使用 `create_tasks_prompt` 提示词，让 LLM 根据已完成任务的结果创建新任务
- 响应返回新任务列表

**提示词示例**：
```
create_tasks_prompt = PromptTemplate(
  template="""You are an AI task creation agent. You have the following objective: "{goal}".
  You have the following incomplete tasks: {tasks}.
  The last task you completed was: "{last_task}" with the result: "{result}".
  Based on this result, create a list of 1-3 new tasks to be completed.""",
  input_variables=["goal", "tasks", "last_task", "result", "language"],
)
```

**前端处理**：
```typescript
// agent-work/create-task-work.ts
run = async () => {
  // 调用后端API创建新任务
  this.taskValues = await this.parent.api.getAdditionalTasks(
    {
      current: this.task.value,
      remaining: this.parent.model.getRemainingTasks().map((task) => task.value),
      completed: this.parent.model.getCompletedTasks().map((task) => task.value),
    },
    this.task.result || ""
  );
};

conclude = async () => {
  // 创建任务消息并显示在界面上
  const TIMEOUT_LONG = 1000;
  this.parent.api.saveMessages(await this.parent.createTaskMessages(this.taskValues));
  await new Promise((r) => setTimeout(r, TIMEOUT_LONG));
};
```

#### 6. 循环执行直至完成

**前端流程**：
- 如果还有待处理的任务，回到步骤 3 继续分析任务
- 如果所有任务都已完成，调用 `summarize()` 方法总结结果

**后端交互**：
- 前端调用 `/api/agent/summarize` 接口
- 后端使用总结提示词，让 LLM 总结所有任务的执行结果
- 响应以流式方式返回总结结果

**前端处理**：
```typescript
// agent-work/summarize-work.ts
run = async () => {
  const executionMessage: Message = {
    type: "task",
    status: "completed",
    value: `Summarizing ${this.parent.model.getGoal()}`,
    id: v1(),
    info: "Loading...",
  };
  this.parent.messageService.sendMessage({ ...executionMessage });

  // 调用后端API总结结果
  await streamText(
    "/api/agent/summarize",
    {
      run_id: this.parent.api.runId,
      goal: this.parent.model.getGoal(),
      model_settings: toApiModelSettings(this.parent.modelSettings, this.parent.session),
      results: this.parent.model
        .getCompletedTasks()
        .filter((task) => task.result && task.result !== "")
        .map((task) => task.result || ""),
    },
    this.parent.api.props.session?.accessToken || "",
    () => {
      executionMessage.info = "";
    },
    (text) => {
      executionMessage.info += text;
      this.parent.messageService.updateMessage(executionMessage);
    },
    () => this.parent.model.getLifecycle() === "stopped"
  );
  this.parent.api.saveMessages([executionMessage]);
};
```

### 具体案例分析

以下是一个创建市场调研报告的具体案例，展示整个工作流程：

#### 案例：创建市场调研报告

**用户输入目标**：
`创建一份关于人工智能在医疗领域应用的市场调研报告`

**初始任务列表**（从 `/api/agent/start` 返回）：
1. 收集人工智能在医疗领域的最新应用数据
2. 分析主要市场参与者和他们的产品
3. 调研市场规模和增长趋势

**任务1分析**（从 `/api/agent/analyze` 返回）：
```json
{
  "reasoning": "需要收集最新数据，搜索引擎是最合适的工具",
  "action": "search",
  "arg": "人工智能在医疗领域的最新应用 2023"
}
```

**任务1执行**（从 `/api/agent/execute` 流式返回）：
```
根据搜索结果，人工智能在医疗领域的最新应用包括：
1. 医学图像诊断：AI算法可以分析CT、MRI等医学图像，辅助医生进行诊断
2. 药物研发：加速新药发现和开发过程
3. 个性化治疗：基于患者数据提供定制化治疗方案
4. 远程医疗：通过AI辅助的远程监测和诊断系统
5. 预测性分析：预测疾病爆发和患者风险
...（更多内容）
```

**创建新任务**（从 `/api/agent/create` 返回）：
1. 深入分析AI医学图像诊断技术的主要参与者
2. 调研药物研发中的AI应用案例和效益

**循环继续**：
- 分析并执行新任务
- 根据执行结果创建更多任务
- 直至所有任务完成

**最终总结**（从 `/api/agent/summarize` 返回）：
```
人工智能在医疗领域的市场调研报告摘要：

市场概况：
AI医疗市场预计到2028年将达到1350亿美元，年复合增长率约38%。

主要应用领域：
1. 医学图像诊断：Google Health、Aidoc和Butterfly Network等公司引领
2. 药物研发：Insilico Medicine和Atomwise加速药物发现过程
3. 个性化治疗：IBM Watson和Tempus提供数据驱动的治疗决策
4. 远程医疗：Babylon Health和Ada Health扩展医疗可及性

市场趋势：
1. 监管环境逐渐明确，FDA已批准多个AI医疗设备
2. 医院采用率逐年提高，特别是在发达国家
3. 数据隐私保护成为关键考量因素
4. 与传统医疗系统的集成仍面临挑战

结论：
AI在医疗领域的应用正处于快速发展阶段，技术进步和市场需求共同推动行业增长。未来五年将是市场爆发期，投资机会丰富。
```

## 工作流程中的关键点

### 1. 任务来源
- **初始任务**：由后端 LLM 根据用户目标生成
- **后续任务**：由后端 LLM 根据已完成任务的结果和剩余任务生成
- 前端只负责展示和管理这些任务，实际的任务内容由后端的 LLM 决定

### 2. 工作流驱动机制
- 前端通过工作队列（`workLog`）管理整个工作流程
- 每个工作项（AgentWork）都有 `run()`、`conclude()` 和 `next()` 方法
- 系统通过这三个方法构建工作链，形成完整的执行流程
- `DefaultAgentRunModel` 维护任务状态，跟踪完成和待处理的任务

### 3. 前端与后端的职责划分
- **前端职责**：用户界面交互、工作流管理、状态维护、消息展示
- **后端职责**：LLM调用、任务生成、任务分析、工具执行
- 两者通过定义明确的API接口进行交互，形成完整的系统

通过这种前后端分离的架构，系统可以灵活地扩展功能，同时保持代码的清晰和可维护性。
