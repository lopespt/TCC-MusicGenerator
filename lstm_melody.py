from gensim.models import KeyedVectors
from keras.models import Model, Sequential
from keras.layers import LSTM
from keras.layers import Dense
from sklearn.model_selection import train_test_split 
import numpy
import os
import json

# carrega o modelo word2vec treinado
def get_word2Vec_model(file_path):
    keyed_vectors = KeyedVectors.load(file_path)
    return keyed_vectors
    
# retorna todas as letras e melodias da base de dados
def get_all_lyrics_and_melody(midi_path_dir):

    data = dict({
        "lyrics": [],
        "melodies": []
    })

    for dir in os.listdir(midi_path_dir):

        midi_folder_path = os.path.join(midi_path_dir,dir)
        print(midi_folder_path)
        for file in os.listdir(midi_folder_path):

            if file == "letra.json":
                file_path = os.path.join(midi_folder_path, file)
                with open(file_path, encoding='utf-8') as json_file:
                    lyics_object = json.load(json_file)
                    lyrics_vec = ret_lyrics_vec(lyics_object)
                    data["lyrics"].append(lyrics_vec)
            if file == "melodia.json":
                file_path = os.path.join(midi_folder_path, file)
                with open(file_path, encoding='utf-8') as json_file:
                    melody_object = json.load(json_file)
                    melody_vec = ret_melody_vec(melody_object)
                    data["melodies"].append(melody_vec)

    return data
                
def ret_melody_vec(melody_object):
    return melody_object["melodia"]

def ret_lyrics_vec(lyics_object):
    return lyics_object["letra"]

def get_word_from_lyrics_vector(lyrics_vector):
    words = []

    for word in lyrics_vector:
        words.append(word)
    
    return words

# retorna a matriz contendo todos os vetores de supervisão no formato [pitch, inicio, fim] de todas as musicas
def get_all_supervised_vectors(data):

    supervised_vectors = []

    for i in range(len(data["melodies"])):
        supervised_vector = get_supervised_vector(data["lyrics"][i], data["melodies"][i])
        for vector in supervised_vector:
            supervised_vectors.append(vector)

    return supervised_vectors

# retorna a matriz contendo todos os vetores numéricos obtidos pelo word2vec de todas as letras de musicas
def get_all_embedding_vectors(data, keyedVector):
    all_embedding_vectors = []

    for i in range(len(data["lyrics"])):
        words = get_word_from_lyrics_vector(data["lyrics"][i])
        lyrics_embedding_vector = get_lyrics_word_embedding(words, keyedVector)
        embedding_vector = get_word_embedding_vector(lyrics_embedding_vector)
        for embedding in embedding_vector:
            all_embedding_vectors.append(embedding)

    return all_embedding_vectors

# retorna o vetor contendo as palavras e os vetores numericos associados a ela obtidos atraves do word2vec
def get_lyrics_word_embedding(lyrics_vector, keyedVector):

    lyrics_embedding_vector =  []
    for lyric in lyrics_vector:
        word = lyric["texto"]
        for key in keyedVector.index_to_key:
            if key == word:
                embedding_dict = dict({
                    "word": word,
                    "vector": keyedVector.get_vector(word).tolist()
                })
                lyrics_embedding_vector.append(embedding_dict)     
    return lyrics_embedding_vector

# retorna o vetor de dados supervisionados com o formato [pitch, tempo_inicial, tempo_final] das notas tocadas no mesmo tempo da letra
def get_supervised_vector(lyrics_vector, melody_vector):
    
    supervised_vectors = []

    for word in lyrics_vector:
        for melody in melody_vector:
            if word["tempo"] >= melody["inicio"] and word["tempo"] <= melody["fim"] or word["tempo"] <= melody["inicio"]:
                supervided_vector = [melody["pitch"],melody["inicio"],melody["fim"]]
                supervised_vectors.append(supervided_vector)
                break
    return supervised_vectors

# separa os conjuntos de dados
def pre_process(embedding_vectors, supervised_vectors):
    embedding_vectors = numpy.array(embedding_vectors)
    supervised_vectors = numpy.array(supervised_vectors)

    print(embedding_vectors.shape, supervised_vectors.shape)

    X_train, X_test, Y_train, Y_test = train_test_split(embedding_vectors,supervised_vectors, test_size = 0.20, random_state = 4)

    X_train = numpy.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    X_test = numpy.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))
    Y_train = numpy.reshape(Y_train, (Y_train.shape[0], 1, Y_train.shape[1]))
    Y_test = numpy.reshape(Y_test, (Y_test.shape[0], 1, Y_test.shape[1]))

    return X_train,X_test,Y_train,Y_test


def lstm_model(supervised_vectors, embedding_vectors):
 
    model = Sequential()
    model.add(LSTM(3, batch_input_shape=(None,128,1), return_sequences=True))
    model.add(Dense(1, activation='linear'))
    
    model.compile(loss='mse', optimizer='adam')
    
    X_train,X_test,Y_train,Y_test = pre_process(supervised_vectors,embedding_vectors)

    model.fit(X_train, 
              Y_train, 
              validation_data=(X_test, Y_test),
              epochs=50)
   

# retorna o vetor numerico de uma determinada letra
def get_word_embedding_vector(lyrics_embedding_vector):

    word_embedding_vector = []

    for embedding_element in lyrics_embedding_vector:
        word_embedding_vector.append(embedding_element["vector"])

    return word_embedding_vector
    


keyed_vectors = get_word2Vec_model("/home/guimaj/Documentos/tcc/lyrics-vectors.kv") #path contendo o modelo word2vec exportado
data = get_all_lyrics_and_melody("/home/guimaj/Documentos/tcc/midi_teste") #path contendo as pastas dos midis extraidos
supervised_vectors = get_all_supervised_vectors(data)
print(len(supervised_vectors))
embedding_vectors  = get_all_embedding_vectors(data,keyed_vectors)

lstm_model(supervised_vectors, embedding_vectors)
