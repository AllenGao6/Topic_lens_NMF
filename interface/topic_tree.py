import numpy as np
from . import NMF as nmf
from sklearn.decomposition import NMF
import random


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
        self.color_category30 = [
        "d3fe14",  "1da49c", "ccf6e9", "a54509", "7d5bf0", "d08f5d", "fec24c",  "0d906b", "7a9293", "7ed8fe",
        "d9a742",  "c7ecf9",  "72805e", "dccc69",  "86757e", "a0acd2",  "fecd0f",  "4a9bda", "bdb363",  "b1485d",
        "b98b91",  "86df9c",  "6e6089", "826cae", "4b8d5f", "8193e5",  "b39da2", "5bfce4", "df4280", "a2aca6", "ffffff"]
        self.doc_relevance = {}
        for i in range(self.X.shape[0]):
            self.doc_relevance[self.doc_label[i]] = 0
        


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

    def get_doc_relevance(self, index):
        return self.doc_relevance[index]

    def set_doc_relevance(self, index, rele_index):
        self.doc_relevance[index] = rele_index

    def rand_color(self):
        '''
            generate random color code for topics
        '''
        random_number = random.randint(0,16777215)
        hex_number = str(hex(random_number))[2:]
        return hex_number

    def assign_topic_color(self):
        for count, topic in enumerate(self.get_all_topics()):
            topic.setColor(self.color_category30[count])
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
        #NN_matrix = nmf.NMF(child_num)
        #NN_matrix.fit(self.X)
        print("Calculating NMF ....")
        NN_matrix =  NMF(n_components=child_num, init='random', random_state=0)
        doc_list = NN_matrix.fit_transform(self.X)
        word_to_topic = NN_matrix.components_
        #doc_list = NN_matrix.doc_to_topic
        #np.savetxt('test1.txt', doc_list, delimiter=',') 
        #print("Error Index: " + np.linalg.norm(self.X - doc_list.dot(word_to_topic)))
        ind = np.argpartition(doc_list, -1, axis=1)[:, doc_list.shape[1]-1]
        #np.savetxt('test2.txt', ind, delimiter=',')'''
        
        #determine the distribution of document 
        for child_num in range(child_num):
            child_topic = topic_tree([], self, self.X[np.where(ind == child_num)[0]], 
                        topic_word=word_to_topic[child_num], doc_topic=doc_list[:, child_num], doc_label=self.doc_label[np.where(ind == child_num)[0]])
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
        self.get_topic_helper(array)
        return array

    def get_topic_helper(self, array):
        if len(self.child) == 0:
            array.append(self)
        for i in self.child:
            i.get_topic_helper(array)
        return array
    
    def get_all_topic_name(self):
        return [topic.name for topic in self.get_all_topics()]


    def get_all_topics(self):
        array = []
        self.get_all_topic_helper(array)
        return array

    def get_all_topic_helper(self, array):
        array.append(self)
        for i in self.child:
            i.get_all_topic_helper(array)
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
    def get_top_topics(self, topic=None, n_words=20, Allword=None, return_indice=False):
        tuple_list = []
        word_topic = topic.topic_word
        indices = np.argpartition(word_topic, -1 * n_words)[-1 * n_words:]
        indices = np.flip(indices[np.argsort(word_topic[indices])])
        if return_indice:
            print("checkkk")
            return list(indices)
        else:
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
        for count, topic in enumerate(self.get_all_topics()):
            topic_list.append(topic.getName())
            print(str(count) + " : " + topic.getName())
        return topic_list

    def find_topic_by_key(self, key):
        for topic in self.get_all_topics():
            print(topic.getName())
            if topic.getName() == key:
                return topic
        return None



            
