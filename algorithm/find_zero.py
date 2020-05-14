#-*- coding=utf-* -*-

# 无需数组差值最近接0


def finder(array=None):
    arr = array
    arr.sort()
    print arr

    if len(arr) <= 2:
        raise

    if arr[0] >= 0:
        print arr[0], arr[1]
        return
    elif arr[0] <0 and arr[-1] <= 0:
        print arr[-2], arr[-1]
        return

    dct = {}
    i,j = 0, len(arr) - 1
    result = arr[j]

    while i < j:
        _cmp = arr[i] + arr[j]
        dct[abs(_cmp)] = [arr[i], arr[j]]

        result = min(abs(_cmp), result)
        print _cmp, result

        if _cmp > 0:
            j = j -1
            continue
        elif _cmp < 0:
            i = i + 1
            continue
        else:
            break
 
    print "small: ", result, dct[result]


if __name__ == "__main__":
    #array = [1, 2, 3, 7, 9, -4, -5, -6, -8]
    #array = [-10, -8, -6, 1, 2, 3, 11]
    array = [-10, -8, -6, -4, -3, -1]
    finder(array)


    array = [1, 2, 3, 7, 9, 10]
    finder(array)


    array = [-10, -8, -6, 1, 2, 3, 11]
    finder(array)
