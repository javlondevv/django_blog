# costs = [1, 3, 2, 4, 1]
# coins = 7
#
#
# class Solution:
#     def maxIceCream(self, costs: list[int], coins: int) -> int:
#         result = res = 0
#         for i in sorted(costs):
#             result += i
#             res += 1
#             if result == coins:
#                 return res
#             elif result >= coins:
#                 return res
#
#
# a = Solution()
# print(a.maxIceCream([1, 6, 3, 1, 2, 5], 20))


version1 = "0.1"
version2 = "1.1"
if version1.count('.') == 2:
    print(0)
elif  version2.count('.') == 2:
    print(0)
else:
    print(int(float(version1)-float(version2)))