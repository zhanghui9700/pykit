# -*- coding=utf-8 -*-


l  = [7, 3, 2, 5, 6, 1]


def run_v1():
    """
    第一轮遍历找到每个元素前方最小的值
    第二轮遍历找到每个元素前方最小的值
    """
    global l
    print l

    mins = []
    _min = l[0]

    for i in range(len(l)):
        print i
        if l[i] <= _min:  
            _min = l[i]
            mins.append(l[i])
        else:
            mins.append(_min)

    d = {}
    _max = 0
    for i in range(len(l)):
       v =  l[i] - mins[i]
       if v > 0:
           d[v] = l[i], mins[i]
       _max = max(v, _max)


    print mins, _max, d


def run_v2():
    """最小子序列
    """
    pass


if __name__ == '__main__':
    run_v1()
    run_v2()
