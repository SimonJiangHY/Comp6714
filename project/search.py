import sys
import re
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

index = sys.argv[1]
index_file = index + "/result"
wnl = WordNetLemmatizer()

#####################
# get index info
#####################
term_dic = {}
with open(index_file, "r") as inputFile:
    for line in inputFile:
        line = line[:-1]
        term_index = line.split("-")
        term, index = term_index[0], term_index[1]
        doc_list = index.split("|")
        index_list = []
        for doc_info in doc_list:
            temp = doc_info.split(",")
            doc_id = int(temp[0])
            cur_pos_list = [int(i) for i in temp[1].split(" ")]
            cur_sent_list = [int(i) for i in temp[2].split(" ")]
            index_list.append([doc_id, cur_pos_list, cur_sent_list])
        term_dic[term] = index_list


#####################
# query preprocessing
#####################
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


def lemma_sent(word_list):
    tagged_sent = pos_tag(word_list)
    lemmas_sent = []
    for tag in tagged_sent:
        wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
        lemmas_sent.append(wnl.lemmatize(tag[0], pos=wordnet_pos))
    return lemmas_sent


#####################
# single operations
#####################
def get_term_info(string):
    result = []
    if string in term_dic:
        result = term_dic[string]
    return result


# space -> OR
def space(p1, p2):
    result = []
    max_1, max_2, i, j = len(p1), len(p2), 0, 0
    while i < max_1 and j < max_2:
        if p1[i][0] == p2[j][0]:
            tmp = [p1[i][0], sorted(list(set(p1[i][1] + p2[j][1]))), sorted(list(set(p1[i][2] + p2[j][2])))]
            result.append(tmp)
            i += 1
            j += 1
        elif p1[i][0] < p2[j][0]:
            result.append(p1[i])
            i += 1
        else:
            result.append(p2[j])
            j += 1

    if i == max_1:
        cur_max = result[-1][0]
        for item in p2:
            if item[0] > cur_max:
                result.append(item)
    elif j == max_2:
        cur_max = result[-1][0]
        for item in p1:
            if item[0] > cur_max:
                result.append(item)

    return result


# & -> AND
def ampersand(p1, p2):
    result = []
    max_1, max_2, i, j = len(p1), len(p2), 0, 0
    while i < max_1 and j < max_2:
        if p1[i][0] == p2[j][0]:
            tmp = [p1[i][0], sorted(list(set(p1[i][1] + p2[j][1]))), sorted(list(set(p1[i][2]+p2[j][2])))]
            result.append(tmp)
            i += 1
            j += 1
        elif p1[i][0] < p2[j][0]:
            i += 1
        else:
            j += 1

    return result


# A +n B
def plus_n(p1, p2, num):
    result = []
    max_1, max_2, i, j = len(p1), len(p2), 0, 0
    while i < max_1 and j < max_2:
        if p1[i][0] == p2[j][0]:
            ##############
            all_sent = sorted(list(set(p1[i][2] + p2[j][2]))) + [9999999999999]
            sent_list = set()
            pos_list = set()
            check = []
            pos_list_1, pos_list_2 = p1[i][1], p2[j][1]
            max_pos_2, n = len(pos_list_2), 0
            while n < max_pos_2:
                for pos_1 in pos_list_1:
                    if 0 < pos_list_2[n] - pos_1 <= num:
                        check.append(1)
                        pos_list.add(pos_list_2[n])
                        pos_list.add(pos_1)
                    elif pos_list_2[n] < pos_1:
                        break
                n += 1
            pos_list = sorted(list(pos_list))
            if len(check) != 0:
                for k in range(len(all_sent)-1):
                    sent_start = all_sent[k]
                    sent_end = all_sent[k+1]
                    for pos in pos_list:
                        if sent_start <= pos < sent_end:
                            sent_list.add(sent_start)
                            break
                sent_list = sorted(list(sent_list))
                tmp = [p1[i][0], pos_list, sent_list]
                result.append(tmp)
            ##############
            i += 1
            j += 1
        elif p1[i][0] < p2[j][0]:
            i += 1
        else:
            j += 1

    return result


# A /n B
def virgule_n(p1, p2, num):
    result = []
    max_1, max_2, i, j = len(p1), len(p2), 0, 0
    while i < max_1 and j < max_2:
        if p1[i][0] == p2[j][0]:
            ##############
            all_sent = sorted(list(set(p1[i][2] + p2[j][2]))) + [9999999999999]
            sent_list = set()
            pos_list = set()
            check = []
            pos_list_1, pos_list_2 = p1[i][1], p2[j][1]
            max_pos_1, m = len(pos_list_1), 0
            while m < max_pos_1:
                for pos_2 in pos_list_2:
                    if abs(pos_list_1[m]-pos_2) <= num:
                        check.append(1)
                        pos_list.add(pos_list_1[m])
                        pos_list.add(pos_2)
                    elif pos_2 - pos_list_1[m] > num:
                        break
                m += 1
            pos_list = sorted(list(pos_list))
            if len(check) != 0:
                for k in range(len(all_sent)-1):
                    sent_start = all_sent[k]
                    sent_end = all_sent[k+1]
                    for pos in pos_list:
                        if sent_start <= pos < sent_end:
                            sent_list.add(sent_start)
                            break
                sent_list = sorted(list(sent_list))
                tmp = [p1[i][0], pos_list, sent_list]
                result.append(tmp)
            ##############
            i += 1
            j += 1
        elif p1[i][0] < p2[j][0]:
            i += 1
        else:
            j += 1

    return result


# A +s B
def plus_s(p1, p2):
    result = []
    max_1, max_2, i, j = len(p1), len(p2), 0, 0
    while i < max_1 and j < max_2:
        if p1[i][0] == p2[j][0]:
            # check if in same sentence
            ##############
            sent_pos_1, sent_pos_2 = p1[i][2], p2[j][2]
            pos_list_1, pos_list_2 = p1[i][1], p2[j][1]
            same_sent = []
            for k in range(len(sent_pos_1)):
                if sent_pos_1[k] in sent_pos_2:
                    if k != len(sent_pos_1) - 1:
                        same_sent.append([sent_pos_1[k], sent_pos_1[k+1]])
                    else:
                        for m in range(len(sent_pos_2)):
                            if sent_pos_2[m] == sent_pos_1[k]:
                                if m != len(sent_pos_2) - 1:
                                    same_sent.append([sent_pos_2[m], sent_pos_2[m+1]])
                                else:
                                    same_sent.append([sent_pos_1[k], 9999999999999])
            sent_list = set()
            pos_list = set()
            if len(same_sent) > 0:
                for sent_start, sent_end in same_sent:
                    for p2_pos in pos_list_2:
                        if sent_end > p2_pos > sent_start:
                            for p1_pos in pos_list_1:
                                if sent_start <= p1_pos < p2_pos:
                                    pos_list.add(p1_pos)
                                    pos_list.add(p2_pos)
                                    sent_list.add(sent_start)
            sent_list = sorted(list(sent_list))
            pos_list = sorted(list(pos_list))
            if len(sent_list) > 0:
                tmp = [p1[i][0], pos_list, sent_list]
                result.append(tmp)
            ##############
            i += 1
            j += 1
        elif p1[i][0] < p2[j][0]:
            i += 1
        else:
            j += 1

    return result


# A /s B
def virgule_s(p1, p2):
    result = []
    max_1, max_2, i, j = len(p1), len(p2), 0, 0
    while i < max_1 and j < max_2:
        if p1[i][0] == p2[j][0]:
            # check if in same sentence
            ##############
            all_sent = sorted(list(set(p1[i][2] + p2[j][2]))) + [9999999999999]
            sent_pos_1, sent_pos_2 = p1[i][2], p2[j][2]
            same_sent = [item for item in sent_pos_1 if item in sent_pos_2]
            sent_range = []
            pos_list = set()
            if len(same_sent) > 0:
                for k in range(len(all_sent)):
                    if all_sent[k] in same_sent:
                        sent_range.append([all_sent[k], all_sent[k+1]])
                for pos in p1[i][1]:
                    for left, right in sent_range:
                        if left <= pos < right:
                            pos_list.add(pos)
                            break
                for pos in p2[j][1]:
                    for left, right in sent_range:
                        if left <= pos < right:
                            pos_list.add(pos)
                            break
                pos_list = sorted(list(pos_list))
                tmp = [p1[i][0], pos_list, same_sent]
                result.append(tmp)
            ##############
            i += 1
            j += 1
        elif p1[i][0] < p2[j][0]:
            i += 1
        else:
            j += 1

    return result


# "A B C"
def double_quot(string):
    words = string[1:-1].split()
    # do lemma
    words = lemma_sent(words)
    # do And
    result = []
    tmp = get_term_info(words[0])
    for i in range(1, len(words)):
        tmp = plus_n(tmp, get_term_info(words[i]), 1)
    for doc in tmp:
        doc_pos, doc_sent = doc[1], doc[2]
        for i in range(len(doc_pos)-len(words)+1):
            check = True
            cur_pos = doc_pos[i]
            for m in range(1, len(words)):
                if doc_pos[i+m] != cur_pos + m:
                    check = False
                    break
            if check:
                for j in range(len(doc_sent)):
                    left = doc_sent[j]
                    if j != len(doc_sent) - 1:
                        right = doc_sent[j+1]
                    else:
                        right = 99999999999
                    if doc_pos[i] >= left and doc_pos[i-1+len(words)] < right:
                        result.append(doc)
                        break
                break
    return result


#####################
# dealing with parser
#####################
def do_calculation(left, symbol, right):
    result = []
    # space
    if re.fullmatch("#", symbol):
        result = space(left,right)
    # +n
    elif re.fullmatch("\+[0-9]+", symbol):
        number = int(symbol[1:])
        result = plus_n(left, right, number)
    # /n
    elif re.fullmatch("/[0-9]+", symbol):
        number = int(symbol[1:])
        result = virgule_n(left, right, number)
    # +s
    elif re.fullmatch("\+s", symbol):
        result = plus_s(left, right)
    # /s
    elif re.fullmatch("/s", symbol):
        result = virgule_s(left, right)
    # &
    elif re.fullmatch("&", symbol):
        result = ampersand(left, right)
    return result


def make_query_list(string):
    result = []
    check = string.split()
    check_range = len(check)
    i = 0
    while i < check_range:
        cur = check[i]
        if "/" not in cur and "+" not in cur and "&" not in cur:
            if "(" in cur:
                left = cur[0]
                result.append(left)
                cur = cur[1:]
                if "\"" in cur:
                    tmp = cur
                    i += 1
                    while "\"" not in check[i]:
                        tmp += f" {check[i]}"
                        i += 1
                    tmp += f" {check[i]}"
                    result.append(tmp)
                else:
                    result.append(cur)
            elif ")" in cur:
                right = cur[-1]
                cur = cur[:-1]
                result.append(cur)
                result.append(right)
            else:
                if "\"" in cur:
                    tmp = cur
                    i += 1
                    while "\"" not in check[i]:
                        tmp += f" {check[i]}"
                        i += 1
                    tmp += f" {check[i]}"
                    if ")" in tmp:
                        right = tmp[-1]
                        tmp = tmp[:-1]
                        result.append(tmp)
                        result.append(right)
                    else:
                        result.append(tmp)
                else:
                    result.append(cur)
            if i != len(check)-1:
                next = check[i+1]
                if "/" not in next and "+" not in next and "&" not in next:
                    result.append("#")
        else:
            result.append(cur)
        i += 1
    return result


def make_data_list(q_list):
    result = []
    for item in q_list:
        if "/" not in item and "+" not in item and "&" not in item \
                           and "(" not in item and ")" not in item and "#" not in item:
            if "\"" in item:
                result.append(double_quot(item))
            else:
                result.append(get_term_info(lemma_sent([item.lower()])[0]))
        else:
            result.append(item)
    return result


order_list = ["#", "\+[0-9]+", "/[0-9]+", "\+s", "/s", "&"]
def no_bracket(d_list):
    # base case
    if len(d_list) == 1:
        return d_list[0]
    # recurrence
    target_symbol = ""
    target_pos = -1
    for symbol in order_list:
        for i in range(len(d_list)):
            if not isinstance(d_list[i], list):
                if re.fullmatch(symbol, d_list[i]):
                    target_symbol = d_list[i]
                    target_pos = i
                    break
        if target_symbol != "":
            break
    left_list = d_list[target_pos - 1]
    right_list = d_list[target_pos + 1]
    # do calculation
    res = do_calculation(left_list, target_symbol, right_list)
    new_d_list = []
    for i in range(len(d_list)):
        if i == target_pos:
            new_d_list.append(res)
        elif i != target_pos - 1 and i != target_pos + 1:
            new_d_list.append(d_list[i])
    return no_bracket(new_d_list)


def query_parser(d_list):
    # base case
    if len(d_list) == 1:
        return d_list[0]
    # recurrence
    left = -1
    right = -1
    for i in range(len(d_list)):
        if d_list[i] == "(":
            left = i
        if d_list[i] == ")":
            right = i
            break
    no_bracket_list = []
    for i in range(left + 1, right):
        no_bracket_list.append(d_list[i])
    sub_result = no_bracket(no_bracket_list)
    new_d_list = []
    for i in range(len(d_list)):
        if i == left:
            new_d_list.append(sub_result)
        elif i < left or i > right:
            new_d_list.append(d_list[i])
    return query_parser(new_d_list)


####################
# main procedure
####################
while True:
    try:
        query = input()
        query_list = make_query_list(query)
        data_list = ["("] + make_data_list(query_list) + [")"]
        doc_result = query_parser(data_list)
        for i in doc_result:
            print(i[0])
    except EOFError:
        exit(1)

