# Atalhos no Espaço-Tempo

> **PT** · Estudo de 6 anos (dez/2026 – nov/2032) sobre métricas de dobra (*warp drives*), buracos de minhoca atravessáveis, condições de energia e causalidade na Relatividade Geral, com reprodução numérica dos resultados em Python.
>
> **EN** · A 6-year self-study (Dec 2026 – Nov 2032) of warp-drive metrics, traversable wormholes, energy conditions and causality in General Relativity, reproducing published results numerically in Python.

Autor: **Tiago Rodrigues** ([@TiagoRodriguesskt](https://github.com/TiagoRodriguesskt))

## Sobre

O projeto acompanha a literatura na ordem em que ela foi construída: das métricas fundadoras (Morris & Thorne 1988, Alcubierre 1994) aos problemas de energia negativa e causalidade (1992–2009) e à fronteira atual (2021–2026). Cada artigo estudado ganha um fichamento em LaTeX e, sempre que possível, um script que reproduz o seu resultado principal.

## Estrutura

```
.
├── README.md
├── LICENSE                     # MIT (código)
├── requirements.txt            # dependências Python
├── referencias.bib             # bibliografia completa (24 referências)
├── plano-de-estudo.pdf         # plano de 6 anos
├── o-que-estudar.pdf           # pré-requisitos de matemática, física e computação
├── artigos/                    # uma pasta por artigo
│   ├── README.md               # índice dos artigos
│   └── 1994-alcubierre/
│       ├── README.md           # referência, links, status de leitura
│       ├── fichamento.tex      # resumo em LaTeX
│       ├── referencia.bib
│       └── codigo/             # reprodução dos resultados
├── 01-fundamentos/             # notas e projetos de cada ano do plano
├── 02-relatividade-geral/
├── 03-condicoes-energia-causalidade/
├── 04-energia-negativa-quantica/
├── 05-fronteira-relatividade-numerica/
└── 06-monografia/
```

## Como usar

**Ambiente Python**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Compilar um fichamento**

```bash
cd artigos/1994-alcubierre
pdflatex fichamento.tex && bibtex fichamento && pdflatex fichamento.tex && pdflatex fichamento.tex
```

## Artigos (PDFs)

Os PDFs dos artigos **não** fazem parte do repositório, porque são obras de terceiros. Cada pasta em `artigos/` traz os links do arXiv e do DOI; baixe e salve como `artigo.pdf` (o `.gitignore` já impede que eles sejam enviados).

## Progresso

| Ano | Fase | Status |
| --- | --- | --- |
| 1 | Fundamentos | Em andamento |
| 2 | Relatividade Geral | — |
| 3 | Condições de energia e causalidade | — |
| 4 | Energia negativa quântica | — |
| 5 | Fronteira e relatividade numérica | — |
| 6 | Monografia | — |

## Licença

- **Código** (arquivos `.py`, notebooks): [MIT](LICENSE).
- **Textos e fichamentos** (`.tex`, `.md`, PDFs próprios): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.pt-br): pode compartilhar e adaptar, desde que cite o autor.
- Os artigos citados pertencem aos seus autores e editoras.
