import numpy as np
'''
    X : the m by n word matrix, m document and n word
    doc_to_topic: an m by n matrix, with m documents and n topics
    word_to_topic: an m by n matrix, wiht m topics and n words


'''


class NMF:

    def __init__(self, topic_nums, max_iter=200, eps=1e-5, seed=None, update_rule="additive", topic_index=None):
        self.max_iter = max_iter
        self.eps = eps
        self.topic_nums = topic_nums
        self.update_rule = update_rule
        self.topic_index = topic_index
        np.random.seed(seed)

    def fit(self, X, word_topic=None, doc_topic=None):
        # print(X[0])
        self.fit_transform(X, word_topic, doc_topic)
        return self

    def fit_transform(self, X, word_topic, doc_topic):
        self.pre_process(X)
        self.initialize_parameters(X, word_topic, doc_topic)
        cost_function = self.check_converge(X, word_topic, doc_topic)
        for trial in range(self.max_iter):  # run though interations to converge
            self.fit_doc_to_topic(X, doc_topic)
            self.fit_word_to_topic(X, word_topic)
            current_improvement = np.abs(
                cost_function - self.check_converge(X, word_topic, doc_topic))
            #print(current_improvement)
            if current_improvement <= self.eps:
                print("Converge after ", trial, "interations with ",
                      self.update_rule, " update rule")
                break
            cost_function = self.check_converge(X, word_topic, doc_topic)
        else:
            print("max interations reached, current converge index: ",
                  self.check_converge(X, word_topic, doc_topic), "with ", self.update_rule, " update rule")

    def fit_doc_to_topic(self, X, doc_topic):
        '''
            X = WH fix H and update W
        '''
        W = self.doc_to_topic
        H = self.word_to_topic
        if type(doc_topic) != np.ndarray:
            if self.update_rule == "multiplcate":
                self.doc_to_topic = W * ((X.dot(H.T)) / (W.dot(H).dot(H.T)))
            elif self.update_rule == "additive":
                self.doc_to_topic += (W/(W.dot(H).dot(H.T))) * (X.dot(H.T) - W.dot(H).dot(H.T))
                #(W.T.dot(X) - W.T.dot(W).dot(H))
            else:
                print("error: updaterule incorrect")
        else:
            print("not yet implemented")

    def fit_word_to_topic(self, X, word_topic):
        '''
            X = WH fix W and update H
        '''
        W = self.doc_to_topic  # (1839, 2)
        H = self.word_to_topic  # (2, 7329)
        control_factor = np.average(self.word_to_topic)
        if type(word_topic) != np.ndarray:
            if self.update_rule == "multiplcate":
                self.word_to_topic = H * ((W.T.dot(X)) / (W.T.dot(W).dot(H)))
            elif self.update_rule == "additive":
               
                self.word_to_topic += np.nan_to_num(H/(W.T.dot(W).dot(H))) * (W.T.dot(X) - W.T.dot(W).dot(H))

            else:
                print("error: updaterule incorrect")
        else:
            
            self.word_to_topic += np.nan_to_num(H/(W.T.dot(W).dot(H))) * (W.T.dot(X) - W.T.dot(W).dot(H)) - 0.01 * control_factor * self.mask_matrix * (H - self.word_topic_bias)

    def check_converge(self, X, word_topic, doc_topic):
        if type(word_topic) == np.ndarray and type(doc_topic) == np.ndarray:
            index = 0
        elif type(word_topic) == np.ndarray:
            index = np.linalg.norm(X - self.doc_to_topic.dot(self.word_to_topic)) + np.linalg.norm(
                self.mask_matrix * (self.word_to_topic - self.word_topic_bias))
        elif type(doc_topic) == np.ndarray:
            index = 0
        else:
            index = np.linalg.norm(
                X - self.doc_to_topic.dot(self.word_to_topic))
        print(index)
        return index

    def pre_process(self, X):
        '''
            binarize the data set
        '''
        if X.max() > 1:
            print("this is activated")
            X = (X > 1)

    def initialize_parameters(self, X, word_topic, doc_topic):
        '''
            random initialize doc_to_topic and word_to_topic, where X = doc_to_topic * word_to_topic
        '''
        self.sample, self.visibleWord = X.shape
        self.doc_to_topic = np.random.random((self.sample, self.topic_nums))
        self.word_to_topic = np.random.random(
            (self.topic_nums, self.visibleWord))
        if type(word_topic) == np.ndarray:
            self.mask_matrix = np.zeros((self.topic_nums, X.shape[1]))
            self.mask_matrix[self.topic_index] = [1] * X.shape[1]
            self.word_topic_bias = np.zeros((self.topic_nums, X.shape[1]))
            self.word_topic_bias[self.topic_index] = word_topic.reshape(
                1, X.shape[1])
        if type(doc_topic) == np.ndarray:
            print("not implemented yet")
