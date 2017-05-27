class WordDataset:
    def __init__(self):
        self.wordSet = {}
        self.synonyms = {}
        self.gram = 0

    def addSynonyms(self,synList):
        if synList[0] in self.wordSet:
            key_id = self.wordSet[synList[0]]
        else:
            key_id = synList[0]
            self.synonyms[key_id] = [key_id]
            self.wordSet[key_id] = key_id
        if len(key_id.split()) > self.gram:
            self.gram = len(key_id.split())
        if len(synList) < 2:
            return
        for word in synList[1:]:
            if len(word.split()) > self.gram:
                self.gram = len(word.split())
            if word in self.wordSet:
                comb_id = self.wordSet[word]
                # combing two synonyms lists.
                if key_id != comb_id:
                    if len(self.synonyms[key_id]) < len(self.synonyms[comb_id]):
                        key_id, comb_id = comb_id, key_id
                    for combWord in self.synonyms[comb_id]:
                        self.wordSet[combWord] = key_id
                    self.synonyms[key_id] += self.synonyms[comb_id]
                    self.synonyms.pop(comb_id, None)
            else:
                self.wordSet[word] = key_id
                self.synonyms[key_id].append(word)
    def iterSynonyms(self,word):
        if word in self.wordSet:
            for i in self.synonyms[self.wordSet[word]]:
                yield i
        else:
            yield word



class Sentence:
    wordData = WordDataset()
    __strips = ",.?!\""

    def __init__(self, sentence, synList = []):
        self.subSentenceSet = set()
        self.split_sentence = []
        self.str_sentence = sentence
        self.lst_sentence = [w.strip(self.__strips) for w in sentence.lower().split()]
        #for w in self.lst_sentence:
        #    self.addSynonyms([w])
        if synList:
            for lst in synList:
                self.addSynonyms(lst)
        # compute possible n-grams
        split_list = [[] for _ in range(len(self.lst_sentence))]
        for n in range(1,self.wordData.gram+1):
            for idx, n_gram in enumerate(zip(*[self.lst_sentence[i:] for i in range(n)])):
                token = ' '.join(n_gram)
                if token in self.wordData.wordSet:
                    ele_num = len(split_list[idx + n - 1])
                    for i in range(idx+n-1,idx-1, -1):
                        while len(split_list[i]) < ele_num:
                            split_list[i].append(self.lst_sentence[i])
                        ele_num = len(split_list[i]) if ele_num < len(split_list[i]) else ele_num
                    split_list[idx].append(token)
        
        n = [len(lst) if len(lst)>0 else 1 for lst in split_list]
        cnt = [0] * len(n)
        k = 0
        new_sentence = []
        while True:
            if cnt[k] < n[k]:
                if split_list[k]:
                    new_sentence.append(split_list[k][cnt[k]])
                else:
                    new_sentence.append(self.lst_sentence[k])
                cnt[k] += 1
                k += len(new_sentence[-1].split())
                if k >= len(n):
                    self.split_sentence.append(new_sentence.copy())
                    k -= len(new_sentence.pop().split())
                else:
                    cnt[k] = 0
            else:
                k -= len(new_sentence.pop().split())
            if k == 0:
                break
        #self.split_sentence = [['i','just had','dinner','too']] # [[' '.join(self.lst_sentence[x[0]:x[1]]) for x in zip(split_list[:-1],split_list[1:])]]

    def addSynonyms(self,synList):
        self.wordData.addSynonyms(synList)

    def enumSentence(self):
        return self.__enumSentence(self.split_sentence)

    def __enumSentence(self,split_sentence = []):
        sentence_set = set()
        for lst in split_sentence:
            iters= [self.wordData.iterSynonyms(lst[0])]
            stack = []
            k = 0
            n = len(lst)
            while True:
                word = next(iters[k],None)
                if word:
                    stack.append(word)
                    k += 1
                    if k == n:
                        if not ' '.join(stack) in sentence_set:
                            sentence_set.add(' '.join(stack))
                            yield ' '.join(stack)
                        stack.pop()
                        k -= 1
                    else:
                        iters.append(self.wordData.iterSynonyms(lst[k]))
                else:
                    stack.pop()
                    iters.pop()
                    k -= 1
                if k == 0:
                    break

    def enumSubSentence(self):
        return self.__enumSubSentence(self.split_sentence)

    def __enumSubSentence(self,split_sentence):
        for sentence in self.__enumSentence(split_sentence):
            lst = sentence.split()
            for start in range(len(lst)):
                for end in range(start+1,len(lst)+1):
                    subsequence = ' '.join(lst[start:end])
                    if not subsequence  in self.subSentenceSet:
                        self.subSentenceSet.add(subsequence)
                        yield subsequence

    def isSubSentence(self, str):
        if str in self.subSentenceSet:
            return True
        str_list = str.split()
        for l in self.split_sentence:
            k = 0
            started = False
            found = True
            for phrase in l:
                syn_list = [phrase] if phrase not in self.wordData.wordSet else self.wordData.synonyms[self.wordData.wordSet[phrase]].copy()
                while k < len(str_list):
                    if [p for p in syn_list if str_list[k] in p]:
                        syn_list = [p for p in syn_list if str_list[k] in p]
                        started = True
                        k += 1
                    elif started and not any([p.endswith(str_list[k-1]) for p in syn_list]):
                        found = False
                        break
                    else:
                        break
                if k >= len(str_list) or not found:
                    break
            if found:
                    return True
        return False

def test_Class(sentence):
    print(sentence.wordData.synonyms)
    print(sentence.wordData.wordSet)
    print(sentence.split_sentence)

def test_SubSentence(sentence):
    print(list(sentence.enumSubSentence()))

def test_Sentence(sentence):
    print(list(sentence.enumSentence()))

def test_isSubSentence(sentence):
    print(sentence.isSubSentence("just finished lunch"))
    print(sentence.isSubSentence("just lunch"))
    print(sentence.isSubSentence("have just"))
    print(sentence.isSubSentence("i already"))

if __file__ == 0:
    s = Sentence("I just had dinner, as well.", [['just had','have just finished'], ['dinner', 'meal', 'lunch'], ['too', 'as well'],['just','already'],['good','well']])
    test_Class(s)
    test_Sentence(s)
    test_isSubSentence(s)
    test_SubSentence(s)
    test_isSubSentence(s)

