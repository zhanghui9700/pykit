#-*-coding=utf-8-*-

# "babad" -> aba or bab
# "cbbbd" -> bbb


class Solution(object):

    def longestPalindrome(self, s):
        """
        :type s: str
        :rtype: str
        """
        if not s:
            return ""

        rt = s[0]
        i, n, _max  = 0, len(s), len(rt)
        while i < n:
            alpha = s[i]
            next_alpha = s.find(alpha, i+1)
            print "alpha:", alpha, "next:", next_alpha
            while next_alpha >=0:
                _s =  s[i:next_alpha+1]
                print "next_alpha:", _s
                if _s == _s[::-1]:
                    if len(_s) > _max:
                        rt = _s
                        _max = len(_s)
                
                next_alpha = s.find(alpha, next_alpha+1)
                if next_alpha<0:
                    break
            i = i + 1    
        print "s: ", s, "->", rt
        return rt


def run():
    s = Solution()
    #s.longestPalindrome(None)
    #s.longestPalindrome("")
    #s.longestPalindrome("babad")
    #s.longestPalindrome("cbbbbd")
    #s.longestPalindrome("bbbbd")
    #s.longestPalindrome("abcda")
    s.longestPalindrome("aaabaaaa")


if __name__ == "__main__":
    run()
