import collections

class ActorMailboxDispatcher:
    """
    Erlang/BEAM-style Reduction-Based Preemptive Actor System.
    Actors possess private state and lock-free mailboxes.
    Supervision tree handles fault tolerance with restart strategies.
    """
    def __init__(self):
        self.actors = {}
        self.supervisors = {}

    def register_actor(self, actor_id, handler, initial_state=None):
        self.actors[actor_id] = {
            "handler": handler,
            "state": initial_state or {},
            "mailbox": collections.deque(),
            "reductions": 0,
            "status": "alive"
        }

    def send(self, actor_id, message):
        if actor_id in self.actors and self.actors[actor_id]["status"] == "alive":
            self.actors[actor_id]["mailbox"].append(message)
            return True
        return False

    def schedule_turn(self, max_reductions=4):
        executed_messages = 0
        for actor_id, act in list(self.actors.items()):
            if act["status"] != "alive":
                continue
            reds = 0
            while act["mailbox"] and reds < max_reductions:
                msg = act["mailbox"].popleft()
                try:
                    act["state"] = act["handler"](act["state"], msg)
                    reds += 1
                    act["reductions"] += 1
                    executed_messages += 1
                except Exception as e:
                    act["status"] = f"crashed: {e}"
                    self._handle_crash(actor_id)
                    break
        return executed_messages

    def register_supervisor(self, sup_name, children, strategy="one_for_one"):
        self.supervisors[sup_name] = {"children": list(children), "strategy": strategy}

    def _handle_crash(self, crashed_child):
        for sup_name, sup in self.supervisors.items():
            if crashed_child in sup["children"]:
                if sup["strategy"] == "one_for_one":
                    self.actors[crashed_child]["status"] = "alive"
                    self.actors[crashed_child]["mailbox"].clear()
                elif sup["strategy"] == "all_for_one":
                    for ch in sup["children"]:
                        self.actors[ch]["status"] = "alive"
                        self.actors[ch]["mailbox"].clear()
