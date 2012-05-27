#!/bin/bash python
#-*-coding=utf-8-*-

import pdb
import sys

class Chessman(object):
    '''棋盘的节点'''
    def __init__(self,x,y):
        assert x >= 0 and y >= 0
        self.x = x
        self.y = y

    def get_childs(self,chessboard):
        raise Exception('subclass must implent this method!!!')
    
    def __str__(self):
        return '(X:%d,Y:%d)'%(self.x,self.y)

    def __cmp__(self,other):
        return cmp(self.x,other.x) and cmp(self.y,other.y)

    def __eq__(self,other):
        return self.x == other.x and self.y == other.y

    def __contians__(self,other):
        return self.x == other.x and self.y == other.y

class Knight(Chessman):
    '''棋子-马'''
    def get_childs(self,chessboard):
        result = []
        
        for x in [-2,2]:
            for y in [-1,1]:
                if self.x + x >= 0 and self.x + x < chessboard.dim \
                    and self.y + y >=0 and self.y + y < chessboard.dim:
                    result.append(Knight(self.x + x,self.y + y))

        for x in [-1,1]:
            for y in [-2,2]:
                if self.x + x >= 0 and self.x + x < chessboard.dim \
                    and self.y + y >=0 and self.y + y < chessboard.dim:
                    result.append(Knight(self.x + x,self.y + y))

        return result

class Chessboard(object):
    '''
    @棋盘
    棋盘提供一个n*n的矩阵
    '''
    def __init__(self,dimension=5):
        assert dimension <= 8 and dimension > 1
        self.dim = dimension
        self.chessmans = [[Chessman(x,y) for y in range(dimension)] \
                                          for x in range(dimension)]

        self.actived = None
        
    def initialize(self,*args,**kwargs):
        '''棋盘初始化,布置各类棋子的初始位置'''
        for chessman in args:
            self.chessmans[chessman.x][chessman.y] = chessman

    def get_chessman(self,x,y):
        assert x >= 0 and x < self.dim 
        assert y >= 0 and y < self.dim

        return self.chessmans[x][y]
    
    def active(self,chessman):
        self.actived = None
        if chessman:
            self.actived = chessman

    def get_actived(self):
        return self.actived
         
class PathUtility(object):
    '''
    寻路工具类
    '''
    def __init__(self,chessboard):
        self.chessboard = chessboard
        self.path = []
        self.found = False

    def set_target(self,target):
        self.path = []
        self.found = False
        self.target = target

    def find_path(self,source):
        if self.found:
            return self.found;
        
        self.path.append(source)
        if source == self.target:
            self.found = True
        else:
            childs = [chess for chess in source.get_childs(self.chessboard) \
                                                if chess not in self.path]
            for chess in childs:
                if chess == self.target:
                    self.found = True
                    break

            if not self.found:
                for chess in childs:
                    self.found = self.find_path(chess)
                    if not self.found:
                        self.path.pop()

        return self.found

    def print_path(self):
        screen = [['-+-' for y in range(self.chessboard.dim)] \
                            for x in range(self.chessboard.dim)]
        i = 1
        for item in self.path:
            screen[item.x][item.y] = '%3s'%i
            i += 1
        
        screen[self.target.x][self.target.y] = '%3d'%i
        
        xdim = range(self.chessboard.dim)
        xdim.reverse()
        
        print 'found_path:'
        for x in xdim:
            for y in range(self.chessboard.dim):
                print screen[y][x],
            print ''
        print ''

def main(N,x,y):
    chessboard = Chessboard(dimension=N) 
    chessboard.active(Knight(x,y))
    
    pathUtility = PathUtility(chessboard)
    
    target = chessboard.get_chessman(N-1,N-1)
    pathUtility.set_target(target)

    source = chessboard.get_actived()
    is_found = pathUtility.find_path(source)

    print '*'*30
    
    if is_found:
        for item in pathUtility.path:
            print item,'>',
        print target 
        pathUtility.print_path()
    else:
        print u'未发现路径......！'

    print 'done...'

if __name__ == '__main__':
    try:
        if len(sys.argv) == 4:
            N,x,y = sys.argv[1:]
            assert N.isdigit() and x.isdigit() and y.isdigit() 
            main(int(N),int(x),int(y))
        else:
            print 'argument parse error!eg:python knight.py 8 2 2'
            print 'please retry again...'
    except Exception,ex:
        print 'i\' so sorry! Application has crushed,please paste the error message and give me a feedback,thannks!'
        print ex

