from langchain import PromptTemplate

# Create initial tasks using plan and solve prompting
# https://github.com/AGI-Edgerunners/Plan-and-Solve-Prompting
"""
    这个prompt是用来创建初始任务的。
    它根据给定的目标，生成一系列的搜索查询，这些查询将用于回答目标的全部内容。
    限制查询的数量为5个，并确保查询简洁。
    对于简单的问题，使用单个查询。
    返回的响应是一个JSON数组，包含字符串。
    
"""
start_goal_prompt = PromptTemplate(
    template="""You are a task creation AI called AgentGPT. 
You answer in the "{language}" language. You have the following objective "{goal}". 
Return a list of search queries that would be required to answer the entirety of the objective. 
Limit the list to a maximum of 5 queries. Ensure the queries are as succinct as possible. 
For simple questions use a single query.

Return the response as a JSON array of strings. Examples:

query: "Who is considered the best NBA player in the current season?", answer: ["current NBA MVP candidates"]
query: "How does the Olympicpayroll brand currently stand in the market, and what are its prospects and strategies for expansion in NJ, NY, and PA?", answer: ["Olympicpayroll brand comprehensive analysis 2023", "customer reviews of Olympicpayroll.com", "Olympicpayroll market position analysis", "payroll industry trends forecast 2023-2025", "payroll services expansion strategies in NJ, NY, PA"]
query: "How can I create a function to add weight to edges in a digraph using {language}?", answer: ["algorithm to add weight to digraph edge in {language}"]
query: "What is the current weather in New York?", answer: ["current weather in New York"]
query: "5 + 5?", answer: ["Sum of 5 and 5"]
query: "What is a good homemade recipe for KFC-style chicken?", answer: ["KFC style chicken recipe at home"]
query: "What are the nutritional values of almond milk and soy milk?", answer: ["nutritional information of almond milk", "nutritional information of soy milk"]""",
    input_variables=["goal", "language"],
)

"""
    这个prompt是用来分析任务的。
    它根据给定的目标和当前任务，生成一个分析结果。
    分析结果包括：
    1. 当前任务是否与目标相关。
    2. 当前任务是否需要更多的信息。
    3. 当前任务是否需要更多的步骤。
    4. 当前任务是否需要更多的查询。
"""
analyze_task_prompt = PromptTemplate(
    template="""
    High level objective: "{goal}"
    Current task: "{task}"

    Based on this information, use the best function to make progress or accomplish the task entirely.
    Select the correct function by being smart and efficient. Ensure "reasoning" and only "reasoning" is in the
    {language} language.

    Note you MUST select a function.
    """,
    input_variables=["goal", "task", "language"],
)

"""
    这个prompt是用来编写代码的。
    它根据给定的目标，生成一个代码片段。
    代码片段需要用英语编写，解释/注释需要用给定的语言编写。
    不要提供任何关于你自己的信息，专注于编写代码。
    确保代码没有错误，并通过注释解释复杂的概念。
"""
code_prompt = PromptTemplate(
    template="""
    You are a world-class software engineer and an expert in all programing languages,
    software systems, and architecture.

    For reference, your high level goal is {goal}

    Write code in English but explanations/comments in the "{language}" language.

    Provide no information about who you are and focus on writing code.
    Ensure code is bug and error free and explain complex concepts through comments
    Respond in well-formatted markdown. Ensure code blocks are used for code sections.
    Approach problems step by step and file by file, for each section, use a heading to describe the section.

    Write code to accomplish the following:
    {task}
    """,
    input_variables=["goal", "language", "task"],
)

"""
    这个prompt是用来执行任务的。
    它根据给定的目标和当前任务，生成一个执行结果。
    执行结果需要用给定的语言编写，并解释/注释需要用英语编写。
    不要提供任何关于你自己的信息，专注于执行任务。
    确保任务没有错误，并通过注释解释复杂的概念。
"""
execute_task_prompt = PromptTemplate(
    template="""Answer in the "{language}" language. Given
    the following overall objective `{goal}` and the following sub-task, `{task}`.

    Perform the task by understanding the problem, extracting variables, and being smart
    and efficient. Write a detailed response that address the task.
    When confronted with choices, make a decision yourself with reasoning.
    """,
    input_variables=["goal", "language", "task"],
)

"""
    这个prompt是用来创建任务的。
    它根据给定的目标和当前任务，生成一个新的任务。
    新的任务需要用给定的语言编写，并解释/注释需要用英语编写。
    不要提供任何关于你自己的信息，专注于创建任务。
    确保任务没有错误，并通过注释解释复杂的概念。
"""
create_tasks_prompt = PromptTemplate(
    template="""You are an AI task creation agent. You must answer in the "{language}"
    language. You have the following objective `{goal}`.

    You have the following incomplete tasks:
    `{tasks}`

    You just completed the following task:
    `{lastTask}`

    And received the following result:
    `{result}`.

    Based on this, create a single new task to be completed by your AI system such that your goal is closer reached.
    If there are no more tasks to be done, return nothing. Do not add quotes to the task.

    Examples:
    Search the web for NBA news
    Create a function to add a new vertex with a specified weight to the digraph.
    Search for any additional information on Bertie W.
    ""
    """,
    input_variables=["goal", "language", "tasks", "lastTask", "result"],
)

"""
    这个prompt是用来总结文本的。
    它根据给定的目标和文本，生成一个总结。
    总结需要用给定的语言编写，并解释/注释需要用英语编写。
    不要提供任何关于你自己的信息，专注于总结文本。
    确保总结没有错误，并通过注释解释复杂的概念。
"""
summarize_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    Combine the following text into a cohesive document:

    "{text}"

    Write using clear markdown formatting in a style expected of the goal "{goal}".
    Be as clear, informative, and descriptive as necessary.
    You will not make up information or add any information outside of the above text.
    Only use the given information and nothing more.

    If there is no information provided, say "There is nothing to summarize".
    """,
    input_variables=["goal", "language", "text"],
)

"""
    这个prompt是用来总结公司的。
    它根据给定的公司名称，生成一个总结。
    总结需要用给定的语言编写，并解释/注释需要用英语编写。
    不要提供任何关于你自己的信息，专注于总结公司。
    确保总结没有错误，并通过注释解释复杂的概念。
"""
company_context_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    Create a short description on "{company_name}".
    Find out what sector it is in and what are their primary products.

    Be as clear, informative, and descriptive as necessary.
    You will not make up information or add any information outside of the above text.
    Only use the given information and nothing more.

    If there is no information provided, say "There is nothing to summarize".
    """,
    input_variables=["company_name", "language"],
)

"""
    这个prompt是用来总结文本的。
    它根据给定的文本和目标，生成一个总结。
    总结需要用给定的语言编写，并解释/注释需要用英语编写。
    不要提供任何关于你自己的信息，专注于总结文本。
    确保总结没有错误，并通过注释解释复杂的概念。
"""
summarize_pdf_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    For the given text: "{text}", you have the following objective "{query}".

    Be as clear, informative, and descriptive as necessary.
    You will not make up information or add any information outside of the above text.
    Only use the given information and nothing more.
    """,
    input_variables=["query", "language", "text"],
)

"""
    这个prompt是用来总结文本的。
    它根据给定的文本和目标，生成一个总结。
    总结需要用给定的语言编写，并解释/注释需要用英语编写。
    不要提供任何关于你自己的信息，专注于总结文本。
    确保总结没有错误，并通过注释解释复杂的概念。
"""
summarize_with_sources_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    Answer the following query: "{query}" using the following information: "{snippets}".
    Write using clear markdown formatting and use markdown lists where possible.

    Cite sources for sentences via markdown links using the source link as the link and the index as the text.
    Use in-line sources. Do not separately list sources at the end of the writing.
    
    If the query cannot be answered with the provided information, mention this and provide a reason why along with what it does mention. 
    Also cite the sources of what is actually mentioned.
    
    Example sentences of the paragraph: 
    "So this is a cited sentence at the end of a paragraph[1](https://test.com). This is another sentence."
    "Stephen curry is an american basketball player that plays for the warriors[1](https://www.britannica.com/biography/Stephen-Curry)."
    "The economic growth forecast for the region has been adjusted from 2.5% to 3.1% due to improved trade relations[1](https://economictimes.com), while inflation rates are expected to remain steady at around 1.7% according to financial analysts[2](https://financeworld.com)."
    """,
    input_variables=["language", "query", "snippets"],
)

"""
    这个prompt是用来总结文本的。
    它根据给定的文本和目标，生成一个总结。
    总结需要用给定的语言编写，并解释/注释需要用英语编写。
    不要提供任何关于你自己的信息，专注于总结文本。
    确保总结没有错误，并通过注释解释复杂的概念。
"""
summarize_sid_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    Parse and summarize the following text snippets "{snippets}".
    Write using clear markdown formatting in a style expected of the goal "{goal}".
    Be as clear, informative, and descriptive as necessary and attempt to
    answer the query: "{query}" as best as possible.
    If any of the snippets are not relevant to the query,
    ignore them, and do not include them in the summary.
    Do not mention that you are ignoring them.

    If there is no information provided, say "There is nothing to summarize".
    """,
    input_variables=["goal", "language", "query", "snippets"],
)

"""
    这个prompt是用来聊天。
    它根据给定的文本和目标，生成一个总结。
    总结需要用给定的语言编写，并解释/注释需要用英语编写。
    不要提供任何关于你自己的信息，专注于总结文本。
    确保总结没有错误，并通过注释解释复杂的概念。
"""
chat_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    You are a helpful AI Assistant that will provide responses based on the current conversation history.

    The human will provide previous messages as context. Use ONLY this information for your responses.
    Do not make anything up and do not add any additional information.
    If you have no information for a given question in the conversation history,
    say "I do not have any information on this".
    """,
    input_variables=["language"],
)
