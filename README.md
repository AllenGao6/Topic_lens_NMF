# Topic_lens Tool

Follow the instruction in conda documentation: https://docs.conda.io/projects/conda/en/4.6.0/user-guide/install/macos.html
install conda on your system

open your terminal

change directory to the project folder (EX. cd /Topic_lens)

run: conda create --name Topic_lens --file pkgs.txt

      conda activate Topic_lens

      python manage.py runserver

the main tool page will be at localhost:8000/interface


To change data set,

create the corresponding pickle file and replace all_words.pickle, doc_word.pickle, and complete_secs.pickle.

all_words.pickle: an array of all whole vocabulary

doc_word.pickle: matrix with doc_word with each word represend as index w.r.t all_words.pickle

complete_secs.pickle: array contains the whole corpus of data
