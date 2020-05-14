
class Solution_(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        result = []
        for i in range(len(nums)):
            v = target - nums[i]
            if v in nums[i+1:]:
                result.append(i)
                result.append(i+1+nums[i+1:].index(v))
                break
        print result
        return result


class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        m = {}
        result = []
        for i in range(len(nums)):
            v = target - nums[i]
            if m.has_key(v):
                result = [m.get(v), i]
                break
            else:
                m[nums[i]] = i
        print result
        return result




if __name__ == "__main__":
    f = Solution_()
    f.twoSum([2, 7, 11, 15], 9)
    f.twoSum([3, 2, 4], 6)
    f.twoSum([3, 3], 6)
    f.twoSum([2, 2, 5, 6], 7)
    print
    f = Solution()
    f.twoSum([2, 7, 11, 15], 9)
    f.twoSum([3, 2, 4], 6)
    f.twoSum([3, 3], 6)
    f.twoSum([2, 2, 5, 6], 7)
