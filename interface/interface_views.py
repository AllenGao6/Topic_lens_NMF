from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse

from topiclens.settings import PROJECT_PATH

import os
import re
import operator
import warnings
import time
import numpy as np
import json

from sklearn.cluster import SpectralClustering
import gensim

import logging
import csv
import pickle

import numpy as np
from . import topic_tree as tt

from gensim.utils import lemmatize

# Dataset = 'CHO'
# Dataset = 'Tax'
Dataset = 'WtP-Part1'
#Dataset = 'WtP-Part2'

WorkDir = os.path.join(PROJECT_PATH, 'corex/')

### Preprocessing Begin ###
print("Preprocess begins...")
start = time.time()

try:
    TrainTexts = pickle.load(open(WorkDir + "train_texts.pickle", "rb"))
    AllWords = np.array(pickle.load(open(WorkDir + "all_words.pickle", "rb")))
    DocWord = pickle.load(open(WorkDir + "doc_word.pickle", "rb")).toarray()
    WVModel = pickle.load(open(WorkDir + "wv_model.pickle", "rb"))
    CompleteDocs = pickle.load(open(WorkDir + "complete_secs.pickle", "rb"))
except (OSError, IOError) as e:
    print("No such file(s).")


# --------------Preprocessing Phase-------------------------------

color_category30 = [
    "d3fe14",  "1da49c", "ccf6e9", "a54509", "7d5bf0", "d08f5d", "fec24c",  "0d906b", "7a9293", "7ed8fe",
    "d9a742",  "c7ecf9",  "72805e", "dccc69",  "86757e",  "a0acd2",  "fecd0f",  "4a9bda", "bdb363",  "b1485d",
    "b98b91",  "86df9c",  "6e6089", "826cae", "4b8d5f", "8193e5",  "b39da2", "5bfce4", "df4280", "a2aca6", "ffffff"]

def color_assign(array, parent):
    parent.assign_topic_color(array)

def update_topic_keys(topic_list, parent):
    parent.update_topic_keys(topic_list) #need to implement this tomorrow

def get_Topic_Keys(parent):
    parent.get_topic_keys()

def init_docs():
    complete_docs = []
    for doc_count in range(0, len(CompleteDocs)):
        doc = CompleteDocs[doc_count].copy()
        doc['idx'] = doc_count
        # indices = [i for i, x in enumerate(
        #   InitModel.labels[doc_count]) ]
        indices = [0, 1]
        doc['topic_ids_str'] = ' '.join(str(x) for x in indices)
        if (Dataset == 'WtP-Part1'):
            if float(doc['signature_count']) >= float(doc['signature_threshold']):
                doc['sig_percent'] = 100.0
            else:
                doc['sig_percent'] = 100.0 * \
                    float(doc['signature_count']) / \
                    float(doc['signature_threshold'])
        complete_docs.append(doc)
        #doc_count = doc_count + 1
        # CIR 需要 segmentation
    return complete_docs

def gen_cords(InitModel):
    global CorexCords
    doc_topics = InitModel.get_Doc_Topic()
    print(doc_topics.shape)
    '''
    doc_vecs = []
    for i in range(len(TrainTexts)):
        doc_vec = list(doc_topics[i])
        doc_vecs.append(doc_vec)
    '''
# fast t-SNE
    from tsne import bh_sne
    cords = bh_sne(doc_topics)
    #random_state=np.random.RandomState(10)
    print("check1")
# sklearn TSNE
    # from sklearn.manifold import TSNE
    # tsne = TSNE(n_components=2, random_state=RandomSeed)
    # cords = tsne.fit_transform(doc_vecs)
# PCA
    # from sklearn.decomposition import PCA
    # pca = PCA(n_components=2, random_state=RandomSeed)
    # cords = pca.fit_transform(doc_vecs)
    lines = []
    for i in range(doc_topics.shape[0]):
        line = {'cord_x': str(cords[i][0]),
                'cord_y': str(cords[i][1]),
                'body': CompleteDocs[i]['body'],
                'title': CompleteDocs[i]['title'],
                'doc_id': str(i)}
        topic_idx = 0
        for j in range(doc_topics.shape[1]):
            line['topic_' + str(j)] = doc_topics[i][j]
            if (doc_topics[i][j] >= doc_topics[i][topic_idx]):
                topic_idx = j
        line['topic_id'] = topic_idx
        lines.append(line)
    return lines

print("It took " + str(time.time() - start) + " seconds to preprocess...")
### Preprocessing End ###

# Train the Initial CorEx topic model with 20 topics (Takes about 3.74s)
NumTopics = 5

print("Training init model...")
start = time.time()

trash_set = tt.topic_tree([], None, np.empty((0, DocWord.shape[1]), int))
InitModel = tt.topic_tree([], None, DocWord)
InitModel.make_children(NumTopics)

print("It took " + str(time.time() - start) + " seconds to train the model...")

print("Init docs...")
start = time.time()

CompleteDocs = init_docs()

print("It took " + str(time.time() - start) + " seconds to init docs...")

print("Init global variables...")
start = time.time()

# state storage for models
#CorexModels = []
# CorexModels.append(InitModel)
CorexCords = []
CorexCords.append(gen_cords(InitModel))
CorexLabels = []
labels = [("Topic " + str(i)) for i in range(1, NumTopics + 1)]
update_topic_keys(labels, InitModel) #store each topic name to corresponding topic_tree leaf class
color_assign(color_category30, InitModel) #store all assigned color in each leaf class

CorexLabels.append(labels)
get_Topic_Keys(InitModel)

# CorexDocs = []

print("It took " + str(time.time() - start) +
      " seconds to init global variables...")

# Print all topics from the CorEx topic model
# def gen_topic_words(corex_model):
#     topic_words = []
#     for n in range(corex_model.n_hidden):
#         words,_ = zip(*corex_model.get_topics(topic=n, n_words=20))
#         topic_words.append(list(words))
#     return topic_words
# End
# --------------Support Function-------------------------------


def translate_topic_word(word_topic, maxWord):
    # get max word index
    indices = np.argpartition(word_topic, -1 * maxWord)[-1 * maxWord:]
    indices = np.flip(indices[np.argsort(word_topic[indices])])
    print(AllWords[indices])

def find_Topic_by_Key(parent, key):
    return parent.find_topic_by_key(key)


    
# --------------Topic Level Operations----------------------------


def MergeT(T1, T2):  # Merge Two Topics
    if T1.parent != T2.parent:
        MoveT(T1, T2.parent)
    InitModel.merge(T1, T2)


def SplitT(T0, num_split):  # Split a topic T0 into child topics
    return T0.make_children(num_split)


def MoveT(T1, T2):  # Move a topic T1 into a new parent T2
    InitModel.recompute(T1, True, word_topic=T1.topic_word)
    InitModel.cut(T1)
    InitModel.insert(T1, T2)
    InitModel.recompute(T2, False)


def RemoveT(T1):  # Remove a topic T1
    InitModel.recompute(T1, True, word_topic=T1.topic_word)
    InitModel.cut(T1)
    InitModel.insert(T1, trash_set)


def FixT(T1):  # make T1 unaffected by recompute
    InitModel.FixT(T1)

# --------------Word Level Operations----------------------------


def addW(Added_word, T1):
    InitModel.recompute(T1, True, word_topic=Added_word)


def ChangeW(Changed_word, T1):
    InitModel.recompute(T1, True, word_topic=Changed_word)


def MoveW(word, T1, T2):
    T1.make_children()
    InitModel.recompute(T1, False, word_topic=word)

# ------------------------------------------------------------------



def get_init_cords(request):
    global InitModel, CorexCords
    response = {}
    response['cords'] = CorexCords[-1]
    return HttpResponse(json.dumps(response), content_type='application/json')


def lemmatize_all(sentence):
    wnl = WordNetLemmatizer()
    for word, tag in pos_tag(word_tokenize(sentence)):
        if tag.startswith("NN"):
            yield wnl.lemmatize(word, pos='n')
        elif tag.startswith('VB'):
            yield wnl.lemmatize(word, pos='v')
        elif tag.startswith('JJ'):
            yield wnl.lemmatize(word, pos='a')
        else:
            yield word


def get_word_topic(all_words, nmf_model, word):
    try:
        cleaned_word = ' '.join(lemmatize_all(word))
        cleaned_word = cleaned_word.strip()
        cleaned_word = gensim.utils.simple_preprocess(
            cleaned_word, deacc=True)[0]
        word_id = all_words.index(cleaned_word)
        return nmf_model.clusters[word_id]
    except:
        return -1



def gen_json(request):
    global CorexCords
    response = {}
    response['cords'] = CorexCords[-1]
    return HttpResponse(json.dumps(response), content_type='application/json')


def index(request): #render out the top words for each topics
    print("Enter TopicLens...")
    start = time.time()

    global InitModel, CorexCords, CorexLabels
    labels = CorexLabels[-1]
    context = {}
    context['docs'] = CompleteDocs
    context['num_docs'] = InitModel.doc_nums
    context['topics'] = []
    print('labels=', labels)
    topic_list = InitModel.get_topics()
    for n in range(InitModel.topic_nums):
        print("check1: ", n)
        item = []
        count, factor = 0, 0
        for word, weight in InitModel.get_top_topics(topic=n, n_words=15, Allword=AllWords):
            print(word, weight)
            if count == 0:
                factor = 120 / weight
            item.append(tuple((word, factor * weight, topic_list[n].getColor() )))
            count += 1
        context['topics'].append(tuple((topic_list[n].getName(), item)))
    context['labels'] = CorexLabels[-1]
    print("It took " + str(time.time() - start) +
          " seconds to enter TopicLens...")
    return render(request, "interface/index.html", context)


def num_topics(request):
    print('num topics')
    global CorexCords, CorexLabels
    response = {}
    context = {}
    num_topics = int(request.POST.get("num_topics"))
    '''
    ct_model_num = ct.Corex(n_hidden=num_topics, words=AllWords,
                            max_iter=MaxIter, verbose=False, seed=RandomSeed)
    ct_model_num.fit(DocWord, words=AllWords)
    CorexModels.append(ct_model_num)
    cords = gen_cords(ct_model_num)
    CorexCords.append(cords)
    labels = [("Topic " + str(i)) for i in range(0, num_topics)]
    CorexLabels.append(labels)
    '''
    context['topics'] = []
    for n in range(InitModel.topic_nums):
        item = []
        count, factor = 0, 0
        for word, weight in InitModel.get_top_topics(topic=n, n_words=20, Allword=AllWords):
            if count == 0:
                factor = 120 / weight
            item.append(tuple((word, factor * weight, color_category30[n])))
            count += 1
        context['topics'].append(tuple((labels[n], item)))
    response['topics-container'] = render_to_string(
        "interface/topics-container.html", context)
    response['cords'] = cords
    response['topics-filters'] = render_to_string(
        "interface/topics-filters.html", context)
    return HttpResponse(json.dumps(response), content_type='application/json')


def merge_topics(request): #not used?
    print('merge topics')
    global CorexModels, CorexCords, CorexLabels
    response = {}
    context = {}
    topic1_id = int(request.POST.get("topic1_id"))
    topic2_id = int(request.POST.get("topic2_id"))

    json_topics = request.POST.get("json_topics")
    _anchor_words = json.loads(json_topics)
    labels = request.POST.getlist('labels[]')

    def merge_labels_helper(idx1, idx2, _labels):
        idx1, idx2 = min(idx1, idx2), max(idx2, idx1)
        print("idx1=", _labels[idx1])
        print("idx2=", _labels[idx2])
        _labels[idx1] = _labels[idx1] + ", " + _labels[idx2]
        print("idx1 - after=", _labels[idx1])
        del _labels[idx2]
        return _labels

    def merge_topics_helper(idx1, idx2, _topic_words):
        idx1, idx2 = min(idx1, idx2), max(idx2, idx1)
        res = []
        for idx, words in enumerate(_topic_words):
            res.append(list(words))
            if(idx == idx2):
                res[idx1] = res[idx2] + res[idx1]
        del res[idx2]
        return res

    labels = merge_labels_helper(topic1_id, topic2_id, labels)
    CorexLabels.append(labels)
    anchor_words_merge = merge_topics_helper(
        topic1_id, topic2_id, _anchor_words)
    ct_model_merge = ct.Corex(n_hidden=len(
        anchor_words_merge), words=AllWords, max_iter=MaxIter, verbose=False, seed=RandomSeed)
    ct_model_merge.fit(DocWord, words=AllWords,
                       anchors=anchor_words_merge, anchor_strength=6)
    CorexModels.append(ct_model_merge)
    cords = gen_cords(ct_model_merge)
    CorexCords.append(cords)
    context['topics'] = []
    for n in range(len(ct_model_merge.get_topics())):
        item = []
        for word, weight in ct_model_merge.get_topics(topic=n, n_words=20):
            item.append(tuple((word, weight * 500, color_category30[n])))
        context['topics'].append(tuple((labels[n], item)))
    response['topics-container'] = render_to_string(
        "interface/topics-container.html", context)
    response['cords'] = cords
    response['topics-filters'] = render_to_string(
        "interface/topics-filters.html", context)
    return HttpResponse(json.dumps(response), content_type='application/json')


def split_topics(request): #not used?
    print('split topics')
    global CorexModels, CorexCords, CorexLabels
    response = {}
    context = {}
    to_split_id = int(request.POST.get("topic_id"))
    num_cluster = int(request.POST.get("num_split"))
    labels = request.POST.getlist('labels[]')
    json_topics = request.POST.get("json_topics")
    anchor_words_split = json.loads(json_topics)

    def distance(word1, word2):
        return WVModel.wv.similarity(word1, word2)

    def buildSimilarityMatrix(samples):
        numOfSamples = len(samples)
        matrix = np.zeros(shape=(numOfSamples, numOfSamples))
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                matrix[i, j] = distance(samples[i], samples[j])
        return matrix

    to_split_words = anchor_words_split[to_split_id]
    sim_mat = buildSimilarityMatrix(to_split_words)
    mat = np.matrix(sim_mat)
    res = SpectralClustering(num_cluster).fit_predict(mat)
    word_set = [[] for _ in range(num_cluster)]
    for i in range(len(to_split_words)):
        idx = res[i]
        word = to_split_words[i]
        word_set[idx].append(word)
    # create new anchor words
    del anchor_words_split[to_split_id]
    newLabel = labels[to_split_id] + " splitted "
    del labels[to_split_id]
    for i in range(num_cluster):
        anchor_words_split.append(word_set[i])
        labels.append(newLabel + str(i))

    ct_model_split = ct.Corex(n_hidden=(len(anchor_words_split)),
                              words=AllWords, max_iter=MaxIter, verbose=False, seed=RandomSeed)
    ct_model_split.fit(DocWord, words=AllWords,
                       anchors=anchor_words_split, anchor_strength=6)
    CorexModels.append(ct_model_split)
    cords = gen_cords(ct_model_split)
    CorexCords.append(cords)
    CorexLabels.append(labels)
    context['topics'] = []
    for n in range(len(ct_model_split.get_topics())):
        item = []
        for word, weight in InitModel.get_top_topics(topic=n, n_words=20, Allword=AllWords):
            
            item.append(tuple((word, weight * 500, color_category30[n])))
        context['topics'].append(tuple((labels[n], item)))
    response['topics-container'] = render_to_string(
        "interface/topics-container.html", context)
    response['cords'] = cords
    response['topics-filters'] = render_to_string(
        "interface/topics-filters.html", context)
    return HttpResponse(json.dumps(response), content_type='application/json')


def split_topics_noupdate(request):
    global CorexLabels, CorexCords
    print('split topics with update')
    response = {}
    context = {}
    num_cluster = int(request.POST.get("num_split"))
    words = labels = request.POST.getlist('words[]')
    topic_key = request.POST.get('origin_label')

    print("words=", words)
    print("num_cluster=", num_cluster)
   
    topic_node = find_Topic_by_Key(InitModel, topic_key)
    child_list = SplitT(topic_node, num_cluster)
    
    for count, child in enumerate(child_list):
        new_Name = topic_node.getName() + " - " + str(count)
        print(new_Name)
        child.setName(new_Name)

    new_Label = InitModel.get_topic_keys()
    CorexLabels.append(new_Label)
    color_assign(color_category30, InitModel)

    #cords = gen_cords(InitModel)
    #CorexCords.append(cords)
    cords = CorexCords[-1]
    #update topic list
    topic_list = InitModel.get_topics()
    context['topics'] = []
    for n in range(InitModel.topic_nums):
        item = []
        count, factor = 0, 0
        for word, weight in InitModel.get_top_topics(topic=n, n_words=15, Allword=AllWords):
            if count == 0:
                factor = 120 / weight
            item.append(tuple((word, factor * weight, topic_list[n].getColor() )))
            count += 1
        context['topics'].append(tuple((topic_list[n].getName(), item)))

    response['topics-container'] = render_to_string(
        "interface/topics-container.html", context)
    response['topics-filters'] = render_to_string(
        "interface/topics-filters.html", context)
    response['cords'] = cords
    
    return HttpResponse(json.dumps(response), content_type='application/json')


def update_topics(request): #will make further changes
    print('update topics')
    global CorexCords, CorexLabels
    response = {}
    context = {}
    labels = request.POST.getlist('labels[]')
    json_topics = request.POST.get("json_topics")
    move_anchor_words = json.loads(json_topics)
    '''
    ct_model_move = ct.Corex(n_hidden=len(
        move_anchor_words), words=AllWords, max_iter=MaxIter, verbose=False, seed=RandomSeed)
    ct_model_move.fit(DocWord, words=AllWords,
                      anchors=move_anchor_words, anchor_strength=6)
    CorexModels.append(ct_model_move)
    '''
    cords = gen_cords(ct_model_move)
    CorexCords.append(cords)
    CorexLabels.append(labels)
    context['topics'] = []
    for n in range(len(ct_model_move.get_topics())):
        item = []
        for word, weight in ct_model_move.get_topics(topic=n, n_words=20):
            item.append(tuple((word, weight * 500, color_category30[n])))
        context['topics'].append(tuple((labels[n], item)))
    response['cords'] = cords
    response['topics-container'] = render_to_string(
        "interface/topics-container.html", context)
    response['topics-filters'] = render_to_string(
        "interface/topics-filters.html", context)
    return HttpResponse(json.dumps(response), content_type='application/json')


def last_state(request):
    print('last state')
    global CorexModels, CorexCords, CorexLabels
    if (len(CorexModels) > 1):
        CorexModels = CorexModels[:-1]
        CorexCords = CorexCords[:-1]
        CorexLabels = CorexLabels[:-1]
    cur_model = CorexModels[-1]
    labels = CorexLabels[-1]

    context = {}
    context['topics'] = []
    for n in range(len(cur_model.get_topics())):
        item = []
        for word, weight in cur_model.get_topics(topic=n, n_words=20):
            item.append(tuple((word, weight * 500, color_category30[n])))
        context['topics'].append(tuple((labels[n], item)))
    response = {}
    response['topics-container'] = render_to_string(
        "interface/topics-container.html", context)
    response['cords'] = CorexCords[-1]
    response['topics-filters'] = render_to_string(
        "interface/topics-filters.html", context)
    return HttpResponse(json.dumps(response), content_type='application/json')


def init_state(request):
    print('init state')
    global CorexModels, CorexCords, CorexLabels
    if (len(CorexModels) > 1):
        CorexModels = CorexModels[:1]
        CorexCords = CorexCords[:1]
        CorexLabels = CorexLabels[:1]
    cur_model = CorexModels[-1]
    labels = CorexLabels[-1]

    context = {}
    context['topics'] = []
    for n in range(len(cur_model.get_topics())):
        item = []
        for word, weight in cur_model.get_topics(topic=n, n_words=20):
            item.append(tuple((word, weight * 500, color_category30[n])))
        context['topics'].append(tuple((labels[n], item)))
    response = {}
    response['topics-container'] = render_to_string(
        "interface/topics-container.html", context)
    response['cords'] = CorexCords[-1]
    response['topics-filters'] = render_to_string(
        "interface/topics-filters.html", context)
    return HttpResponse(json.dumps(response), content_type='application/json')


def get_doc(request):
    print('get_doc')
    global InitModel, CorexCords, CorexLabels
    response = {}
    labels = request.POST.getlist('labels[]')
    doc_idx = int(request.POST.get("doc_idx"))
    doc = CompleteDocs[doc_idx].copy()
    # tokens = re.sub(r'([^\s\w]|_)+', '', doc['body']).split(' ')
    tokens = doc['body'].split(' ')
    html = ""
    for token in tokens:
        topic_id = get_word_topic(AllWords, InitModel, token)
        #topic_id = -1
        if (topic_id == -1):
            html = html + " " + token
            #print("this happens every single time")
        else:
            html = html + " " + "<span title='topic " + \
                str(topic_id) + "' style='background: #" + color_category30[get_word_topic(
                    AllWords, InitModel, token)] + ";'>" + token + "</span>"
    # doc['body'] = " ".join(["<span style='background: #" + color_category30[get_word_topic(AllWords, CorexModels[-1], token)] + ";'>" + token + "</span>" for token in tokens])
    doc['body'] = html
    #topic_weights = InitModel.get_Doc_Topic()[doc_idx]
    #indices = [i for i, x in enumerate(
     #   CorexModels[-1].labels[doc_idx]) if x == True]
    #indices = [InitModel.label()[doc_idx]]
    #indices = [InitModel.label[doc_idx]] #instead of label index, should return topic name and color, maybe objest itself
    #indices = sorted(indices, key=lambda x: topic_weights[x], reverse=True)


    indices_topic = InitModel.find_topic_by_doc_index(doc_idx)
    print(' '.join(x[1].getColor() for x in indices_topic))
    print(' '.join(x[1].getName() for x in indices_topic))
    doc['color_list'] = ' '.join(x[1].getColor() for x in indices_topic)
    doc['label_list'] = '^'.join(x[1].getName() for x in indices_topic)
    #doc['labels'] = labels
    if (Dataset == 'CHO' or Dataset == 'Tax'):
        full_text = doc['full_text']
        index = doc['index']
        texts = full_text.split('\n')
        texts[index] = '<span style="background-color:yellow;">' + \
            texts[index] + '</span>'
        full_text_html = '</p><p>'.join(texts)
        doc['full_text_html'] = '<p>' + full_text_html + '</p>'
    response = doc
    return HttpResponse(json.dumps(response), content_type='application/json')

def get_tree_graph(request):
    print(request.POST.get("a"))
    print(request.POST.get("b"))
    response = {}
    response['testing'] = ["hello", "word", "my friend"]
    return HttpResponse(json.dumps(response), content_type='application/json')