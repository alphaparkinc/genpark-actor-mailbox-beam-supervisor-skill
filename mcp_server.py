import sys
import json
from client import ActorMailboxDispatcher

dispatcher = ActorMailboxDispatcher()

def handle_call(name, arguments):
    if name == "register_actor":
        aid = arguments["actor_id"]
        dispatcher.register_actor(aid, lambda st, msg: {**st, "last_msg": msg})
        return {"status": "registered", "actor_id": aid}
    elif name == "send":
        ok = dispatcher.send(arguments["actor_id"], arguments["message"])
        return {"delivered": ok}
    elif name == "schedule":
        msgs = dispatcher.schedule_turn()
        return {"executed_messages": msgs}
    return {"error": f"Unknown tool: {name}"}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_call(req.get("name"), req.get("arguments", {}))
            print(json.dumps({"id": req.get("id"), "result": res}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
