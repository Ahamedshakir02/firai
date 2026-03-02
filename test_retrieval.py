from core.retrieval_engine import find_similar_firs

test_text = """
A man was caught driving under influence of alcohol during highway patrol.
"""

results = find_similar_firs(test_text)

for r in results:
    print(r)