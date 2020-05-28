import requests
from json import dump
from json import loads
import os
import errno
import json
from csv import DictWriter


token = input("Informe seu token do github: ")
headers = {"Authorization": "Bearer " + token}

def run_query(query, headers): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

query = """
{
  search(query: "stars:>100 topic:machine-learning", type: REPOSITORY, first: 100{AFTER}) {
    nodes {
      ... on Repository {
        name
        primaryLanguage {
          name
        }
        languages(first: 1) {
          totalCount
        }
        url
        stargazers {
          totalCount
        }
        watchers {
          totalCount
        }
        forks {
          totalCount
        }
        diskUsage
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}

"""

#substituindo o comando after na consulta inicial
finalQuery = query.replace("{AFTER}", "")

#obtendo a primeira query
resultado = run_query(finalQuery, headers)

#carregando o json em um dicionario python
nodes = resultado['data']['search']['nodes']

#verificação se há proximas paginas e iniciando o contador de paginas
total_paginas = 1
prox_pagina  = resultado["data"]["search"]["pageInfo"]["hasNextPage"] 

while (total_paginas < 1000 and prox_pagina): 
    
    # montando as query subsequentes à primeira, 
    # detectando o cursor da ultima entrada da query anterior
    # adicionando o campo after na query do graphql
    # rodando o script com a nova query 
    # carregando o resultado json no dicionario do python
    cursor = resultado["data"]["search"]["pageInfo"]["endCursor"]
    next_query = query.replace("{AFTER}", ", after: \"%s\"" % cursor)
    resultado = run_query(next_query, headers)
    nodes += resultado['data']['search']['nodes']
    prox_pagina  = resultado["data"]["search"]["pageInfo"]["hasNextPage"]
    total_paginas += 1

#preparando o cabecalho do arquivo csv
with open("D:/VSCode-Workspace/TIS_VI/repositorios_ml.csv", "w") as Arquivo_Repositorios_ML:
    cabecalho = ['name', 'primaryLanguage', 'languages', 'url', 'stargazers','watchers', 'forks', 'diskUsage']
    writer = DictWriter(Arquivo_Repositorios_ML, fieldnames=cabecalho)
    writer.writeheader()

    #escrevendo no arquivo csv
    for node in nodes:
        writer.writerow(node)

print("Execucao encerrada!")