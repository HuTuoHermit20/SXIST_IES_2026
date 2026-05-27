from agent_client import agent
from langchain.messages import HumanMessage

config = {"configurable": {"thread_id": "final1", "checkpoint_ns": ""}, "recursion_limit": 30}
out = open(r"F:\SXIST_IES_2026\agent_out.txt", "w", encoding="utf-8")

def ask(q, label):
    out.write(f"\n=== {label} ===\n")
    out.flush()
    msgs = agent.stream(
        {"messages": [HumanMessage(content=q)]},
        stream_mode="messages", config=config,
    )
    for t, m in msgs:
        if t.content and not getattr(t, "tool_calls", None) and getattr(t, "type", None) != "tool":
            out.write(t.content)
            out.flush()
    out.write("\n")

ask("大数据与计算机科学学院有哪些老师从事自然语言处理领域的研究？", "1-NLP教师查询")
ask("山西科技学院2025年在山东省的招生计划是怎样的？", "2-山东省招生计划")
ask("2025年面向山东省招生的各专业平均分是多少？", "3-山东省录取平均分")
ask("山西科技学院2025年本科招生章程的主要内容", "4-招生章程")

out.write("ALL DONE\n")
out.close()
