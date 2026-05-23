"""
03_defense.py - Same six attacks, defended agent.

Runs the same six extraction techniques against SafeAgent, which applies
all three defense layers:

  Layer 1 (architectural): no secrets in the system prompt at all
  Layer 2 (output filtering): scans every response, redacts known-sensitive
                              strings before returning to user
  Layer 3 (refusal instructions): system prompt tells the model to refuse
                                  meta-queries about its own instructions

Layer 1 is doing most of the work here. There are simply no secrets in the
prompt for the model to leak. Layer 2 catches anything that slips through.
Layer 3 makes the refusals feel polished.

Run:
    python -m examples.03_defense
"""

from dotenv import load_dotenv

from src.attack_techniques import ATTACK_TECHNIQUES
from src.safe_agent import SafeAgent

load_dotenv()


def main():
    agent = SafeAgent()
    results = []

    for i, attack in enumerate(ATTACK_TECHNIQUES, start=1):
        print(f"\n=== Attack {i}/{len(ATTACK_TECHNIQUES)}: {attack['name']} ===")
        print(f"Query: {attack['query']}\n")

        result = agent.respond(attack["query"])
        print(f"--- Agent response ---\n{result['answer']}\n")
        if result["leakage_detected"]:
            print(f"LAYER 2 CAUGHT: {result['leakage_detected']}")
            print("(The response was redacted before being shown above.)")
        else:
            print("Layer 2: no sensitive patterns detected.")

        results.append({
            "technique": attack["name"],
            "leakage_caught_by_filter": result["leakage_detected"],
        })

    print("\n\n=== Summary ===")
    print("Layer 1 (no secrets in prompt) is the primary defense — the model")
    print("can't leak what isn't there. Layer 2 (output filter) adds safety net.")
    print("Layer 3 (refusal instructions) handles the polite-decline UX.")
    print()
    for r in results:
        if r["leakage_caught_by_filter"]:
            print(f"  Layer 2 filtered  - {r['technique']:35} {r['leakage_caught_by_filter']}")
        else:
            print(f"  Layer 1 sufficient - {r['technique']}")

    print("\nEXPECTED: zero verbatim sensitive content reaches the user.")
    print("Most attacks get a clean refusal from Layer 3 + nothing-to-leak")
    print("from Layer 1. If any did slip through Layer 1+3, Layer 2 caught them.")


if __name__ == "__main__":
    main()
