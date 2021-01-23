import numpy as np
from . import NMF as nmf


class topic_tree:

    def __init__(self, child, parent, X, topic_word=None, doc_topic=None, fixed=False, name=None, doc_label = []):
        self.child = []
        self.parent = parent
        self.X = X
        self.fixed = fixed
        self.topic_word = topic_word
        self.doc_topic = doc_topic
        self.name = name
        self.color = None
        if len(doc_label) == 0: #the identifier for each document
            self.doc_label = np.array([i for i in range(self.X.shape[0])])
        else:
            self.doc_label = doc_label


    @property
    def topic_nums(self):
        return len(self.get_topics())

    @property
    def doc_nums(self):
        return self.X.shape[0]

    def setColor(self, color):
        self.color = color

    def getColor(self):
        return self.color

    def assign_topic_color(self, color_array):
        for count, topic in enumerate(self.get_topics()):
            topic.setColor(color_array[count])
        print("Color assignment complete")
        
    def find_topic_by_doc_index(self, doc_index):#return topic_id and topic_object itself
        topic_return = []
        for count, topic in enumerate(self.get_topics()):
            if topic.contain_doc(doc_index):
                print(topic.name)
                topic_return.append([count, topic])
        return topic_return

    def contain_doc(self, doc_index): #check if a doc in this topic set
        if doc_index in self.doc_label:
            return True
        else:
            return False

    def make_childrens(self):  # split a node into two or its children node
        NN_matrix = nmf.NMF(2)
        NN_matrix.fit(self.X)

        doc_topic = NN_matrix.doc_to_topic
        word_topic = NN_matrix.word_to_topic
        comparator = (doc_topic[:, 0] < doc_topic[:, 1])*1
        X1_index = np.where(comparator == 0)[0]  # find all indices of child1
        X2_index = np.where(comparator == 1)[0]  # find all indices of child2
        # get all the document list

        X1 = self.X[X1_index]
        X2 = self.X[X2_index]

        child1 = topic_tree(
            [], self, X1, topic_word=word_topic[0, :], doc_topic=doc_topic[:, 0])
        child2 = topic_tree(
            [], self, X2, topic_word=word_topic[1, :], doc_topic=doc_topic[:, 1])
        self.child.append(child1)
        self.child.append(child2)

        return [child1, child2]

    def make_children(self, child_num):
        NN_matrix = nmf.NMF(child_num)
        NN_matrix.fit(self.X)

        doc_list = NN_matrix.doc_to_topic
        ind = np.argpartition(doc_list, -1, axis=1)[:, doc_list.shape[1]-1]
        for child_num in range(child_num):
            child_topic = topic_tree([], self, self.X[np.where(ind == child_num)[0]], 
                        topic_word=NN_matrix.word_to_topic[child_num], doc_topic=NN_matrix.doc_to_topic[:, child_num], doc_label=self.doc_label[np.where(ind == child_num)[0]])
            self.child.append(child_topic)
        return self.child

    def merge(self, T1, T2):
        parent_node = T2.parent
        parent_node.child.remove(T2)  # cut connection from parent node to T2
        new_topic = topic_tree(T2.child, parent_node,
                               T2.X, topic_word=T2.topic_word, doc_topic=T2.doc_topic)
        parent_node.child.append(new_topic)
        new_topic.child.append(T2)
        T2.parent = new_topic

        return new_topic
        # parent_node.X = np.concatenate((T1.X, T2.X), axis=0)

    def insert(self, T1, T2):  # insert T1 under T2
        T2.child.append(T1)
        T2.X = np.concatenate((T1.X, T2.X), axis=0)
        current = T2.parent
        while current != None:
            current.X = np.concatenate((T1.X, current.X), axis=0)
            current = current.parent

    def cut(self, T1):  # remove topic 1 from its ancestors
        current = T1.parent
        T1.parent = None
        # remove T1 from its parent node
        current.child.remove(T1)
        current.X = np.empty((0, self.X.shape[1]), int)
        for child in current.child:
            current.X = np.concatenate((child.X, current.X), axis=0)
        # if len(current.child) == 1:
        #    current.child = []
        # change the document set of every parent node except the top node
        while current.parent != None:
            current = current.parent
            current.X = np.empty((0, self.X.shape[1]), int)
            for child in current.child:
                current.X = np.concatenate((child.X, current.X), axis=0)

    def recompute(self, T, parent_check, word_topic=None, doc_topic=None):
        if parent_check:
            target_node = T.parent
            NN_matrix = nmf.NMF(len(target_node.child),
                                topic_index=target_node.child.index(T), eps=1e-3)
        else:
            target_node = T
            NN_matrix = nmf.NMF(len(target_node.child))

        if type(word_topic) == np.ndarray:
            NN_matrix.fit(target_node.X, word_topic=word_topic)
        elif type(doc_topic) == np.ndarray:
            NN_matrix.fit(target_node.X, doc_topic=doc_topic)
        else:
            NN_matrix.fit(target_node.X)

        # go through each doc to topic matrix, m by k
        # update data in each child node
        doc_list = NN_matrix.doc_to_topic
        ind = np.argpartition(doc_list, -1, axis=1)[:, doc_list.shape[1]-1]
        for child_num in range(NN_matrix.topic_nums):
            child_node = target_node.child[child_num]  # initialize child node

            # find all index under this child topic
            child_node.X = target_node.X[np.where(ind == child_num)[0]]
            child_node.topic_word = NN_matrix.word_to_topic[child_num]
            child_node.doc_topic = NN_matrix.doc_to_topic[:, child_num]

        return target_node.child

    def FixT(self, T):
        T.fixed = True

    def get_topics(self):  # return the total number of leaf topics
        array = []
        self.get_get_topic_helper(array)
        return array

    def get_get_topic_helper(self, array):
        if len(self.child) == 0:
            array.append(self)
        for i in self.child:
            i.get_get_topic_helper(array)
        return array

    def get_Word_Topic(self):  # return a m by 2 2d array, m topics and n words
        leaf_list = self.get_topics()
        Topic_Word = np.empty((0, self.X.shape[1]), float)
        for i in leaf_list:
            Topic_Word = np.append(
                Topic_Word, i.topic_word.reshape(1, self.X.shape[1]), axis=0)
        return Topic_Word

    def get_Doc_Topic(self):  # return a m by 2 2d array, m docs and n topics
        leaf_list = self.child
        Doc_Topic = np.empty((self.X.shape[0], 0), float)
        for i in leaf_list:
            Doc_Topic = np.concatenate(
                (Doc_Topic, i.doc_topic.reshape(1, self.X.shape[0]).T), axis=1)
        return Doc_Topic

    @property
    def clusters(self):
        """Return cluster labels for variables"""
        return np.argmax(self.get_Word_Topic(), axis=0)


    # return a list of tuple (word, weight)
    def get_top_topics(self, topic=None, n_words=20, Allword=None):
        tuple_list = []
        word_topic = self.get_Word_Topic()[topic]
        indices = np.argpartition(word_topic, -1 * n_words)[-1 * n_words:]
        indices = np.flip(indices[np.argsort(word_topic[indices])])
        words = Allword[indices]
        for i in range(len(words)):
            tuple_list.append((words[i], word_topic[indices[i]] ))
        return tuple_list

    def setName(self, new_name):
        self.name = new_name

    def getName(self):
        return self.name

    def update_topic_keys(self, topics):
        for count, topic in enumerate(self.get_topics()):
            topic.setName(topics[count])
        print("Topic Update Complete!")

    def get_topic_keys(self):
        print("this is reached")
        topic_list = []
        for count, topic in enumerate(self.get_topics()):
            topic_list.append(topic.getName())
            print(str(count) + " : " + topic.getName())
        return topic_list

    def find_topic_by_key(self, key):
        for topic in self.get_topics():
            if topic.getName() == key:
                return topic
        return None



            
