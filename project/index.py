import os
import sys
from nltk.tokenize import sent_tokenize
from string import punctuation
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import pos_tag
import time
from collections import defaultdict
import nltk


# download package
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)

time_start = time.time()
path = sys.argv[1]
target = sys.argv[2]
if not os.path.exists(target):
    os.mkdir(target)

wnl = WordNetLemmatizer()
####################
# preprocessing functions
####################
def get_sentences(string):
    result = []
    raw = sent_tokenize(string)
    for temp in raw:
        if not temp[0].isupper() and not temp[0] == "\"":
            if len(result) == 0:
                result.append(temp)
            else:
                result[-1] += f" {temp}"
        else:
            result.append(temp)

    return result

# this function referred from web
def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def remove_start_end_dash(string):
    if string[0] == "\'":
        if string[-1] == "\'":
            string = string[1:-1]
        else:
            string = string[1:]
    elif string[-1] == "\'":
        string = string[:-1]

    return string


def word_with_dash(string):
    temp = string.split("\'")
    left, right = temp[0], temp[1]
    tag = pos_tag([left])[0][1]
    if tag.startswith("C"):
        string = right
    elif tag.startswith("N"):
        if left not in ['i', 'don', 'won', 'doesn', 'didn', 'couldn', 'shouldn', 'haven'] and len(left) != 1:
            string = left
        else:
            string = string.replace("\'", " ")
    else:
        string = string.replace("\'", " ")
    return string


def lemma_sent(word_list):
    tagged_sent = pos_tag(word_list)
    lemmas_sent = []
    for tag in tagged_sent:
        wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
        lemmas_sent.append(wnl.lemmatize(tag[0], pos=wordnet_pos))
    return lemmas_sent

def make_string(index):
    result = ""
    for i in range(len(index)):
        doc_info = index[i]
        doc_num = str(doc_info[0])
        pos_list = " ".join([str(i) for i in doc_info[1]])
        sent_list = " ".join([str(i) for i in doc_info[2]])
        temp = f"{doc_num},{pos_list},{sent_list}"
        if i != len(index) - 1:
            temp += "|"
        result += temp
    return result


########################
# main procedure
########################
doc_num = 0
token_num = 0
term_num = 0
check = 0
index_dic = defaultdict(list)

for dirpath, dirnames, filenames in os.walk(path):
    file_names = sorted([int(file) for file in filenames])
    for file in file_names:
        file_path = path+"/"+str(file)
        doc_num += 1
        #print(file)
        with open(file_path, "r", encoding="utf-8") as inputFile:
            ################
            # preprocessing
            ################
            text = ""
            tmp = []
            for line in inputFile:
                line = line.strip()
                if line != "":
                    tmp.append(line)
            # get the file as a whole str
            text = " ".join(tmp)
            # divide text file to sentences
            sentences = get_sentences(text)
            # dealing with every sentence
            for i in range(len(sentences)):
                # make lower & replace '.'
                sent = sentences[i].lower().replace('.', '')
                for item in punctuation:
                    if item != "'":
                        sent = sent.replace(item, ' ')
                # remove duplicate space
                words = list(filter(lambda x: not str(x).isdigit(), sent.split()))
                # # dealing with word with '
                for j in range(len(words)):
                    word = words[j]
                    if "\'" in word:
                        word = remove_start_end_dash(word)
                        if "\'" in word:
                            word = word_with_dash(word)
                            # print(word)
                    words[j] = word

                sent = " ".join(words)
                # make word lemmatization
                sentences[i] = lemma_sent(sent.split())
            #######################
            # producing index
            #######################
            pos = 0
            cur_doc_dic = {}
            for i in range(len(sentences)):
                sent_start_pos = pos
                sentence = sentences[i]
                for word in sentence:
                    token_num += 1
                    if word not in cur_doc_dic:
                        cur_doc_dic[word] = [[pos], {sent_start_pos}]
                    else:
                        tmp = cur_doc_dic[word]
                        tmp[0].append(pos)
                        tmp[1].add(sent_start_pos)
                        cur_doc_dic[word] = tmp
                    pos += 1
            for word, info in cur_doc_dic.items():
                index_dic[word].append([file, info[0], sorted(list(info[1]))])


target_file = "result"
target_path = target + "/" + target_file

with open(target_path, "w") as OutputFile:
    for key, value in index_dic.items():
        line = f"{key}-{make_string(value)}\n"
        OutputFile.write(line)


print(f"Total number of documents: {doc_num}")
print(f"Total number of tokens: {token_num}")
print(f"Total number of terms: {len(index_dic)}")

time_end = time.time()
time_sum = time_end - time_start
print(time_sum)

