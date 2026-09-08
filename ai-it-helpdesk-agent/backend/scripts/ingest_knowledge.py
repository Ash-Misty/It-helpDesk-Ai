"""
Seed script for the IT Knowledge Base.
Safe to run multiple times - documents are re-indexed each run.
"""
from app.knowledge.knowledge_base import knowledge_base

def main():
    print(f"Knowledge base already contains {knowledge_base.count()} documents.")
    print("Documents are loaded from code at startup.")
    print("Available categories:")
    cats = {}
    for doc in knowledge_base.list_all():
        cat = doc["category"]
        cats[cat] = cats.get(cat, 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"  - {cat}: {count} documents")
    print(f"\nTotal: {knowledge_base.count()} knowledge documents indexed.")

if __name__ == "__main__":
    main()
