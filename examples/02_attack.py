"""
02_attack.py - Six extraction techniques against the vulnerable agent.

Runs each of the six attack queries from src/attack_techniques.py against
the same vulnerable agent. For each one, checks the response against the
sensitive-pattern list and reports which secrets leaked.

Some techniques succeed dramatically. Some are partially blocked by the
model's own alignment. The point is to show the input attack surface is
unbounded: defense has to be architectural and output-side, because you
can't enumerate every possible extraction phrasing.

Run:
    python -m examples.02_attack
"""

from dotenv import load_dotenv

from src.attack_techniques import ATTACK_TECHNIQUES
from src.defenses import scan_for_leakage
from src.vulnerable_agent import VulnerableAgent

load_dotenv()


def main():
    agent = VulnerableAgent()
    results = []

    for i, attack in enumerate(ATTACK_TECHNIQUES, start=1):
        print(f"\n=== Attack {i}/{len(ATTACK_TECHNIQUES)}: {attack['name']} ===")
        print(f"Description: {attack['description']}")
        print(f"\nQuery: {attack['query']}\n")

        answer = agent.respond(attack["query"])
        leaks = scan_for_leakage(answer)

        print(f"--- Agent response ---\n{answer}\n")
        if leaks:
            print(f"LEAKED: {leaks}")
        else:
            print("No verbatim secret matches detected (may have leaked paraphrased content — check response).")

        results.append({"technique": attack["name"], "leaks": leaks})

    print("\n\n=== Summary ===")
    leaked_count = sum(1 for r in results if r["leaks"])
    print(f"{leaked_count}/{len(results)} techniques produced at least one verbatim leak")
    for r in results:
        marker = "  LEAKED " if r["leaks"] else "  clean  "
        print(f"  {marker} - {r['technique']:35} {r['leaks'] if r['leaks'] else ''}")

    print("\nEXPECTED: at least 3-4 techniques produce verbatim leaks (override")
    print("password, internal email addresses, promo code, customer PII).")
    print("Even ones marked 'clean' often leak paraphrased content - inspect")
    print("the responses above to see.")


if __name__ == "__main__":
    main()
