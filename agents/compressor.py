"""
agents/compressor.py
Compresses repeated constraints in memory.
"""
from agents.memory import load_memory, save_memory

def compress_memory():
    mem = load_memory()
    before_count = len(mem.get("learned_constraints", []))
    original = mem.get("learned_constraints", []).copy()
    compressed = set()
    for c in original:
        cl = c.lower()
        if "trap" in cl:
            compressed.add("reject actions with immediate lethal next-state risk")
        elif "enemy" in cl or "timing" in cl:
            compressed.add("timing-sensitive enemy risk must be evaluated before navigation")
        elif "key" in cl and "door" in cl:
            compressed.add("key must be obtained before attempting door")
        elif "bonus" in cl:
            compressed.add("bonus collection cannot override survival constraint")
        else:
            compressed.add(c)
    final = list(compressed)
    mem["learned_constraints"] = final
    mem["version_notes"].append(f"Compressed: before={before_count}, after={len(final)}")
    save_memory(mem)
    return {
        "before_constraint_count": before_count,
        "after_constraint_count": len(final),
        "removed_duplicates": before_count - len(final),
        "compressed_constraints": final
    }
