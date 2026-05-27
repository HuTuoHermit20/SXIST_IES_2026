import os
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from agent_tool import tool_sim
from langchain_deepseek import ChatDeepSeek

load_dotenv(".env")

model = ChatDeepSeek(
    api_key=os.getenv("LLM_API_KEY"),
    model=os.getenv("LLM_ID"),
    base_url=os.getenv("LLM_BASE_URL"),
    temperature=0.1,
    timeout=60,
    max_tokens=2000,
    max_retries=10,
    extra_body={"thinking": {"type": "disabled"}},
)

agent = create_agent(
    model=model,
    tools=[tool_sim],
    system_prompt=
    """## 角色定义
    - 你是**山西科技学院招生办主任**，统筹山西科技学院的招生工作，了解山西科技学院的学校章程、
    校规校纪、负责解答普通高中应届毕业生或者高等专科学校应届毕业生的问题。

    ## 能力限定
    - 1.完全根据**山西科技学院官网**发布的所有关于山西科技学院的简介、章程、领导班子、历
    年招生计划、历年各专业录取最低分数线、招生政策、各二级学院的简介、专业设置、培养方案、学
    术成就、师资力量作答。**不胡编乱造**。
    - 2.若考生咨询该校的**录取概率**时，明确拒绝。
    - 3.若考生咨询某专业的**就业前景**时，建议该考生自行前往有关社交媒体查询。

    ## 交互风格
    - 严肃、冷静、毫无幽默。""",
    checkpointer=InMemorySaver()
)
