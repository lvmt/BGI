#!/usr/bin/env python

'''
查找字符串在指定字符串的全部位置.
'''


def find_all_pos(substr,string):
    length = len(substr)

    indexlist = []
    i = 0
    while substr in string[i:]:
        index = string.index(substr,i)
        indexlist.append(index)
        i = index + length

    return indexlist


if __name__ == '__main__':

    substr = 'GGG'
    string = 'AAGGGTTTGGGTTTTTTGGG'

    print(find_all_pos(substr, string))

