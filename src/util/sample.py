import sys
import random

def get_raw_data(data_file):
    raw_dict = {}
    total = 0
    for line in open(data_file):
        ss = line.strip().split(" ")
        try:
            label = int(ss[0])
            total += 1
            if label not in raw_dict:
                raw_dict[label] = list()
            raw_dict[label].append(line.strip())
        except:
            continue
    return total, raw_dict

def sample_from_raw_data(raw_dict, sample_rate):
    sample_dict = {}
    for label in raw_dict:
        raw_list = raw_dict[label]
        sample_dict[label] = random.sample(raw_list, int(len(raw_list) * sample_rate))
    return sample_dict

def write_sample_file(sample_dict, filename):
    sample = list()
    for label in sample_dict:
        sample.extend(sample_dict[label])
    random.shuffle(sample)
    with open(filename, 'w') as f:
        for ss in sample:
            f.write(ss)
            f.write('\n')

if __name__ == '__main__':
    total, raw_dict = get_raw_data(sys.argv[1])
    print("total data num is %d" %(total))
    sample_rate = [x * 0.1 for x in range(1, 10)]
    for srt in sample_rate:
        sample = sample_from_raw_data(raw_dict, srt)
        write_sample_file(sample, sys.argv[2]+ "."+ str(int(srt * 10)))


