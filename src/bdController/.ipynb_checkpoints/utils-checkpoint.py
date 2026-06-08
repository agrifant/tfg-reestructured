import re

patterns = [
    re.compile(r'\bart[ií]culo\s*\d+(\.\d+)?\s*(bis|ter)?', re.IGNORECASE),
    re.compile(r'\bart\.?\s*\d+(\.\d+)?', re.IGNORECASE),
    re.compile(r'\b\d+(\.\d+)?\s*bis\b', re.IGNORECASE),
    re.compile(r'\b\d+(\.\d+)?\s*ter\b', re.IGNORECASE),
]

def filtrar_incluir(data: dict, incluir: list[str]) -> dict:
    return {k: v for k, v in data.items() if k in incluir}

def filtrar_excluir(data: dict, excluir: list[str]) -> dict:
    return {k: v for k, v in data.items() if k not in excluir}

def isArticulo(text: str) -> str | None:
    for p in patterns:
        match = p.search(text)
        if match:
            return match.group(0)
    return None

def normalize(d):
    vals = list(d.values())
    if not vals:
        return d
    min_v, max_v = min(vals), max(vals)
    if max_v == min_v:
        return {k: 0 for k in d}
    return {k: (v - min_v)/(max_v - min_v) for k, v in d.items()}

def top_k(semantic_results, keyword_results, k, alpha):
    """
    menor alfa-> mayor peso bm25
    """
    semantic_results = normalize(semantic_results)
    keyword_results = normalize(keyword_results)

    hybrid_scores = {}

    for doc_id in set(semantic_results) | set(keyword_results):
        v = semantic_results.get(doc_id, 0)
        b = keyword_results.get(doc_id, 0)

        hybrid_scores[doc_id] = alpha * v + (1 - alpha) * b

    ranked = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:k]