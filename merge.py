"""
Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.

The overall run time complexity should be O(log (m+n)).

 

Example 1:

Input: nums1 = [1,3], nums2 = [2]
Output: 2.00000
Explanation: merged array = [1,2,3] and median is 2.
Example 2:

Input: nums1 = [1,2], nums2 = [3,4]
Output: 2.50000
Explanation: merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.
"""

class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
          # Always binary search on the smaller array
          if len(nums1) > len(nums2):
               nums1, nums2 = nums2, nums1

          m, n = len(nums1), len(nums2)
          lo, hi = 0, m  # i ranges from 0 to m
          half = (m + n + 1) // 2  # size of the left half

          while lo <= hi:
               i = (lo + hi) // 2      # elements taken from nums1's left
               j = half - i            # elements taken from nums2's left

               # Sentinel values for out-of-bounds
               left1  = nums1[i - 1] if i > 0 else float('-inf')
               right1 = nums1[i]     if i < m else float('inf')
               left2  = nums2[j - 1] if j > 0 else float('-inf')
               right2 = nums2[j]     if j < n else float('inf')

               if left1 <= right2 and left2 <= right1:
                    # Valid cut found
                    if (m + n) % 2 == 1:
                         return max(left1, left2)
                    else:
                         return (max(left1, left2) + min(right1, right2)) / 2
               elif left1 > right2:
                    hi = i - 1   # i too large, move left
               else:
                    lo = i + 1   # i too small, move right
                    
decimal_value = 0
    for i, included in enumerate(S):
        decimal_value += (int(included) * (2**i))
    