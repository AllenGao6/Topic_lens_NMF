import pickle
import numpy as np
from sklearn.decomposition import NMF

#require data
AllWords = np.array(pickle.load(open("all_words.pickle", "rb")))
DocWord = pickle.load(open("doc_word.pickle", "rb")).toarray()
CompleteDocs = pickle.load(open("complete_secs.pickle", "rb"))

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
