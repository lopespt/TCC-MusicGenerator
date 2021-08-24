# -*- coding: utf-8 -*-
import numpy as np
import pretty_midi
import os
import json, ast
import shutil
import re
import sys
from chord_extractor.extractors import Chordino

MIDI_PATH = '/home/guimaj/Documentos/'
SCORE_FILE = '/home/guimaj/Documentos/Mids.json'
MIDI_WITH_LYRICS_PATH = '/home/guimaj/Documentos/tcc/midi/'


def get_midi_chords(midi_file_path, midi_id):

    chordino = Chordino(roll_on=1) 
    conversion_file_path = chordino.preprocess(os.path.join(midi_file_path,midi_id + ".mid")) 
    chords = []

    for chord in chordino.extract(conversion_file_path):    
        chord_dict = dict({
            "nome": chord.chord,
            "tempo": chord.timestamp
        })
        chords.append(chord_dict) 
    
    midi_chords = dict({
        "midi_id": midi_id,
        "acordes": chords
    })

    return midi_chords

def create_folder(folder_name, base_path):
    path = os.path.join(base_path, folder_name)
    os.mkdir(path)

def get_midi_notes(instrument):
    
    notes = []

    for note in instrument.notes:
        
        note_dict = dict({
            "nome": pretty_midi.note_number_to_name(note.pitch),
            "pitch": note.pitch,
            "inicio": note.start,
            "fim": note.end,
            "duracao": note.get_duration()
        })
        notes.append(note_dict)

    return notes

def get_midi_instruments(instruments):

    instrument_list = []

    for instrument in instruments:
        instrument_dict = dict({
            "nome": pretty_midi.program_to_instrument_name(instrument.program),
            "notas": []
        })

        notas = get_midi_notes(instrument)

        instrument_dict["notas"].append(notas)
        instrument_list.append(instrument_dict)

    return instrument_list


def get_midi_lyrics(midi_file):

    lyrics = []

    lines = [0] + [n for n, lyric in enumerate(midi_file.lyrics) if '\r' in lyric.text]

    for start, end in zip(lines[:-1], lines[1:]):
        for lyric in midi_file.lyrics[start:end]:
            if lyric.text != '\r':    
                texto = re.sub('[.,:;@$#=!\/]',"",lyric.text).strip().rstrip('\x00').strip()   
                if texto != '':      
                    lyric_dict = dict({
                        "texto": texto,
                        "tempo": lyric.time
                    })
                    lyrics.append(lyric_dict)
    
    return lyrics

def msd_id_to_dirs(msd_id):
    return os.path.join(msd_id[2], msd_id[3], msd_id[4], msd_id)

def get_score_file():
    with open(SCORE_FILE,'r') as f:
        return json.load(f)

def export_lyric_file(midi_original_path, export_path):
    shutil.copy(midi_original_path, export_path)

def export_json_file(dict, file_path):
    out_file = open(file_path, "w")
   
    json.dump(dict, out_file, indent=3,ensure_ascii=False)
    
    out_file.close()

def get_midi_path(msd_id, midi_md5, kind):
    return os.path.join(MIDI_PATH, 'lmd_{}'.format(kind),
                        msd_id_to_dirs(msd_id), midi_md5 + '.mid')

def get_midi_info(midi_file, midi_id):
    midi_instruments = get_midi_instruments(midi_file.instruments)
    midi_lyrics = get_midi_lyrics(midi_file)
    midi_info = dict({
        "midi_id": midi_id,
        "instrumentos": midi_instruments,
        "letra": midi_lyrics
    })  
    return midi_info                    

def export_midi_chords(midi_id, file_path):
    midi_chords = get_midi_chords(file_path, midi_id)
    file_path = os.path.join(file_path, "acordes.json")
    export_json_file(midi_chords,file_path)

def export_midi_infos(midi_file, midi_id, file_path):
    midi_info = get_midi_info(midi_file, midi_id)
    file_path = os.path.join(file_path, "letras.json")
    export_json_file(midi_info,file_path)


def get_midi_with_lyrics(scores):

    while len(scores) > 0:
        try:
            msd_id, matches = scores.popitem()
            midi_with_max_score = ''
            midi_score = 0

            for midi_id in matches:
                
                if matches[midi_id] >  midi_score:
                    midi_score =  matches[midi_id] 
                    midi_with_max_score = midi_id

            midi_md5 = midi_with_max_score
            aligned_midi_path = get_midi_path(msd_id, midi_md5, 'aligned')
            midi_file = pretty_midi.PrettyMIDI(aligned_midi_path)
                
            if(len(midi_file.lyrics) > 5):
                create_folder(midi_md5,MIDI_WITH_LYRICS_PATH)
                export_lyric_file(aligned_midi_path, os.path.join(MIDI_WITH_LYRICS_PATH, midi_md5))
                export_midi_chords(midi_md5, os.path.join(MIDI_WITH_LYRICS_PATH,midi_md5))
                export_midi_infos(midi_file, midi_md5, os.path.join(MIDI_WITH_LYRICS_PATH,midi_md5)) 
        except:
            print("ocorreu um erro ao tentar recuperar os dados do arquivo MIDI")

def main():
    scores = get_score_file()
    get_midi_with_lyrics(scores)

main()
       
