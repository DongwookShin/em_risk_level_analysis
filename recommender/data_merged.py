import re
import sys
sys.path.append("..")


def main():       
    ifile1 = open('./data/annotation_first_cleaned.tsv', "r")
    ifile2 = open('./data/annotation_second_cleaned.tsv', "r")
    ofile = open('./data/annotation_combined_cleaned.tsv', "w")

    quoteDic = {}
    lines = ifile1.readlines()

    for line in lines:
        items = line.split('\t')
        if not items[0] in quoteDic:
            quoteDic[items[0]] = items[1]
            
    lines = ifile2.readlines()

    for line in lines:
        items = line.split('\t')
        if not items[0] in quoteDic:
            quoteDic[items[0]] = items[1]

    for key in quoteDic.keys():
        ofile.write(key + "\t" + quoteDic[key])

    ofile.close()

if __name__ == '__main__':
    main()
