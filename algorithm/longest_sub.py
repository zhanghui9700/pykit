#-*-coding=utf-8-*-

class Solution(object):
    
    def findLongest(self, nums):

        pre, _sum = 0, nums[0];
        for num in  nums:
            pre = max(pre+num, num)
            _sum = max(pre, _sum)
            print "-"*10
            print pre, _sum
  
        return _sum


class Solution(object):
    
    def findLongest(self, nums):

        _min = nums[0]
        _max = 0
        for index,v in enumerate(nums):
            _min = min(v, _min)
            _max = max(v-_min, _max)
            
        return _max 


if __name__ == "__main__":
    s = Solution()
    print s.findLongest([-2,1,-3,4,-1,2,1,-5,4])
    print s.findLongest([-2,1,-1])
    print s.findLongest([7,1,5,3,6,4])
    print s.findLongest([7,6,4,3,1])
