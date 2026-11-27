#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# reorganizar.sh
# Move cada pasta de artigo de artigos/ para o ano de estudo correspondente:
#     artigos/1994-alcubierre  ->  02-relatividade-geral/artigos/1994-alcubierre
#
# Uso (na raiz do projeto):
#     bash reorganizar.sh --teste    # só mostra o que faria, não mexe em nada
#     bash reorganizar.sh            # faz a mudança de verdade
#
# Depois de rodar:
#     git add -A && git status       # o Git reconhece os arquivos como "renamed"
# ---------------------------------------------------------------------------
set -euo pipefail

TESTE=0
[[ "${1:-}" == "--teste" ]] && TESTE=1

# Garante que o script roda na raiz do projeto, de onde quer que seja chamado
cd "$(dirname "$0")"
if [[ ! -f pyproject.toml || ! -d artigos ]]; then
    echo "Erro: rode este script na raiz do projeto (onde ficam pyproject.toml e artigos/)."
    exit 1
fi

# Ano de estudo de cada artigo (mesma distribuição do plano)
declare -A ANO=(
    [1988-morris-thorne]=01-fundamentos
    [1994-alcubierre]=02-relatividade-geral
    [1992-hawking]=03-condicoes-energia-causalidade
    [1996-everett]=03-condicoes-energia-causalidade
    [1997-everett-roman]=03-condicoes-energia-causalidade
    [1998-krasnikov]=03-condicoes-energia-causalidade
    [1998-olum]=03-condicoes-energia-causalidade
    [1999-van-den-broeck]=03-condicoes-energia-causalidade
    [2002-natario]=03-condicoes-energia-causalidade
    [1995-ford-roman]=04-energia-negativa-quantica
    [1997-lamoreaux]=04-energia-negativa-quantica
    [1997-pfenning-ford]=04-energia-negativa-quantica
    [2003-krasnikov]=04-energia-negativa-quantica
    [2004-lobo-visser]=04-energia-negativa-quantica
    [2009-finazzi]=04-energia-negativa-quantica
    [2012-mcmonigal]=05-fronteira-relatividade-numerica
    [2014-lee-cleaver]=05-fronteira-relatividade-numerica
    [2021-lentz]=05-fronteira-relatividade-numerica
    [2021-bobrick-martire]=05-fronteira-relatividade-numerica
    [2022-santiago]=05-fronteira-relatividade-numerica
    [2024-fuchs]=05-fronteira-relatividade-numerica
    [2024-clough]=05-fronteira-relatividade-numerica
    [2026-barzegar]=05-fronteira-relatividade-numerica
    [2026-le]=05-fronteira-relatividade-numerica
)

executa() {
    if (( TESTE )); then echo "  [teste] $*"; else "$@"; fi
}

movidos=0
faltando=0

echo "== Movendo artigos para os anos de estudo"
for artigo in $(printf '%s\n' "${!ANO[@]}" | sort); do
    origem="artigos/$artigo"
    destino="${ANO[$artigo]}/artigos/$artigo"
    if [[ ! -d "$origem" ]]; then
        if [[ -d "$destino" ]]; then
            echo "  já está no lugar: $destino"
        else
            echo "  AVISO: não encontrei $origem"
            faltando=$((faltando + 1))
        fi
        continue
    fi
    echo "  $origem  ->  $destino"
    executa mkdir -p "${ANO[$artigo]}/artigos"
    executa mv "$origem" "$destino"
    movidos=$((movidos + 1))

    # O fichamento ficou um nível mais fundo: corrige o caminho da bibliografia
    fich="$destino/fichamento.tex"
    if (( TESTE )); then
        echo "  [teste] corrigir \\bibliography em $fich"
    elif [[ -f "$fich" ]]; then
        sed -i 's#\\bibliography{\.\./\.\./referencias}#\\bibliography{../../../referencias}#' "$fich"
    fi
done

echo "== Índice dos artigos"
if [[ -f artigos/README.md ]]; then
    echo "  artigos/README.md  ->  ARTIGOS.md"
    executa mv artigos/README.md ARTIGOS.md
fi

echo "== Limpando a pasta artigos/ antiga"
if (( TESTE )); then
    echo "  [teste] remover artigos/ se estiver vazia"
elif [[ -d artigos ]]; then
    find artigos -type d -name __pycache__ -prune -exec rm -rf {} +
    if rmdir artigos 2>/dev/null; then
        echo "  artigos/ removida"
    else
        echo "  AVISO: artigos/ não está vazia; confira o que sobrou:"
        ls -A artigos
    fi
fi

echo
echo "Resumo: $movidos movidos, $faltando não encontrados."
if (( TESTE )); then
    echo "Isto foi só um teste. Para fazer de verdade: bash reorganizar.sh"
else
    echo "Próximo passo: git add -A && git status"
fi
