from agent_client import agent
from langchain.messages import HumanMessage

config = {"configurable":
              {"thread_id": "thread_20260520_1", "checkpoint_ns": ""},
          "recursion_limit": 100}

print("=" * 50)
print("山西科技学院招生智能体")
print("输入 'quit' 或 'exit' 退出对话")
print("=" * 50)

while True:
    user_input = input("\n你: ").strip()
    if user_input.lower() in ("quit", "exit", "q"):
        print("再见！")
        break
    if not user_input:
        continue

    print("智能体: ", end="", flush=True)
    messages = agent.stream(
        {"messages": [HumanMessage(content=user_input)]},
        stream_mode="messages",
        config=config,
    )
    for token, metadata in messages:
        if (token.content and not getattr(token, "tool_calls", None)
                and getattr(token, "type", None) != "tool"):
            print(token.content, end="", flush=True)
    print()
