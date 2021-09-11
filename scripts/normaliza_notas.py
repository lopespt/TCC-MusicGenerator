import json
import numpy as np

# Funcao para gerar o vetor das notas normalizados
def normaliza(path, divisor_dt):
    #path pro arquivo da letras.json
    f = open(path,)
    data = json.load(f)
    #extrai lista com os intrumentos do arquivo
    k = data['melodia']
    #acessar uma linha de notas do primeiro instrumento
    f.close()
    
    notas = []
    for i in k:
        temp = []
        temp.append(i.get("pitch")/89)
        temp.append(i.get("inicio"))
        temp.append(i.get("fim"))
        temp.append(i.get("duracao")/divisor_dt)
        notas.append(temp)
        
    return(notas)