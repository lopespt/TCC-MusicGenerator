import numpy as np
from gensim.models import Word2Vec, KeyedVectors
import os
import json
from numpy import array 

#def get_sample_batch_size(notas, letras)
    
# Separa batch sample em n_steps
def split_seq(letras, notas, n_steps):
    X, y = list(), list()
    for i in range(len(letras)):
        # acha o final da sequencia
        end_ix = i + n_steps
        # checa se já passou da sequencia
        if end_ix > len(letras)-1:
            break
        # coleta o input e o outiput da sequencia
        seq_x, seq_y = letras[i:end_ix], notas[end_ix]
        X.append(seq_x)
        y.append(seq_y)
    return array(X), array(y)
