#-*-coding=utf-8-*-

class Solution(object):
    def stat(self, ages):
        ag = [0 for i in range(100)]
        max_aget = 99
        for i in ages:
            ag[i] = ag[i] + 1

        print ag
        index = 0
        for i in range(100):
            j = 0
            while j < ag[i]:
                ages[index] = i
                j = j + 1
                index = index +1

        return ages


                

if __name__ == "__main__":
    s = Solution()
    print s.stat([20, 18, 21, 20, 25, 21]) 
