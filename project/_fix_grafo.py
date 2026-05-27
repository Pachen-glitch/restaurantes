from pathlib import Path
import re
text = Path("recommendation.py").read_text(encoding="utf-8")
text2 = re.sub(
    r"def obtener_datos_grafo\(focus_user_id=None\):.*?return \{\"nodes\": list\(nodes\.values\(\)\), \"edges\": edges\}",
    open("_grafo_fn.txt", encoding="utf-8").read().strip(),
    text,
    count=1,
    flags=re.S,
)
Path("recommendation.py").write_text(text2, encoding="utf-8")
print("ok")