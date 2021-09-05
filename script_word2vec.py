# -*- coding: utf-8 -*-
from gensim.models import Word2Vec
import os
import json

def get_lyrics_vec(midi_path_dir):
    all_lyrics = []

    for dir in os.listdir(midi_path_dir):

        midi_folder_path = os.path.join(midi_path_dir,dir)

        for file in os.listdir(midi_folder_path):

            if file == "letra.json":
                file_path = os.path.join(midi_folder_path, file)
                with open(file_path, encoding='utf-8') as json_file:
                    lyics_object = json.load(json_file)
                    lyrics_vec = ret_lyrics_vec(lyics_object)
                    all_lyrics.append(lyrics_vec)
    return all_lyrics

def ret_lyrics_vec(lyics_object):
    lyrics_vec = []
    lyrics = lyics_object["letra"]

    for lyric_object in lyrics:
        lyric = lyric_object["texto"]
        lyrics_vec.append(lyric)

    return lyrics_vec

def save_word2Vec_result(all_lyrics, result_path):
    model = Word2Vec(all_lyrics, min_count=1)
    model.save(result_path + "/wor2vec.model")

def main():
    lyrics_vector = get_lyrics_vec("/home/guimaj/Documentos/tcc/midi/") 
    save_word2Vec_result(lyrics_vector, "/home/guimaj/Documentos/tcc/")

main() 