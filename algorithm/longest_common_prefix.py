#-*-coding=utf-8-*-


class Solution(object):
    def longestCommonPrefix(self, strs):
        """
        :type strs: List[str]
        :rtype: str
        """
        if not strs:
            return ""

        if len(strs) < 2:
            return strs[0]
  
        _min, _max = strs[0], strs[0] 
        _min_len, _max_len = len(strs[0]), len(strs[0])

        for i, s in enumerate(strs):
            if len(s) < _min_len:
                _min, _min_len = s, len(s)
            if len(s) > _max_len:
                _max, _max_len = s, len(s)

        print _min_len, _max_len
        print _min, _max

        for i in range(_min_len):
            if _min[i] != _max[i]:
                return _min[0: i]


if __name__ == "__main__":
    s = Solution()
    print s.longestCommonPrefix(["flower","flow","flight"])
    print s.longestCommonPrefix(["dog","racecar","car"])
