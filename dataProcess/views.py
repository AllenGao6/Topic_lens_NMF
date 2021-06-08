from django.shortcuts import render
from django.http import HttpResponse
import json
from tqdm import tqdm
#data processing
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re
import numpy as np
import pickle
from topiclens.settings import PROJECT_PATH
import os
import time
from sklearn.decomposition import NMF

WorkDir = os.path.join(PROJECT_PATH, 'test/')
#data cleaning methods
stopword = nltk.corpus.stopwords.words('english')
wordnet_lemmatizer = WordNetLemmatizer()

def remove_punctuation(text):
    no_punct=[words for words in text if words not in string.punctuation]
    words_wo_punct=''.join(no_punct)
    return words_wo_punct

def tokenize(text):
    split=re.split("\W+",text) 
    return split

def remove_stopwords(text):
    text=[word for word in text if word not in stopword and word.isnumeric()==False]
    return text

def Lemmatization(text):
    text=[wordnet_lemmatizer.lemmatize(word) for word in text]
    return text


# Create your views here.
def upload(request):
    print('success!')
    return render(request, "dataProcess/upload.html")

def process_data(request):
    print("this is called")
    #recieve data from frontend
    title_list = request.POST.getlist("titles[]")
    content_list = request.POST.getlist("contents[]")
    SIZE = len(title_list)
    #store in complete doc dic
    Complete_doc = {}
    Allword = set() #contains all unique words

    for i in tqdm(range(SIZE)):
        Complete_doc[i] = {'title': title_list[i]}
        Complete_doc[i]['body'] = content_list[i]

    #start to process the data
    #process each document by iterations
    for i in tqdm(range(SIZE)):
        #remove puntuation
        doc_wo_punct = remove_punctuation(content_list[i])
        #tokenization and convert whole string to lower case
        tokenized_doc = tokenize(doc_wo_punct.lower())
        #remove all stop words from tokenized_doc
        cleaned_tokenized_doc = remove_stopwords(tokenized_doc)
        #Lemmatizatize the data
        content_list[i] = Lemmatization(cleaned_tokenized_doc)
        #add new words in collection for later use
        for word in content_list[i]:
            Allword.add(word)
    #All words data ready
    NUM_WORDS = len(Allword)
    Allword_numpy = np.asarray(list(Allword))
    
    print('constructing frequency matrix...')
    DocWord = []
    for doc in tqdm(content_list):
        layer = [0 for _ in range(NUM_WORDS)]
        x = np.array(doc)
        #construct frequency matrix
        unique, counts = np.unique(x, return_counts=True)
        temp_frequency = np.asarray((unique, counts)).T
        for i in temp_frequency:
            index = np.where(Allword_numpy==i[0])[0][0]
            layer[index] = int(i[1])
        DocWord.append(layer)

    print("Constructing pickle files...")

    with open(WorkDir + 'Complete_doc.pickle', 'wb') as handle:
        pickle.dump(Complete_doc, handle, protocol=pickle.HIGHEST_PROTOCOL)
    handle.close()

    with open(WorkDir + 'all_words.pickle','wb') as handle2:
        pickle.dump(Allword_numpy, handle2)
    handle2.close()

    with open(WorkDir + 'doc_word.pickle','wb') as handle3:
        pickle.dump(np.asarray(DocWord), handle3)
    handle3.close()



    response = {}
    return HttpResponse(json.dumps(response), content_type='application/json')
    
def analyze(request):
    #retrieve data from previously uploaded csv file
    AllWords = pickle.load(open(WorkDir + "all_words.pickle", "rb"))
    DocWord = pickle.load(open(WorkDir + "all_words.pickle", "rb"))
    CompleteDocs = pickle.load(open(WorkDir + "Complete_doc.pickle", "rb"))

    NN_matrix =  NMF(n_components=13, init='random', random_state=0)

    doc_list = NN_matrix.fit_transform(DocWord)
    word_to_topic = NN_matrix.components_
    print(doc_list.T.shape)
    print(word_to_topic.shape)

    #train LDA model
    '''from gensim.test.utils import common_texts
    from gensim.corpora.dictionary import Dictionary
    import gensim

    common_dictionary = Dictionary(CompleteDocs)
    common_corpus = [common_dictionary.doc2bow(text) for text in common_texts]

    lda = gensim.models.ldamodel.LdaModel(common_corpus, num_topics=10, alpha='auto', eval_every=5) 
    print('\nPerplexity: ', lda.log_perplexity(corpus)) 
    '''

    from sklearn.cluster import KMeans
    from sklearn.datasets import make_blobs

    from yellowbrick.cluster import KElbowVisualizer

    # Generate synthetic dataset with 8 random clusters

    method = 1
    opt_k = 0

    if method == 1:
        # Instantiate the clustering model and visualizer
        model = KMeans()
        visualizer = KElbowVisualizer(model, k=(4,16))

        visualizer.fit(doc_list)        # Fit the data to the visualizer
        visualizer.show()        # Finalize and render the figure
        opt_k = visualizer.elbow_value_
    else:
        model = KMeans()
        visualizer = KElbowVisualizer(
            model, k=(4,12), metric='calinski_harabasz', timings=False
        )

        visualizer.fit(doc_list)        # Fit the data to the visualizer
        visualizer.show()        # Finalize and render the figure
        opt_k = visualizer.elbow_value_

    from sklearn.mixture import GaussianMixture

    gm = GaussianMixture(n_components=opt_k, random_state=0).fit(doc_list)
    print("training GMM...")
    print(gm.means_)
    time.sleep(2)
    response = {}
    return HttpResponse(json.dumps(response), content_type='application/json')