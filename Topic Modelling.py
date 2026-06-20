from gensim.models.coherencemodel import CoherenceModel
from pathlib import Path
import re
import unicodedata
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# GUI
from tkinter import Tk, filedialog, messagebox, simpledialog

# NLTK
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
for pkg, res in [("stopwords","corpora/stopwords"),
                 ("punkt","tokenizers/punkt"),
                 ("wordnet","corpora/wordnet"),
                 ("omw-1.4","corpora/omw-1.4")]:
    try:
        nltk.data.find(res)
    except LookupError:
        nltk.download(pkg, quiet=True)

# Gensim
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from gensim.models.phrases import Phrases, Phraser  # correcto

# --- Config plots ---
TOPS = [10, 20, 30]
PLOT_COLORS = {10: "steelblue", 20: "darkorange", 30: "seagreen"}

# ---------- Normalización y filtros ----------
TOKEN_RE = re.compile(r"^[a-záéíóúñü]+(?:_[a-záéíóúñü]+)*$", re.IGNORECASE)  # permite bigramas con _
MIN_LEN = 3

def normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    return s.lower()

def is_valid_token(tok: str) -> bool:
    if len(tok) < MIN_LEN:
        return False
    return TOKEN_RE.match(tok) is not None

def token_contains_blocked(token: str, blocked: set[str]) -> bool:
    """Bloquea si el token es igual a una palabra prohibida o si CUALQUIERA de sus partes (split '_') lo es."""
    parts = token.split("_")
    return any(p in blocked for p in parts) or token in blocked

# ---------- Stopwords base ----------
def build_stopwords(lang_choice: str) -> set[str]:
    sw = set()
    if lang_choice == "en":
        try: sw |= set(stopwords.words("english"))
        except Exception: pass
    elif lang_choice == "es":
        try: sw |= set(stopwords.words("spanish"))
        except Exception: pass
    else:
        for lang in ("english", "spanish"):
            try: sw |= set(stopwords.words(lang))
            except Exception: pass
    sw |= {"would", "could", "also"}
    return {normalize_text(w) for w in sw}

# ---------- Tokenizado / preprocesado ----------
def tokenize_gfg_style(text: str) -> list[str]:
    t = normalize_text(text)
    t = re.sub(r"[^\w\s]", " ", t, flags=re.UNICODE)
    t = re.sub(r"\d+", " ", t)
    toks = t.split()
    toks = [tok for tok in toks if tok.isalpha()]
    return toks

def preprocess_docs(docs_raw: list[str], lang_choice: str, blocked: set[str]) -> list[list[str]]:
    sw = build_stopwords(lang_choice)
    lemmatizer = WordNetLemmatizer()
    processed = []
    for text in docs_raw:
        toks = tokenize_gfg_style(text)
        toks = [lemmatizer.lemmatize(t) for t in toks]   # lematiza
        toks = [t for t in toks if t not in sw]          # quita stopwords
        toks = [t for t in toks if is_valid_token(t)]    # regex/longitud
        toks = [t for t in toks if not token_contains_blocked(t, blocked)]  # quita prohibidas
        processed.append(toks)
    return processed

def apply_bigrams(texts_tok, min_count=2, threshold=10, blocked: set[str] = None):
    if blocked is None:
        blocked = set()
    bigram = Phrases(texts_tok, min_count=min_count, threshold=threshold)
    phraser = Phraser(bigram)
    out = []
    for doc in texts_tok:
        d = list(phraser[doc])                    # añade tokens con _
        d = [t for t in d if is_valid_token(t)]   # valida
        d = [t for t in d if not token_contains_blocked(t, blocked)]  # quita prohibidas (incluye partes del bigrama)
        out.append(d)
    return out

# ---------- LDA robusto ----------
def fit_lda_gfg(texts_tok: list[list[str]], num_topics: int, random_state: int = 42):
    n_docs = len(texts_tok)
    dictionary = Dictionary(texts_tok)
    if n_docs <= 1:
        no_below, no_above = 1, 1.0
    elif n_docs <= 5:
        no_below, no_above = 1, 0.9
    else:
        no_below, no_above = 2, 0.3
    dictionary.filter_extremes(no_below=no_below, no_above=no_above)
    if len(dictionary) == 0:
        dictionary = Dictionary(texts_tok)

    corpus = [dictionary.doc2bow(doc) for doc in texts_tok]
    if sum(len(bow) for bow in corpus) == 0 or len(dictionary) == 0:
        raise ValueError("El preprocesamiento dejó el vocabulario vacío.")

    vocab_size = len(dictionary)
    if num_topics > max(2, vocab_size):
        num_topics = max(2, min(num_topics, vocab_size))

    lda = LdaModel(
        corpus=corpus, id2word=dictionary, num_topics=num_topics,
        random_state=random_state, passes=12, iterations=200,
        alpha="asymmetric", eta=0.05, per_word_topics=False
    )
    return lda, dictionary, corpus

# ---------- Presentación ----------
def topic_terms_as_df(lda: LdaModel, topic_id: int, topn: int = 30) -> pd.DataFrame:
    terms = lda.show_topic(topic_id, topn=topn)
    return pd.DataFrame(terms, columns=["word", "weight"])

def plot_topic_bars(df: pd.DataFrame, topn: int, out_dir: Path, base_name: str, topic_label: str):
    sub = df.head(topn)
    if sub.empty:
        return
    words = sub["word"].tolist(); weights = sub["weight"].tolist()
    y = list(range(len(words) - 1, -1, -1))
    plt.figure(figsize=(10, 6))
    plt.barh(y, weights[::-1], color=PLOT_COLORS.get(topn, "gray"))
    plt.yticks(y, words[::-1])
    plt.xlabel("Peso (probabilidad en el tema)")
    plt.title(f"{topic_label} — Top-{topn} ({base_name})")
    plt.xlim(0, max(weights) * 1.05)
    plt.tight_layout()
    out_png = out_dir / f"{base_name}_{topic_label.replace(' ', '_')}_top{topn}.png"
    plt.savefig(out_png, dpi=150, bbox_inches="tight"); plt.close()

def format_topic_line(lda_model, topic_id: int, topn: int = 10) -> str:
    pairs = lda_model.show_topic(topic_id, topn=topn)
    parts = [f'{w:.3f}*"{term}"' for term, w in pairs]
    return f'({topic_id}, ' + "'" + " + ".join(parts) + "')"

# --- Exclusividad de palabras entre temas ---
def unique_top_words(lda, topn: int = 30, overshoot: int = 100, final_filter=None):
    used = set(); results = []
    for t in range(lda.num_topics):
        pairs = lda.show_topic(t, topn=overshoot)
        uniq = []
        for term, w in pairs:
            if final_filter and not final_filter(term):
                continue
            if term not in used:
                uniq.append((term, w)); used.add(term)
            if len(uniq) >= topn:
                break
        results.append(uniq)
    return results

def unique_topic_df_list(lda, topn=30, overshoot=100, final_filter=None):
    lists = unique_top_words(lda, topn=topn, overshoot=overshoot, final_filter=final_filter)
    return [pd.DataFrame(lst, columns=["word", "weight"]) for lst in lists]

# ---------- Main ----------
def main():
    root = Tk(); root.withdraw(); root.title("LDA — Uno o varios documentos")
    messagebox.showinfo("Documentos", "Elegí uno o varios archivos .txt para analizar con LDA")

    # 🔹 CAMBIO: permitir seleccionar VARIOS archivos
    paths = filedialog.askopenfilenames(
        title="Seleccioná el/los .txt del documento",
        filetypes=[("Text files", "*.txt")]
    )
    if not paths:
        messagebox.showwarning("Cancelado", "No seleccionaste ningún archivo .txt.")
        root.destroy(); return

    fps = [Path(p) for p in paths]

    # Parámetros
    try:
        num_topics = simpledialog.askinteger("Temas (K)", "¿Cuántos temas querés? (ej: 5)",
                                             minvalue=2, maxvalue=50, initialvalue=5)
        if not num_topics: root.destroy(); return
        lang_choice = simpledialog.askstring("Idioma stopwords",
                                             "Idioma stopwords: 'en', 'es' o 'both'",
                                             initialvalue="both") or "both"
        # Palabras prohibidas (separadas por coma)
        blocked_input = simpledialog.askstring(
            "Palabras prohibidas",
            "Escribí palabras a eliminar (separadas por coma). Ej: social, desarrollo",
            initialvalue=""
        ) or ""
        blocked = {normalize_text(x.strip()) for x in blocked_input.split(",") if x.strip()}
    except Exception:
        messagebox.showerror("Error", "Parámetros inválidos."); root.destroy(); return

    # Leer y preprocesar TODOS los documentos seleccionados
    docs_raw = [fp.read_text(encoding="utf-8", errors="ignore") for fp in fps]
    texts_tok = preprocess_docs(docs_raw, lang_choice, blocked=blocked)
    texts_tok = apply_bigrams(texts_tok, min_count=2, threshold=10, blocked=blocked)

    # ¿Quedaron tokens?
    if (not texts_tok) or all(len(doc) == 0 for doc in texts_tok):
        messagebox.showerror("Sin términos",
            "El preprocesamiento eliminó todos los términos.\n"
            "Ajusta las palabras prohibidas o las stopwords.")
        root.destroy(); return

    # Entrenar LDA robusto
    try:
        lda, dictionary, corpus = fit_lda_gfg(texts_tok, num_topics=num_topics, random_state=42)
    except ValueError as e:
        messagebox.showerror("LDA vacío", str(e)); root.destroy(); return

    # Temas + coherencia
    topic_lines = [format_topic_line(lda, t, topn=10) for t in range(lda.num_topics)]
    for line in topic_lines: print(line)

    try:
        cm = CoherenceModel(model=lda, texts=texts_tok, dictionary=dictionary, coherence="c_v")
        coherence = cm.get_coherence()
        print(f"\nCoherence Score:  {coherence:.12f}")
    except Exception as e:
        coherence = float("nan"); print(f"\n[Advertencia] No se pudo calcular coherencia c_v: {e}")

    # Filtro FINAL para presentación (incluye prohibidas)
    sw_final = build_stopwords(lang_choice)
    def final_filter(term: str) -> bool:
        term = normalize_text(term)
        if not is_valid_token(term): return False
        if term in sw_final: return False
        if token_contains_blocked(term, blocked): return False
        return True

    # Salidas
    out_dir = Path("./Gráficos"); out_dir.mkdir(parents=True, exist_ok=True)

    # 🔹 Nombre base: si es 1 doc, usamos su nombre; si son varios, un nombre genérico
    if len(fps) == 1:
        base = fps[0].stem
    else:
        base = "Compendio - Cátedra Matilda (Libros 1, 2 y 3)"

    (out_dir / f"{base}_topics_and_coherence.txt").write_text(
        "\n".join(topic_lines) + ("" if np.isnan(coherence) else f"\n\nCoherence Score:  {coherence:.12f}"),
        encoding="utf-8"
    )

    # EXCLUSIVOS sin repetir ENTRE temas + filtrado final (con prohibidas)
    max_top = max(TOPS)
    dfs_unique = unique_topic_df_list(lda, topn=max_top, overshoot=max_top*3, final_filter=final_filter)

    # Graficar/exportar
    all_topics_rows = []
    for t, df_t in enumerate(dfs_unique):
        if not df_t.empty:
            df_t = df_t[df_t["word"].apply(final_filter)]
        for n in TOPS:
            plot_topic_bars(df_t, n, out_dir, base_name=base, topic_label=f"Topic {t+1}")
        for _, row in df_t.iterrows():
            all_topics_rows.append({"topic": t+1, "word": row["word"], "weight": row["weight"]})

    pd.DataFrame(all_topics_rows).to_csv(out_dir / f"{base}_topics_all_EXCLUSIVE.csv",
                                         index=False, encoding="utf-8-sig")

    # 🔹 Distribución documento-tema para CADA documento
    rows_doc = []
    for fp, bow in zip(fps, corpus):
        dist = lda.get_document_topics(bow, minimum_probability=0.0)
        dist = sorted(dist, key=lambda x: x[0])
        row = {"doc": fp.name}
        for tid, prob in dist:
            row[f"topic_{tid+1}"] = prob
        rows_doc.append(row)

    pd.DataFrame(rows_doc).to_csv(out_dir / f"{base}_doc_topic_distribution.csv",
                                  index=False, encoding="utf-8-sig")

    if len(fps) == 1:
        info_docs = f"Documento: {fps[0].name}"
    else:
        info_docs = f"Documentos: {len(fps)} (ej: {fps[0].name}, ...)"

    messagebox.showinfo(
        "Listo ✅",
        f"{info_docs} | Temas: {lda.num_topics}\n"
        f"Salidas en: {out_dir.resolve()}\n\n"
        f"- {base}_Topic_X_top10/20/30.png (EXCLUSIVOS + prohibidas fuera)\n"
        f"- {base}_topics_all_EXCLUSIVE.csv\n"
        f"- {base}_doc_topic_distribution.csv\n"
        f"- {base}_topics_and_coherence.txt"
    )
    root.destroy()

if __name__ == "__main__":
    main()
