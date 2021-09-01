# -*- coding: utf-8 -*-
import pretty_midi
import os
import json
import shutil
import re
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


def writeMidi(notes,midi_id,file_path):
    # Create a PrettyMIDI object
    pianoMidi = pretty_midi.PrettyMIDI()
    # Create an Instrument instance for a cello instrument
    piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
    piano = pretty_midi.Instrument(program=piano_program)
    
    # Add the piano instrument to the PrettyMIDI object
    pianoMidi.instruments.append(piano)
    
    pianoMidi.instruments[0].notes = notes

    midi_path = os.path.join(file_path, midi_id) + "melody.mid"
  
    # Write out the MIDI data
    pianoMidi.write(midi_path)

def get_midi_instruments(instruments):

    instrument_list = []

    for instrument in instruments:
        notas = get_midi_notes(instrument)

        instrument_dict = dict({
            "nome": pretty_midi.program_to_instrument_name(instrument.program),
            "notas": notas
        })
        instrument_list.append(instrument_dict)

    return instrument_list


def get_midi_lyrics(midi_file):

    lyrics = []

    lines = [0] + [n for n, lyric in enumerate(midi_file.lyrics) if '\r' in lyric.text]

    for start, end in zip(lines[:-1], lines[1:]):
        for lyric in midi_file.lyrics[start:end]:
            if lyric.text != '\r':    
                texto = re.sub('[.,:;@$#=!\/?''*&()_]',"",lyric.text).strip().rstrip('\x00').strip()   
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

def get_midi_lyrics_object(midi_file, midi_id):
    midi_lyrics = get_midi_lyrics(midi_file)   
    midi_lyrics_object = dict({
        "midi_id": midi_id,
        "letra": midi_lyrics
    })   
    return midi_lyrics_object        

def export_midi_chords(midi_id, file_path):
    midi_chords = get_midi_chords(file_path, midi_id)
    file_path = os.path.join(file_path, "acordes.json")
    export_json_file(midi_chords,file_path)

def export_midi_lyrics(midi_file, midi_id, file_path):
    midi_lyrics = get_midi_lyrics_object(midi_file, midi_id)
    file_path = os.path.join(file_path, "letra.json")
    export_json_file(midi_lyrics,file_path)

def export_midi_melody(midi_file, midi_id, file_path):
    midi_melody = get_midi_melody(midi_file, midi_id, file_path)
    file_path = os.path.join(file_path, "melodia.json")
    export_json_file(midi_melody,file_path)

def export_midi_infos(midi_file, midi_id, file_path):
    midi_info = get_midi_info(midi_file, midi_id)
    file_path = os.path.join(file_path, "midi_infos.json")
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
                export_midi_melody(midi_file, midi_md5, os.path.join(MIDI_WITH_LYRICS_PATH,midi_md5))
                export_midi_lyrics(midi_file, midi_md5, os.path.join(MIDI_WITH_LYRICS_PATH,midi_md5))
                
        except:
            print("ocorreu um erro ao tentar recuperar os dados do arquivo MIDI")

def most_frequent(instrument_indexes):
    counter = 0
    index_most_frequeny = instrument_indexes[0]
     
    for instrument_index in instrument_indexes:
        curr_frequency = instrument_indexes.count(instrument_index)
        if(curr_frequency > counter):
            counter = curr_frequency
            index_most_frequeny = instrument_index
 
    return index_most_frequeny

def get_midi_melody(midi_file, midi_id, file_path):

    lyrics = []

    for lyric in midi_file.lyrics:
        lyrics.append(lyric)

    melody_instrument = midi_file.instruments[get_melody_instrument(midi_file,lyrics)]
    melody_notes = get_midi_notes(melody_instrument)
    
    midi_melody = dict({
        "midi_id": midi_id,
        "melodia": melody_notes
    })

    writeMidi(melody_instrument.notes, midi_id, file_path)

    return midi_melody


def get_melody_instrument(midi_file, lyrics):
    instrument_indexes = []

    for instrument in midi_file.instruments:
        for note in instrument.notes:
            for lyric in lyrics:
                if note.start == lyric.time:
                    instrument_indexes.append(midi_file.instruments.index(instrument))
    
    return most_frequent(instrument_indexes)

def main():
    scores = get_score_file()
    get_midi_with_lyrics(scores)

main()
       
