class Solution(object):
    def isPalindrome(self, x):
        """
        :type x: int
        :rtype: bool
        """
        rt = False

        if isinstance(x, int) and x > 0:
            _x = x
            m = 0 
            
            while _x > 0: 
                _x, _m = _x // 10, _x % 10
                m = m * 10 + _m
            rt = m == x
        
        
        if isinstance(x, int) and x == 0:
            rt = True

        return rt


if __name__ == "__main__":
    s = Solution()
    print s.isPalindrome(121) 
    print s.isPalindrome(-121) 
    print s.isPalindrome(10) 
    print s.isPalindrome(0) 
