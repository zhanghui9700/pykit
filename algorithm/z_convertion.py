#-*-coding=utf-8-*-

class Solution(object):
    def convert(self, s, numRows):
        """
        :type s: str
        :type numRows: int
        :rtype: str
        """
        if not s:
            return "" 
        if numRows < 2:
            return s

        rt = ["" for i in range(numRows)]
        
        index, flag = 0, 1
        for c in s: 
            rt[index] = rt[index] +  c
            if index == 0:
                flag = 1
            if index == numRows - 1:
                flag = -1
            index = index + flag
            
        print rt 
        return "".join(rt)

                

if __name__ == "__main__":
    s = Solution()
    print s.convert("LEETCODEISHIRING", 3) 
    print "LCIRETOESIIGEDHN"
    print s.convert("LEETCODEISHIRING", 4)
    print "LDREOEIIECIHNTSG"

    print s.convert("LEETCODEISHIRING", 2) 
    print s.convert("LEETCODEISHIRING", 1) 
