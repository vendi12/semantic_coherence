# -*- coding: utf-8 -*-
'''
svakulenko
17 Mar 2018

Load embeddings
'''
import numpy as np

import gensim
from keras.preprocessing.sequence import pad_sequences

from embeddings import entity_embeddings, word_embeddings
from prepare_dataset import load_vocabulary, LATEST_SAMPLE

PATH = './embeddings_npy/'


def load_word2vec(sample=LATEST_SAMPLE):
    vocabulary = load_vocabulary('./%s/words/vocab.pkl' % sample)
    save_to = './%s/words/%s.npy' % (sample, 'word2vec')
    embeddings_config =  word_embeddings['word2vec']
    # create a weight matrix for entities in training docs
    embedding_matrix = np.zeros((len(vocabulary), embeddings_config['dims']))
    # load embeddings binary model with gensim for word2vec and rdf2vec embeddings
    # model = gensim.models.Word2Vec.load(embeddings_config['path'])
    model = gensim.models.KeyedVectors.load_word2vec_format(embeddings_config['path'], binary=True)
    embedded_words = model.wv
    missing = 0
    for word, word_id in vocabulary.items():
        if word in embedded_words:
            embedding_matrix[word_id] = embedded_words[word]
        else:
            missing += 1
    print "Done loading word2vec embeddings. %d missing" % missing
    # save embedding_matrix
    np.save(save_to, embedding_matrix)
    # print embedding_matrix
    return embedding_matrix


def load_glove_word_embeddings(embeddings_name='GloVe', sample=LATEST_SAMPLE):
    vocabulary = load_vocabulary('./%s/words/vocab.pkl' % sample)
    # from https://machinelearningmastery.com/use-word-embedding-layers-deep-learning-keras/
    # create a weight matrix for entities in training docs
    embedding_matrix = np.zeros((len(vocabulary), word_embeddings[embeddings_name]['dims']))
    with open(word_embeddings[embeddings_name]['path']) as embs_file:
        embedding_matrix = load_embeddings(embs_file, embedding_matrix, vocabulary, entities=False)
        # save embedding_matrix for entities in the training dataset
        np.save(PATH+'GloVe%s.npy'%sample, embedding_matrix)
    print embedding_matrix


def load_embeddings(embeddings, embedding_matrix, vocabulary, entities=True):
    words = 0
    # embeddings in a text file one per line for Global vectors and glove word embeddings
    for line in embeddings:
        wordAndVector = line.split(None, 1)
        # match the entity labels in vector embeddings
        word = wordAndVector[0]
        if entities:
            word = word[1:-1]  # Dbpedia global vectors strip <> to match the entity labels 
        #print word
        if word in vocabulary:
            vector = wordAndVector[1]
            vector = vector.split()
            embedding_vector = np.asarray(vector, dtype='float32')
            embedding_matrix[vocabulary[word]] = embedding_vector
            
            words += 1
            if words >= len(vocabulary):
                break
    missing = len(vocabulary) - words
    print "done loading line based embedding. %d missing" % missing
    return embedding_matrix


def load_embeddings_lines(embeddings_config, label, vocabulary):
    # from https://machinelearningmastery.com/use-word-embedding-layers-deep-learning-keras/
    # create a weight matrix for entities in training docs
    embedding_matrix = np.zeros((len(vocabulary)+1, embeddings_config['dims']))
    with open(embeddings_config['path']) as embs_file:
        embedding_matrix = load_embeddings(embs_file, embedding_matrix, vocabulary)
        # save embedding_matrix for entities in the training dataset
        np.save(PATH+label+'.npy', embedding_matrix)
    #print embedding_matrix
    return embedding_matrix


def load_embeddings_gensim(embeddings_config, label, vocabulary, save_to):
    # create a weight matrix for entities in training docs
    embedding_matrix = np.zeros((len(vocabulary), embeddings_config['dims']))
        
    # load embeddings binary model with gensim for word2vec and rdf2vec embeddings
    model = gensim.models.Word2Vec.load(embeddings_config['path'])
    #model = gensim.models.KeyedVectors.load_word2vec_format(embeddings_config['path'], binary=True)
    embedded_entities = model.wv
    missing = 0
    for entity, entity_id in vocabulary.items():
        # strip entity label format to rdf2vec label format
        #rdf2vec_entity_label = 'dbr:%s' % entity.split('/')[-1]
        #print rdf2vec_entity_label
        rdf2vec_entity_label = '<' + entity + '>'
        if rdf2vec_entity_label in embedded_entities:
            embedding_matrix[entity_id] = embedded_entities[rdf2vec_entity_label]
        else:
            missing += 1
    print "done loading gensim entities. %d missing" % missing
    # save embedding_matrix for entities in the training dataset
    np.save(save_to, embedding_matrix)
    # print embedding_matrix
    return embedding_matrix


def load_entity_embeddings(sample=LATEST_SAMPLE):
    # dataset params
    entity_vocabulary = load_vocabulary('./%s/entities/vocab.pkl' % sample)

    for embeddings_name, config in embeddings['GlobalVectors'].items():
        try:
            label = 'GlobalVectors_' + embeddings_name
            print label
            load_embeddings_lines(config, label, entity_vocabulary)
        except Exception as e:
            print e

    for embeddings_name, config in embeddings['rdf2vec'].items():
        try:
            label = 'rdf2vec_' + embeddings_name
            print label
            load_embeddings_gensim(config, label, entity_vocabulary)
        except Exception as e:
            print e


if __name__ == '__main__':
    # load_glove_word_embeddings()
    load_word2vec()
    # path to the data set: './291848/entities/vocab.pkl'
    # load_entity_embeddings()
