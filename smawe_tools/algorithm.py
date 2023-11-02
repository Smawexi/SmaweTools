def bubble_algorithm(array: list) -> list:
    """时间复杂度O(n^2), 对输入数组进行升序排序，返回排序后的数组副本"""
    array = array.copy()
    length = len(array)
    for i in range(length - 1):
        for j in range(length - 1 - i):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
    return array
