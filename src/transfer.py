from collections import namedtuple

Raw_Example = namedtuple('Raw_Example', 'label entity1 entity2 sentence')
PositionPair = namedtuple('PosPair', 'first last')

'''
Raw_Example(label=18, entity1=PosPair(first=1, last=1),
            entity2=PosPair(first=9, last=9),
            sentence=['the', 'child', 'was', 'carefully', 'wrapped', 'and', 'bound', 'into', 'the', 'cradle', 'by', 'means', 'of', 'a', 'cord'])
'''
def load_raw_data(filename):
    data = []
    with open(filename) as f:
        for line in f:
            words = line.strip().split(' ')
            sent = words[5:]
            n = len(sent)
            label = int(words[0])
            entity1 = PositionPair(int(words[1]), int(words[2]))
            entity2 = PositionPair(int(words[3]), int(words[4]))
            example = Raw_Example(label, entity1, entity2, sent)
            data.append(example)
    return data

def replace_entity(example):
    entity1 = example.entity1
    entity2 = example.entity2
    label = example.label
    sent = example.sentence
    def replace(entity1 ,entity2, sent, re1, re2):
        if entity1.first != entity1.last:
            sent[entity1.first] = re1
            sent.pop(entity1.last)
            entity2 = PositionPair(entity2.first - 1, entity2.last -1)
        else:
            sent[entity1.first] = re1
        if entity2.first != entity2.last:
            sent[entity2.first] = re2
            sent.pop(entity2.last)
        else:
            sent[entity2.first] = re2
    result = {
            '0':lambda:replace(entity1, entity2, sent, "smoking","cancer"),
            '1':lambda:replace(entity1, entity2, sent, "cancer","smoking"),
            '2':lambda:replace(entity1, entity2, sent, "apartment","kitchen"),
            '3':lambda:replace(entity1, entity2, sent, "kitchen","apartment"),
            '4':lambda:replace(entity1, entity2, sent, "Earth","Milky"),
            '5':lambda:replace(entity1, entity2, sent, "Milkyy","Earth"),
            '6':lambda:replace(entity1, entity2, sent, "boy","bed"),
            '7':lambda:replace(entity1, entity2, sent, "bed","boy"),
            '8':lambda:replace(entity1, entity2, sent, "letters","countries"),
            '9':lambda:replace(entity1, entity2, sent, "countries","letters"),
            '10':lambda:replace(entity1, entity2, sent, "practices","engineers"),
            '11':lambda:replace(entity1, entity2, sent, "engineer","practices"),
            '12':lambda:replace(entity1, entity2, sent, "trees","forest"),
            '13':lambda:replace(entity1, entity2, sent, "forest","trees"),
            '14':lambda:replace(entity1, entity2, sent, "lecture","semantics"),
            '15':lambda:replace(entity1, entity2, sent, "semantics","lecture"),
            '16':lambda:replace(entity1, entity2, sent, "farmer","apples"),
            '17':lambda:replace(entity1, entity2, sent, "apples","farmer"),
            '18':lambda:replace(entity1, entity2, sent, "interrogation","activities")
        }
    return result[str(label)]()


def write_file(raw_train_data, example, count):
    f = open('files/' + str(count) , 'w')
    entity1 = example.entity1
    entity2 = example.entity2
    sent = example.sentence
    for data in raw_train_data:
        tmp_example = Raw_Example(data.label, entity1, entity2, sent.copy())
        replace_entity(tmp_example)
        sent_tmp = ' '.join(tmp_example.sentence)
        sent1 = ' '.join(data.sentence)
        f.write(sent_tmp + '\t' + sent1 + '\n')
    f.close()


raw_train_data = load_raw_data("../data/train.cln")
raw_test_data = load_raw_data("../data/test.cln")
for example in raw_train_data:
    replace_entity(example)
count = 0
for example in raw_test_data:
    write_file(raw_train_data, example, count)
    count += 1



