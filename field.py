from pyais.messages import MessageType1, MessageType5, MessageType18, MessageType24

types = {
    1: MessageType1,
    5: MessageType5,
    18: MessageType18,
    24: MessageType24,
}

for msg_type, cls in types.items():
    print(f"Type {msg_type} 字段：")
    for f in cls.fields():
        print(f"  {f}")
    print()
