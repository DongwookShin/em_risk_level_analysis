import re
import sys
sys.path.append("..")


def main():       
    ifile = open('./data/annotation_second_testing.tsv', "r")
    ofile = open('./data/annotation_second_dedup_testing.tsv', "w")
    quoteDic = {}           
    lines = ifile.readlines()

    for line in lines:
        items = line.split('\t')
        if not items[0] in quoteDic:
            quoteDic[items[0]] = items[1]

    for key in quoteDic.keys():
        ofile.write(key + "\t" + quoteDic[key])

    ofile.close()

if __name__ == '__main__':
    main()
