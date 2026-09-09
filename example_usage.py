from client import ActorMailboxDispatcher

def main():
    print("=== Testing BEAM-Style Actor Mailbox & Supervisor ===")
    dispatcher = ActorMailboxDispatcher()

    def bank_handler(state, msg):
        op, amount = msg
        if op == "deposit":
            state["balance"] += amount
        elif op == "withdraw":
            if amount > state["balance"]:
                raise ValueError("Insufficient funds")
            state["balance"] -= amount
        return state

    dispatcher.register_actor("account_1", bank_handler, {"balance": 100})
    dispatcher.register_supervisor("bank_sup", ["account_1"], strategy="one_for_one")

    dispatcher.send("account_1", ("deposit", 50))
    dispatcher.send("account_1", ("withdraw", 30))
    dispatcher.schedule_turn(max_reductions=5)

    print("Account state after operations:", dispatcher.actors["account_1"]["state"])
    assert dispatcher.actors["account_1"]["state"]["balance"] == 120

    # Test crash and supervisor recovery
    dispatcher.send("account_1", ("withdraw", 9999))
    dispatcher.schedule_turn()
    print("Supervisor status for account_1:", dispatcher.actors["account_1"]["status"])
    assert dispatcher.actors["account_1"]["status"] == "alive"
    print("=== All tests passed successfully! ===")

if __name__ == "__main__":
    main()
