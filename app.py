from flask import Flask, render_template, request
import requests
import hashlib
import time

app = Flask(__name__)

# Cache simples em memória (termo -> (timestamp, livros)), expira em 5 min
_cache = {}
_CACHE_TTL = 300  # segundos


def _cache_key(termo):
    return hashlib.md5(termo.strip().lower().encode()).hexdigest()


def buscar_livros(termo):
    # remove espaços e hífens
    termo_limpo = termo.replace("-", "").replace(" ", "")
    termo_upper = termo_limpo.upper()

    # verifica se é ISBN
    if (
        (len(termo_upper) == 13 and termo_upper.isdigit()) or
        (len(termo_upper) == 10 and termo_upper[:-1].isdigit() and termo_upper[-1] in "0123456789X")
    ):
        query = f"isbn:{termo_upper}"
    else:
        query = termo

    key = _cache_key(termo)
    now = time.time()
    if key in _cache:
        cached_at, cached_livros = _cache[key]
        if now - cached_at < _CACHE_TTL:
            return cached_livros
        del _cache[key]

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": 10
    }

    try:
        print(f"🔍 Buscando por: {query}")
        response = requests.get(url, params=params, timeout=8)
        print(f"📡 Status da API: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Erro na API: status {response.status_code}")
            return []
        
        data = response.json()
        print(f"📚 Itens encontrados: {len(data.get('items', []))}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return []

    livros = []

    for item in data.get("items", []):
        info = item.get("volumeInfo", {})

        # 🔹 ISBN
        identificadores = info.get("industryIdentifiers", [])

        isbn_10 = "—"
        isbn_13 = "—"

        for ident in identificadores:
            if ident.get("type") == "ISBN_10":
                isbn_10 = ident.get("identifier")
            elif ident.get("type") == "ISBN_13":
                isbn_13 = ident.get("identifier")

        livros.append({
            "titulo": info.get("title", "Título desconhecido"),
            "autores": ", ".join(info.get("authors", ["—"])),
            "editora": info.get("publisher", "—"),
            "ano": info.get("publishedDate", "—")[:4],
            "paginas": info.get("pageCount", "—"),
            "categorias": ", ".join(info.get("categories", ["—"])),
            "descricao": info.get("description", "Sem descrição."),
            "capa": info.get("imageLinks", {}).get("thumbnail"),
            "link": info.get("previewLink", "#"),
            "isbn_10": isbn_10,
            "isbn_13": isbn_13
        })

    _cache[key] = (now, livros)
    return livros



@app.route("/", methods=["GET", "POST"])
def index():
    livros = []
    erro = None

    if request.method == "POST":
        termo = request.form.get("termo")
        if termo:
            livros = buscar_livros(termo)
            if not livros:
                erro = "Nenhum livro encontrado. Tente outro termo de busca."
        else:
            erro = "Digite algo para buscar."

    return render_template("index.html", livros=livros, erro=erro)


if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request
import requests
import hashlib
import time

app = Flask(__name__)

# Cache simples em memória (termo -> (timestamp, livros)), expira em 5 min
_cache = {}
_CACHE_TTL = 300  # segundos


def _cache_key(termo):
    return hashlib.md5(termo.strip().lower().encode()).hexdigest()


def buscar_livros(termo):
    # remove espaços e hífens
    termo_limpo = termo.replace("-", "").replace(" ", "")
    termo_upper = termo_limpo.upper()

    # verifica se é ISBN
    if (
        (len(termo_upper) == 13 and termo_upper.isdigit()) or
        (len(termo_upper) == 10 and termo_upper[:-1].isdigit() and termo_upper[-1] in "0123456789X")
    ):
        query = f"isbn:{termo_upper}"
    else:
        query = termo

    key = _cache_key(termo)
    now = time.time()
    if key in _cache:
        cached_at, cached_livros = _cache[key]
        if now - cached_at < _CACHE_TTL:
            return cached_livros
        del _cache[key]

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": 10
    }

    try:
        print(f"🔍 Buscando por: {query}")
        response = requests.get(url, params=params, timeout=8)
        print(f"📡 Status da API: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Erro na API: status {response.status_code}")
            return []
        
        data = response.json()
        print(f"📚 Itens encontrados: {len(data.get('items', []))}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return []

    livros = []

    for item in data.get("items", []):
        info = item.get("volumeInfo", {})

        # 🔹 ISBN
        identificadores = info.get("industryIdentifiers", [])

        isbn_10 = "—"
        isbn_13 = "—"

        for ident in identificadores:
            if ident.get("type") == "ISBN_10":
                isbn_10 = ident.get("identifier")
            elif ident.get("type") == "ISBN_13":
                isbn_13 = ident.get("identifier")

        livros.append({
            "titulo": info.get("title", "Título desconhecido"),
            "autores": ", ".join(info.get("authors", ["—"])),
            "editora": info.get("publisher", "—"),
            "ano": info.get("publishedDate", "—")[:4],
            "paginas": info.get("pageCount", "—"),
            "categorias": ", ".join(info.get("categories", ["—"])),
            "descricao": info.get("description", "Sem descrição."),
            "capa": info.get("imageLinks", {}).get("thumbnail"),
            "link": info.get("previewLink", "#"),
            "isbn_10": isbn_10,
            "isbn_13": isbn_13
        })

    _cache[key] = (now, livros)
    return livros



@app.route("/", methods=["GET", "POST"])
def index():
    livros = []
    erro = None

    if request.method == "POST":
        termo = request.form.get("termo")
        if termo:
            livros = buscar_livros(termo)
            if not livros:
                erro = "Nenhum livro encontrado. Tente outro termo de busca."
        else:
            erro = "Digite algo para buscar."

    return render_template("index.html", livros=livros, erro=erro)


if __name__ == "__main__":
    app.run(debug=True)
