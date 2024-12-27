# -*- coding: UTF-8 -*-
# @Date    :2024/4/22 21:17
# @Author  :高猛
# @Project :MPDA_ACO-main 
# @File    :lc.py
# @IDE     :PyCharm

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class MyLinkedList:

    def __init__(self, lst=None):
        self.vh = ListNode(0)
        self.cur = self.vh
        if lst is None:
            lst = []
        for i in lst:
            n = ListNode(i)
            self.cur.next = n
            self.cur = n

    def get(self, index):
        self.cur = self.vh.next
        while index > 0 and self.cur:
            self.cur = self.cur.next
            index -= 1
        return -1 if self.cur is None else self.cur.val

    def addAtHead(self, val):
        newh = ListNode(val, self.vh.next)
        self.vh.next = newh

    def addAtTail(self, val):
        newt = ListNode(val)
        self.cur = self.vh
        while self.cur.next:
            self.cur = self.cur.next
        self.cur.next = newt

    def addAtIndex(self, index, val):
        newn = ListNode(val)
        self.cur = self.vh
        while index > 0 and self.cur.next:
            self.cur = self.cur.next
            index -= 1
        if index == 0:
            newn.next = self.cur.next
            self.cur.next = newn

    def deleteAtIndex(self, index):
        self.cur = self.vh
        while index > 0 and self.cur.next:
            self.cur = self.cur.next
            index -= 1
        if index == 0 and self.cur.next:
            self.cur.next = self.cur.next.next

    def print_list(self):
        p = []
        self.cur = self.vh.next
        while self.cur:
            p.append(self.cur.val)
            self.cur = self.cur.next
        print(p)


def test_MyLinkedList():
    # 创建一个空的链表
    my_linked_list = MyLinkedList()

    # 向链表头部添加元素
    my_linked_list.print_list()
    my_linked_list.addAtHead(1)

    my_linked_list.print_list()
    my_linked_list.addAtHead(2)

    my_linked_list.print_list()
    my_linked_list.addAtHead(3)

    my_linked_list.print_list()

    # 验证头部添加后的元素个数和特定位置的元素值
    assert my_linked_list.get(0) == 3  # 第一个元素是3
    assert my_linked_list.get(1) == 2  # 第二个元素是2
    assert my_linked_list.get(2) == 1  # 第三个元素是1

    # 向链表尾部添加元素
    my_linked_list.addAtTail(4)
    my_linked_list.print_list()
    assert my_linked_list.get(3) == 4  # 第四个元素是4

    # 在索引2的位置添加元素5
    my_linked_list.addAtIndex(2, 5)
    my_linked_list.print_list()
    assert my_linked_list.get(2) == 5  # 索引2的元素现在是5

    # 删除索引1的位置的元素
    my_linked_list.deleteAtIndex(1)
    my_linked_list.print_list()
    assert my_linked_list.get(1) == 5  # 索引1的元素现在是5

    # 尝试获取超出范围的元素，应该返回-1
    assert my_linked_list.get(10) == -1
    my_linked_list.print_list()

    my_linked_list.addAtIndex(4, 8)
    my_linked_list.print_list()

    my_linked_list.addAtIndex(11, 9)
    my_linked_list.print_list()

    print("All tests passed.")


# 运行测试用例
test_MyLinkedList()