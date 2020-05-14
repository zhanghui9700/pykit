#-*-coding=utf-8-*-


class Node():
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def set_left(self, node):
        self.left = node

    def set_right(self, node):
        self.right = node

    def __str__(self):
        return str(self.value)
        
    def __repr__(self):
        return str(self.value)


class Solution(object):

    def _preorder(self, root): 
        if not root:
            return
        print root.value
        self.preorder(root.left)
        self.preorder(root.right)

    def preorder(self, root): 

        a = [root]

        while a:
            node = a.pop()
            print node.value
            if node.right:
                a.append(node.right)
            if node.left:
                a.append(node.left)

    def inorder(self, root): 
        if not root:
            return

        stack = []
        node = root
        while node or stack:
            while node:
                #print node.value, node.left.value  if node.left else None
                stack.append(node)
                print stack
                node = node.left
            node = stack.pop()
            print node.value
            node = node.right

    def postorder(self, root):
        stack1 = [root]
        stack2 = []

        while stack1:
            cur = stack1.pop()
            if cur.left:
                stack1.append(cur.left)

            if cur.right:
                stack1.append(cur.right)

            stack2.append(cur)

        while stack2:
            cur = stack2.pop()
            print cur.value


if __name__ == "__main__":
    root = Node(1)
    two = Node(2)
    three = Node(3)
    four= Node(4)
    five = Node(5)
    six = Node(6)
    seven = Node(7)
    eight = Node(8)

    root.left = two
    root.right = three

    two.left = four 
    two.right = five

    three.right = six

    five.left = seven
    five.right = eight

    s = Solution()
    #s.preorder(root)
    #s.inorder(root)
    s.postorder(root)
