import sys; sys.path.insert(0, '.')
from services.legal_rag import warmup, search, is_ready
warmup()
print("Ready:", is_ready())

results = search("acid attack punishment")
print("\nSearch: acid attack")
for r in results:
    act = r["act"]
    sec = r["section"]
    score = r["relevance_score"]
    print(f"  {act} {sec} - score: {score}")

results2 = search("what to do in kidnapping case")
print("\nSearch: kidnapping")
for r in results2:
    act = r["act"]
    sec = r["section"]
    score = r["relevance_score"]
    print(f"  {act} {sec} - score: {score}")
