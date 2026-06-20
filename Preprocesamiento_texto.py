import re
import string
from pathlib import Path
from collections import Counter
import pandas as pd
from unidecode import unidecode
import nltk
from nltk.corpus import stopwords
from tkinter import Tk, filedialog, messagebox

# spaCy para español
import spacy

# Asegurar stopwords en español descargadas
try:
    _ = stopwords.words("spanish")
except Exception:
    nltk.download("stopwords")

# ===================== CONFIGURACIÓN ===================== #
# Stopwords personalizadas propias
CUSTOM_STOPWORDS = [
    'que', 'los', 'del', 'las', 'por', 'para', 'con', 'una', 'como', 'mas', 'pero', 'sus',
    'este', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre',
    'tambien', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos',
    'uno', 'les', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'esto', 'antes',
    'algunos', 'unos', 'otro', 'otras', 'otra', 'tanto', 'esa', 'estos', 'mucho',
    'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar', 'estas', 'algunas',
    'algo', 'nosotros', 'mis', 'tus', 'ellas', 'nosotras', 'vosotros', 'vosotras', 'mio',
    'mia', 'mios', 'mias', 'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya', 'suyos',
    'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros',
    'vuestras', 'esos', 'esas', 'estoy', 'estamos', 'estais', 'estan', 'estes', 'estemos',
    'esteis', 'esten', 'estare', 'estaras', 'estara', 'estaremos', 'estareis', 'estaran',
    'has', 'hemos', 'habeis', 'han', 'haya', 'hayas', 'hayamos', 'hayan', 'ser', 'soy',
    'eres', 'somos', 'sois', 'son', 'sea', 'seas', 'seamos', 'seais', 'sean', 'cada',
    'fue', 'traves', 'tienen', 'puede', 'tener', 'vez', 'tiene', 'manera', 'solo', 'asi',
    'primer', 'pueden', 'dos', 'cal', 'dentro', 'fuera', 'partir', 'mismo', 'aun',
    'debe', 'cuales', 'cuanto', 'cuantos', 'siendo', 'sino', 'si no', 'tal vez', 'hace',
    'hacer', 'dar', 'tres', 'cuatro', 'cinco', 'hacia', 'fueron', 'sido', 'sera', 'tal',
    'bajo', 'mientras', 'fin', 'todas', 'todes', 'realizo', 'aunque', 'presentan',
    'respecto', 'menos', 'igual', 'embargo', 'alto', 'alta', 'segun', 'forma', 'paso',
    'pasos', 'permite', 'acuerdo', 'abordar', 'anterior', 'posterior', 'despues', 'mayor',
    'menor', 'medio', 'contexto', 'base', 'marco', 'podria', 'metodologia', 'indica',
    'indicando', 'indicar', 'tipo', 'observa', 'campo', 'campos', 'siguiente', 'siguientes',
    'primero', 'segundo', 'tercer', 'tercero', 'parte', 'partes', 'mediante', 'muestra',
    'objetivo', 'objetivos', 'ademas', 'cabo', 'momento', 'total', 'totales', 'lado',
    'lados', 'uso', 'muestran', 'encuentran', 'realiza', 'realizan', 'realizar', 'deben',
    'deberan', 'realizado', 'alrededor', 'encuentra', 'ello', 'elles', 'luego', 'mejor',
    'busca', 'acerca', 'misma', 'numero', 'grandes', 'gran', 'linea', 'lineas', 'dado',
    'trata', 'realizadas', 'realizada', 'realizados', 'observar', 'largo', 'resulta',
    'palabra', 'palabras', 'decir', 'medida', 'medidas', 'medido', 'dichas', 'hecho',
    'siempre', 'indice', 'multiple', 'multiples', 'principalmente', 'finalmente', 'ultimo',
    'determinar', 'requiere', 'continuacion', 'tomar', 'poner', 'mismas', 'mismos', 'implica',
    'especialmente', 'hacen', 'dicho', 'existe', 'saber', 'dicha', 'alguna', 'llevan',
    'lleva', 'considerar', 'muchas', 'permitio', 'particularmente', 'pesar', 'ambos',
    'puedan', 'ultimos', 'perciben', 'aquellos', 'aquellas', 'toma', 'consideran',
    'relacionadas', 'propone', 'determinan', 'haber', 'sigue', 'adelante', 'puesta',
    'surge', 'iniciales', 'reconoce', 'tales', 'entonces', 'realizaron', 'comun', 'final',
    'posee', 'poseer', 'asimismo', 'debido', 'tomando', 'considera', 'considerando',
    'pasado', 'logra', 'necesario', 'necesaria', 'necesarios', 'necesarias', 'alla',
    'alli', 'enfrentan', 'poseen', 'pagina', 'pretenden', 'pretende', 'establecen',
    'establece', 'etc...', 'etc', 'demas', 'cabe', 'constituye', 'hizo', 'toda', 'casi',
    'consisten', 'torno', 'existen', 'concepto', 'haciendo', 'solamente', 'incluso',
    'exclusivamente', 'observamos', 'explican', 'aborda', 'incluyendo', 'permiten',
    'constituyen', 'refiere', 'refieren', 'posibles', 'desarrolla', 'desarrollan',
    'historicamente,', 'directamente', 'él','sólo', 'según', 'además', 'través',
    'seleccionar', 'según', 'además', 'creado', 'fio', 'isi'
]

# Pronombres extra (refuerzo)
PRONOUNS_EXTRA = {
    "yo","me","mi","mí","conmigo","tu","tú","te","ti","contigo","vos","usted","ustedes",
    "el","él","ella","ello","nos","nosotros","nosotras","vosotros","vosotras",
    "ellos","ellas","se","sí","consigo",
    "mio","mía","mia","míos","mias","tuyo","tuya","tuyos","tuyas",
    "suyo","suya","suyos","suyas","nuestro","nuestra","nuestros","nuestras",
    "vuestro","vuestra","vuestros","vuestras","así","asi"
}

# Palabras que NO deben cambiar con lematización (evita Hondura)
LEMMA_EXCEPTIONS = {
    "honduras",
    "limón",
    "costaricense",
    # Podés agregar más si ves mutaciones raras
}

# Remociones avanzadas
REMOVE_PERSON_NAMES = True
REMOVE_NUMBER_WORDS = True
MIN_TOKEN_LEN = 3

# ======================================================== #

# Palabras-número comunes en español
ES_NUMBER_WORDS = {
    "cero","uno","una","un","dos","tres","cuatro","cinco","seis","siete",
    "ocho","nueve","diez","once","doce","trece","catorce","quince",
    "dieciseis","diecisiete","dieciocho","diecinueve","veinte","treinta",
    "cuarenta","cincuenta","sesenta","setenta","ochenta","noventa",
    "cien","ciento","doscientos","trescientos","cuatrocientos","quinientos",
    "seiscientos","setecientos","ochocientos","novecientos",
    "mil","miles","millon","millones","billon","billones",
    "primer","primero","primera","segundo","segunda",
    "tercer","tercero","tercera","cuarto","quinta","quinto",
    "sexto","septimo","octavo","noveno","decimo"
}

ROMAN_RE = re.compile(r"^(?=[MDCLXVI])(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))$", re.I)

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
NUMBER_RE = re.compile(r"\b\d+[\d.,]*\b")
PUNCT_TABLE = str.maketrans({c: " " for c in string.punctuation})
TOKEN_RE = re.compile(r"\b\w+\b", re.U)

# Cargar modelo spaCy en español
try:
    NLP_ES = spacy.load("es_core_news_sm")
except Exception:
    NLP_ES = None

USE_LEMMA = True


def remove_person_entities(original_text: str) -> str:
    """Quita nombres propios PERSON usando spaCy."""
    if NLP_ES is None:
        return original_text
    doc = NLP_ES(original_text)
    out = []
    last = 0
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            out.append(original_text[last:ent.start_char])
            last = ent.end_char
    out.append(original_text[last:])
    return "".join(out)


def clean_text(original_text: str, stopwords_set: set) -> str:
    """Limpieza completa con lematización spaCy segura."""
    text = original_text

    if REMOVE_PERSON_NAMES:
        text = remove_person_entities(text)

    text = text.lower()
    text = URL_RE.sub(" ", text)
    text = EMAIL_RE.sub(" ", text)
    text = NUMBER_RE.sub(" ", text)
    text = text.translate(PUNCT_TABLE)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = []

    if NLP_ES is not None:
        doc = NLP_ES(text)
        for tok in doc:
            if tok.is_space or tok.is_punct:
                continue

            surface = tok.text.lower().strip()

            if len(surface) < MIN_TOKEN_LEN:
                continue

            # --- Lematización segura ---
            if USE_LEMMA:
                lemma_candidate = tok.lemma_.lower().strip()

                if (
                    surface not in LEMMA_EXCEPTIONS and
                    tok.pos_ not in {"PROPN"} and
                    tok.ent_type_ not in {"LOC","GPE"} and
                    lemma_candidate
                ):
                    lemma = lemma_candidate
                else:
                    lemma = surface
            else:
                lemma = surface

            # stopwords
            if lemma in stopwords_set:
                continue

            # números
            if REMOVE_NUMBER_WORDS:
                if lemma in ES_NUMBER_WORDS or ROMAN_RE.match(lemma):
                    continue
                if lemma.endswith(("avo","ava","avos","avas")):
                    continue

            # adverbios -mente
            if len(lemma) >= 6 and lemma.endswith("mente"):
                continue

            # pronombres
            if tok.pos_ == "PRON" or lemma in PRONOUNS_EXTRA:
                continue

            tokens.append(lemma)

    else:
        # Sin spaCy
        raw_tokens = [t for t in TOKEN_RE.findall(text) if len(t) >= MIN_TOKEN_LEN]
        for t in raw_tokens:
            if t in stopwords_set:
                continue
            tokens.append(t)

    return " ".join(tokens)


def process_file(file_path: Path, output_dir: Path, stopwords_set: set):
    raw = robust_read_text(file_path)
    cleaned = clean_text(raw, stopwords_set)
    tokens = cleaned.split()
    freq = Counter(tokens)

    output_dir.mkdir(parents=True, exist_ok=True)
    clean_file = output_dir / f"{file_path.stem}_cleaned.txt"
    freq_file = output_dir / f"{file_path.stem}_frequencies.csv"

    clean_file.write_text(cleaned, encoding="utf-8")
    pd.DataFrame(freq.most_common(), columns=["word","frequency"]).to_csv(
        freq_file, index=False, encoding="utf-8-sig"
    )

    return clean_file, freq_file, len(tokens), len(freq)


def fix_mojibake(s: str) -> str:
    if "Ã" in s or "Â" in s:
        for enc in ("latin-1","cp1252"):
            try:
                t2 = s.encode(enc, errors="ignore").decode("utf-8", errors="ignore")
                if "Ã" not in t2 and "Â" not in t2:
                    return t2
            except:
                pass
    return s


def robust_read_text(p: Path) -> str:
    for enc in ("utf-8","utf-8-sig","cp1252","latin-1"):
        try:
            txt = p.read_text(encoding=enc, errors="strict")
            return fix_mojibake(txt)
        except:
            continue
    txt = p.read_text(encoding="utf-8", errors="ignore")
    return fix_mojibake(txt)


def main():
    es_sw = set(stopwords.words("spanish"))
    stopwords_set = es_sw | set(CUSTOM_STOPWORDS) | PRONOUNS_EXTRA

    root = Tk()
    root.withdraw()
    root.title("Preprocesamiento de texto")
    messagebox.showinfo("Seleccionar archivo", "Elegí el archivo .txt a limpiar 🧹")

    chosen = filedialog.askopenfilename(
        title="Seleccioná un .txt",
        filetypes=[("Archivos de texto","*.txt")]
    )
    if not chosen:
        messagebox.showwarning("Cancelado","No se seleccionó ningún archivo.")
        return

    file_path = Path(chosen)
    out_dir = Path("./Textos_finales")

    clean_file, freq_file, total, unique = process_file(file_path, out_dir, stopwords_set)

    messagebox.showinfo(
        "✅ Limpieza completada",
        f"Archivo: {file_path.name}\n\n"
        f"Palabras totales (post-limpieza): {total}\n"
        f"Palabras únicas: {unique}\n\n"
        f"Generado:\n- {clean_file.name}\n- {freq_file.name}"
    )


if __name__ == "__main__":
    main()
