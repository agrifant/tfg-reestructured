import re

patterns = [
    re.compile(r'\bart[ií]culo\s*(\d+(\.\d+)?\s*(bis|ter|quater|quinquies)?)', re.IGNORECASE),
    re.compile(r'\bart\.?\s*(\d+(\.\d+)?)', re.IGNORECASE),
    re.compile(r'\b(\d+(\.\d+)?\s*bis)\b', re.IGNORECASE),
    re.compile(r'\b(\d+(\.\d+)?\s*ter)\b', re.IGNORECASE),
]


def extract_articulo(text: str) -> str | None:
    for p in patterns:
        match = p.search(text)
        if match:
            return match.group(1)  # 👈 clave aquí
    return None

def extract_articulos_more_than_one(text: str) -> list[str]:
    results = set()

    for p in patterns:
        matches = p.findall(text)
        for m in matches:
            if isinstance(m, tuple):
                m = m[0]
            results.add(m.strip().lower())

    return list(results)
