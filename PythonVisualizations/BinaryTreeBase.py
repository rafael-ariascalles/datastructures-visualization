from tkinter import *
import time, random
from enum import Enum

try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

class Child(Enum):
    LEFT = 0
    RIGHT = 1

class Node(object):
    def __init__(self, drawable, coords, tag):
        self.drawable = drawable
        self.coords = coords
        self.tag = tag

    def getKey(self):
        return self.drawable.val

    def setKey(self, k):
        self.drawable.val = k

    def __str__(self):
        return "{" + str(self.getKey()) + "}"

class BinaryTreeBase(VisualizationApp):
    # -------- CONSTANTS ------------------
    FONT_SIZE = -16
    VALUE_FONT = ('Helvetica', FONT_SIZE)
    FOUND_FONT = ('Helvetica', FONT_SIZE)

    def __init__(self, X0, Y0, X1, Y1, CIRCLE_SIZE = 15, 
               ARROW_HEIGHT = 30,MAX_LEVEL = 5, **kwargs):
        """Build a VisualizationApp that will show a binary tree on part of the
        canvas within the rectangle bounded by (X0, Y0) and (X1, Y1).
        CIRCLE_SIZE is the radius of the circles used for each node in the tree.
        ARROW_HEIGHT is the length of a pointer arrow to point at a node.
        MAX_LEVEL is one more than the maximum node level allowed in the tree.
        """
        super().__init__(**kwargs)
        
        self.CIRCLE_SIZE = CIRCLE_SIZE       # radius of each node
        self.ARROW_HEIGHT = ARROW_HEIGHT     # indicator arrow height
        self.MAX_LEVEL = MAX_LEVEL           # the max level of the tree plus 1
        self.ROOT_X0 = (X0 + X1) // 2        # root's x center
        self.ROOT_Y0 = Y0 + ARROW_HEIGHT + CIRCLE_SIZE # root's y center
        self.TREE_WIDTH = X1 - X0 - 2 * CIRCLE_SIZE # max tree width
        # the vertical gap between levels
        self.LEVEL_GAP = (Y1 - CIRCLE_SIZE - self.ROOT_Y0) / max(1, MAX_LEVEL - 1)

        # tree will be stored in array
        # root will be index 0
        # root's left child will be index 1, root's right child will be index 2
        self.maxElems = 2 ** self.MAX_LEVEL     
        self.nodes = [None] * self.maxElems
        self.size = 0

        self.prevId = -1      # One up counter for node tags

    # --------- ACCESSOR METHODS ---------------------------

    # returns the index of the node
    def getIndex(self, node):
        for i in range(len(self.nodes)):
            if self.nodes[i] is node:
                return i
      
        return -1

    # return's the node's left child's index
    def getLeftChildIndex(self, node):
        nodeIndex = self.getIndex(node)
        childIndex = 2*nodeIndex + 1

        if childIndex >= self.maxElems: return -1
        else: return childIndex

    # return's the node's right child's index
    def getRightChildIndex(self, node):
        nodeIndex = self.getIndex(node)
        if nodeIndex == -1: return -1
        childIndex = 2*nodeIndex + 2

        if childIndex >= self.maxElems: return -1
        else: return childIndex

    # returns the node's left child
    def getLeftChild(self, node):
        childIndex = self.getLeftChildIndex(node)

        if childIndex != -1: return self.nodes[childIndex]
        else: return None

    # returns the node's right child
    def getRightChild(self, node):
        childIndex = self.getRightChildIndex(node)

        if childIndex != -1: return self.nodes[childIndex]
        else: return None

    # returns the root node
    def getRoot(self):
        return self.nodes[0]

    # returns True if node is the root
    def isRoot(self, node):
        return self.nodes[0] is node

    # returns True if the node has no children, false otherwise
    def isLeaf(self, node):
        # if neither a right or left child exists
        if not (self.getRightChild(node) or self.getLeftChild(node)):
            return True
        else: return False

    # returns True if node is a right child, false otherwise
    def isRightChild(self, node):
        # is it the root?
        if self.isRoot(node): return False

        # right child will always be an even index
        index = self.getIndex(node)
        return index % 2 == 0

    # returns True if node is a left child, false otherwise
    def isLeftChild(self, node):
        # left child will always be an odd index
        index = self.getIndex(node)
        return index % 2 == 1

    # returns enum if node is right or left child
    # returns None if node is the root
    def getChildDirection(self, node):
        if self.isRoot(node):
            direction = None
        elif self.isRightChild(node):
            direction = Child.RIGHT
        else:
            direction = Child.LEFT
        return direction

    # returns the node's parent
    def getParent(self, node):
        # is it the root?
        if self.isRoot(node): return None

        parentIndex = self.getParentIndex(node)
        return self.nodes[parentIndex]

    def getParentIndex(self, node):
        # get node's index
        index = self.getIndex(node)
        return (index - 1) // 2

    # returns the level of the node
    def getLevel(self, node):
        if self.isRoot(node): return 0
        else: return self.getLevel(self.getParent(node)) + 1

    def getHeight(self, node):
        if not node: return 0

        rightChild = self.getRightChild(node)
        leftChild = self.getLeftChild(node)

        return max(self.getHeight(rightChild), self.getHeight(leftChild)) + 1

    # return difference in node's child heights
    def heightDiff(self, node):
        leftChild, rightChild = self.getChildren(node)
        left = self.getHeight(leftChild) if leftChild else 0
        right = self.getHeight(rightChild) if rightChild else 0

        return left - right

    # returns the line pointing to the node
    def getLine(self, node, highlight=False):
        coords = self.calculateLineCoordinates(node)
        # is there a line in these coords?
        overlap = set(self.canvas.find_overlapping(*coords))

        if not highlight: line = set(self.canvas.find_withtag("line"))
        else: line = set(self.canvas.find_withtag("highlight line"))

        foundLine = (overlap & line)
        if len(foundLine) > 1 and node: return set(self.canvas.find_withtag(node.tag + " line")).pop()
        else: return foundLine.pop() if len(foundLine) > 0 else None 
      
    # returns a tuple of the left and right child of node
    def getChildren(self, node):
      return self.getLeftChild(node), self.getRightChild(node)

    # returns the level of the node
    def getLevel(self, node):
        if self.isRoot(node): return 0
        else: return self.getLevel(self.getParent(node)) + 1

    def getHeight(self, node):
        if not node: return -1

        rightChild = self.getRightChild(node)
        leftChild = self.getLeftChild(node)

        return max(self.getHeight(rightChild), self.getHeight(leftChild)) + 1

    # returns the line pointing to the node from its parent
    def getLine(self, node, highlight=False):
        items = self.canvas.find_withtag(node.tag + " line")
        return None if len(items) == 0 else set(items).pop()
      
    # returns a tuple of the left and right child of node
    def getChildren(self, node):
        return self.getLeftChild(node), self.getRightChild(node)

    # returns a list of all the nodes that descend from node
    def getAllDescendants(self, node):
        if not node: return []

        left, right = self.getChildren(node)
        return (([left] if left else []) + ([right] if right else []) +
                self.getAllDescendants(left) + self.getAllDescendants(right))

    # returns the subtree of the node
    def getSubtree(self, node):
        if not node:
            return []
        curIndex = self.getIndex(node)
        que = []
        subTree = []

        # keep going until the bottom of the tree
        while curIndex < self.maxElems:
            # add the current node to the subtree
            node = self.nodes[curIndex]
            subTree.append(self.nodes[curIndex])
            
            # add the left and right child to the que
            que += [2*curIndex+1, 2*curIndex+2]

            # get the next index to process
            curIndex = que.pop(0)

        return subTree


    # ----------- DRAWING METHODS -------------------
   
    # monkey patching to allow for circles to be drawn easier
    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    Canvas.create_circle = _create_circle

    # Create an arrow to point at a node
    def createArrow(self, nodeOrCoords):
        if isinstance(nodeOrCoords, Node):
            coords = node.coords
        else:
            coords = nodeOrCoords
        
        arrow = self.canvas.create_line(coords[0], coords[1] - self.CIRCLE_SIZE - self.ARROW_HEIGHT,
                                        coords[0], coords[1] - self.CIRCLE_SIZE, arrow="last", fill='red')
        return (arrow, )

    # move the arrow to point above the node
    def moveArrow(self, arrow, node, numSteps=10, sleepTime=0.02):
        # was a node passed in?
        if isinstance(node, Node):
            toPos = (node.coords[0], node.coords[1] - self.CIRCLE_SIZE - self.ARROW_HEIGHT,
            node.coords[0], node.coords[1] - self.CIRCLE_SIZE)
        # were the coords passed?
        elif isinstance(node, tuple):
            toPos = (node[0], node[1] - self.CIRCLE_SIZE - self.ARROW_HEIGHT,
            node[0], node[1] - self.CIRCLE_SIZE)

        self.moveItemsTo(arrow, (toPos,), steps = numSteps, sleepTime=sleepTime)

    # get the coords for where to move the arrow
    def getMoveArrowCoords(self, arrow, nodeCoords):
        return (nodeCoords[0], nodeCoords[1] - self.CIRCLE_SIZE - self.ARROW_HEIGHT,
                nodeCoords[0], nodeCoords[1] - self.CIRCLE_SIZE)

    # calculate the coordinates for the node shape
    def calculateCoordinates(self, parent, level, childDirection):
        if level == 0:
            return self.ROOT_X0, self.ROOT_Y0
        elif childDirection == Child.LEFT:
            return parent.coords[0] - 1/2**(level+1)* self.TREE_WIDTH, self.ROOT_Y0+level* self.LEVEL_GAP
        else:
            return parent.coords[0] + 1/2**(level+1)* self.TREE_WIDTH, self.ROOT_Y0+level* self.LEVEL_GAP
        
    def nodeShapeCoordinates(self, center):
        return (center[0] - self.CIRCLE_SIZE, center[1] - self.CIRCLE_SIZE,
                center[0] + self.CIRCLE_SIZE, center[1] + self.CIRCLE_SIZE)

    # calculate the coordinates for the line attached to the node
    def calculateLineCoordinates(self, node, parent=None):
        # get node's parent
        if parent is None:
            parent = self.getParent(node)
        return parent.coords + node.coords

    # highlight or unhighlight the line that points to the node
    def createHighlightedLine(self, node, callEnviron=None, color= drawable.palette[0]):
        line = self.getLine(node)
        if line is None:
            return
        highlightLine = self.copyCanvasItem(line)
        self.canvas.tag_lower(highlightLine,
                            self.getRoot().drawable.display_shape)

        self.canvas.itemconfig(highlightLine, fill=color, width=4, tags= "highlight line")

        if callEnviron: callEnviron.add(highlightLine)

        return highlightLine

    def createHighlightedCircle(self, node, callEnviron=None, color=drawable.palette[0]):
        circle = self.copyCanvasItem(node.drawable.display_shape)
        self.canvas.itemconfig(circle, outline=color, fill= '', width=2,
                               tags="highlight circle")

        if callEnviron: callEnviron.add(circle)

        return circle

    # creates a highlighted value on top of the normal value associated with the node
    def createHighlightedValue(self, node, callEnviron=None, color=drawable.palette[0]):
        text = self.canvas.create_text(
            *node.coords, text=node.getKey(), font=self.VALUE_FONT, fill=color,
            tags="highlight value")
      
        if callEnviron: callEnviron |= set((text,))

        return text

    # draws the circle and the key value
    def createNodeShape(self, x, y, key, tag, color= drawable.palette[2]):
        circle = self.canvas.create_circle(x, y, self.CIRCLE_SIZE, tag = tag, fill=color, outline='')
        circle_text = self.canvas.create_text(x,y, text=key, font=self.VALUE_FONT, tag = tag)

        return circle, circle_text

    def restoreNodesPosition(self, moveItems, arrow=None, sleepTime=0.1):
        "moves all the nodes in moveItems to their proper place (as defined by their place in the array)"
        # get the coords for the node to move to
        moveCoords = []
        moveItemsTags = []
        for node in moveItems:
            if node:
                # add the node and its coordinates
                moveItemsTags.append(node.tag)
                node.coords = self.calculateCoordinates(self.getParent(node), self.getLevel(node), self.getChildDirection(node))
                moveCoords.append(( node.coords[0]-self.CIRCLE_SIZE, node.coords[1]-self.CIRCLE_SIZE,
                                        node.coords[0]+self.CIRCLE_SIZE, node.coords[1]+self.CIRCLE_SIZE))
        arrowList = []
        arrowCoords = []
        if arrow:
            arrowList.append(arrow)
            arrowCoords.append(self.getMoveArrowCoords(arrow, node.coords))
        if len(moveItemsTags) > 0: self.moveItemsTo(moveItemsTags+arrowList, moveCoords+arrowCoords, sleepTime=sleepTime)

    # draw a line pointing to node
    def createLine(self, node):
        parent = self.getParent(node)
        lineCoords = self.calculateLineCoordinates(node, parent)
        line = self.canvas.create_line(*lineCoords, tags = ("line", node.tag + " line"))
        self.canvas.tag_lower(line)

    # remove all the line drawings
    def clearAllLines(self):
        self.canvas.delete("line")

    # draw all the lines
    def drawAllLines(self):
        cur = self.getRoot()
        if cur:
            left = self.getLeftChild(cur)
            right = self.getRightChild(cur)
            self.__drawLines(left, right)

    def __drawLines(self, left, right):
        if left: 
            self.createLine(left)
            self.__drawLines(self.getLeftChild(left), self.getRightChild(left))
        if right: 
            self.createLine(right)
            self.__drawLines(self.getLeftChild(right), self.getRightChild(right))

    # remove any existing lines and draw lines
    def redrawLines(self):
        self.clearAllLines()
        self.drawAllLines()

   # ----------- SETTER METHODS --------------------
   
   # create a Node object with key and parent specified
   # parent should be a Node object
    def createNode(self, key, parent = None, direction = None, addToArray=True,):
        # calculate the level
        if not parent: level = 0
        else: level = self.getLevel(parent) + 1                                                
        
        # calculate the coords
        coords = self.calculateCoordinates(parent, level, direction)
        x,y = coords

        # generate a tag
        tag = self.generateTag()

        # create the shape and text
        circle, circle_text = self.createNodeShape(x, y, key, tag)
        
        # create the drawable object
        drawableObj = drawable(key, self.canvas.itemconfigure(circle, 'fill')[-1], *(circle, circle_text))
        
        # create the Node object
        node = Node(drawableObj, coords, tag)

        # increment size
        self.size += 1

        # add the node object to the internal representation
        if addToArray: self.setChildNode(node, direction, parent)

        # draw the lines
        if parent:
            self.createLine(node)

        return node 

    # create a copy of a Node object
    def copyNode(self, node):
        # create a tag
        tag = self.generateTag()

        # get the circle and key drawing
        circle, circle_text = self.createNodeShape(*(node.coords), node.getKey(), tag)

        # get the key
        key = node.getKey()
        # create the drawable obj
        drawableObj = drawable(key, self.canvas.itemconfigure(circle, 'fill')[-1], circle, circle_text)

        # add the tag
        self.canvas.itemconfig(circle, tags=tag)
        self.canvas.itemconfig(circle_text, tags=tag)
      
        return Node(drawableObj, node.coords, tag)

    def setRoot(self, node):
        self.nodes[0] = node

    # set the node's left child
    def setLeftChild(self, node, child):
        index = self.getLeftChildIndex(node)
        if index != -1:
            self.nodes[index] = child
            return index
        else:
            return -1

    # set the node's right child
    def setRightChild(self, node, child):
        index = self.getRightChildIndex(node)
        if index != -1:
            self.nodes[index] = child
            return index
        else:
            return -1

    # set the node's child
    # returns the index where the child is stored
    def setChildNode(self, child, direction = None, parent = None):
        if not parent:
            self.nodes[0] = child
            return 0

        if direction == Child.LEFT:
            return self.setLeftChild(parent, child)
        else:
            return self.setRightChild(parent, child)

    def moveSubtree(self, toIndex, fromThis):
        "Move subtree rooted at fromThis (can be index or list) to be rooted at toIndex"
        if (isinstance(fromThis, list)):
            fromList = fromThis
            fromIndex = 0

            if (toIndex < 0 or toIndex >= len(self.nodes)):
                return
        else:
            fromList = self.nodes
            fromIndex = fromThis
            
            if (toIndex < 0 or toIndex >= len(self.nodes) or
            fromIndex < 0 or fromIndex >= len(self.nodes)):
                return           # Do nothing if to or from index out of bounds
        
        toDo = [(toIndex, fromIndex)] # Queue of assignments to make
        while len(toDo):      # While there are subtrees to move
            top = toDo.pop(0) # Get next subtree to move from front of queue
            tIndex, fIndex = top
            
            # stop if tree cannot hold nodes > tIndex
            if tIndex >= len(self.nodes): break

            fNode = fromList[fIndex] if fIndex < len(fromList) else None
            self.nodes[tIndex] = fNode
            if fNode:         # If from node exists
                for child in range(1, 3): # Loop over child's children
                    toDo.append(   # Enqueue move granchild to child position
                        (2 * tIndex + child, 2 * fIndex + child))

    def generateTag(self):
        self.prevId+=1
        return "item" + str(self.prevId)

    # remove node and any of its descendants from the internal array
    def clearDescendants(self, node, subSize = True):
        if isinstance(node, Node):
            nodeIndex = self.getIndex(node)
        else:
            nodeIndex = node

        # stop if node does not exist in tree
        if not node or nodeIndex == -1 or nodeIndex >= self.maxElems: return
        
        # get the child indices
        leftIndex = 2*nodeIndex + 1
        rightIndex = 2*nodeIndex + 2
        
        # remove from tree
        self.nodes[nodeIndex] = None
        if subSize: self.size -= 1

        # recursively remove children
        self.clearDescendants(leftIndex, subSize= subSize)
        self.clearDescendants(rightIndex, subSize = subSize)

    # remove the tree's drawing
    # empty the tree's data
    def emptyTree(self):
        self.canvas.delete("all")
        self.size = 0
        self.nodes = [None] * (2**self.MAX_LEVEL)

    # remove the node's drawing
    def removeNodeDrawing(self, node, line=False):
        # should the line pointing to the node be removed?
        if line: self.removeLine(node)

        self.canvas.delete(node.tag)

    # remove the line that was pointing to node
    def removeLine(self, node):
        line = self.getLine(node)
        if line: self.canvas.delete(line)

    # remove the node from the internal array
    def removeNodeInternal(self, node):
        self.nodes[self.getIndex(node)] = None
        self.size -= 1

    def removeNodesInternal(self, nodeList):
        for node in nodeList:
            self.removeNodeInternal(node)

    def rotateLeft(self, top, animation=True):
        "rotate a subtree to the left in the array and animate it"
        # the node to raise is top's right child
        toRaise = self.getRightChild(top)

        # save top's left subtree
        topLeft = self.getLeftChild(top)
        topLeftTree = self.getSubtree(topLeft)

        # save toRaise's left subtree
        toRaiseLeft, toRaiseRight = self.getChildren(toRaise)
        toRaiseLeftTree = self.getSubtree(toRaiseLeft)
        toRaiseRightTree = self.getSubtree(toRaiseRight)

        self.clearDescendants(toRaiseLeft, subSize=False)
        self.clearDescendants(toRaiseRight, subSize=False)

        # toRaise takes over top's spot
        self.nodes[self.getIndex(top)] = toRaise
        self.moveSubtree(self.getRightChildIndex(toRaise), toRaiseRightTree)

        # top becomes toRaise's left
        self.setLeftChild(toRaise, top)
        
        # toRaise's left becomes top's right
        self.moveSubtree(self.getRightChildIndex(top), toRaiseLeftTree)

        # move top's left subtree over
        self.moveSubtree(self.getLeftChildIndex(top), topLeftTree)

        if animation:
            self.restoreNodesPosition([toRaise] + self.getAllDescendants(toRaise), sleepTime=.05)
        
        # Return raised node to update parent
        return toRaise                                           

    def rotateRight(self, top, animation=True):
        "rotate a subtree to the right in the array and animate it"
        # the node to raise is top's left child
        toRaise = self.getLeftChild(top)

        # save top's right subtree
        topRight = self.getRightChild(top)
        topRightTree = self.getSubtree(topRight)

        # save toRaise's left and right subtree
        toRaiseLeft, toRaiseRight = self.getChildren(toRaise)
        toRaiseLeftTree = self.getSubtree(toRaiseLeft)
        toRaiseRightTree = self.getSubtree(toRaiseRight)

        self.clearDescendants(toRaiseRight, subSize=False)
        self.clearDescendants(toRaiseLeft, subSize=False)

        # toRaise takes over top's spot
        self.nodes[self.getIndex(top)] = toRaise
        self.moveSubtree(self.getLeftChildIndex(toRaise), toRaiseLeftTree)

        # top becomes toRaise's right
        self.setRightChild(toRaise, top)
        
        # toRaise's right becomes top's left
        self.moveSubtree(self.getLeftChildIndex(top), toRaiseRightTree)

        # move top's right subtree over
        self.moveSubtree(self.getRightChildIndex(top), topRightTree)

        if animation:
            self.restoreNodesPosition([toRaise] + self.getAllDescendants(toRaise), sleepTime=.05)
        # Return raised node to update parent
        return toRaise                                            

    # ----------- TESTING METHODS --------------------
   
    def inOrderTraversal(self, cur):
        if cur:
            self.inOrderTraversal(self.getLeftChild(cur))
            print(" " + str(cur), end="")
            self.inOrderTraversal(self.getRightChild(cur))

    def printTree(self, indentBy=4):
        self.__pTree(self.nodes[0], "ROOT:  ", "", indentBy)

    def __pTree(self, node, nodeType, indent, indentBy=4):
        if node:
            self.__pTree(self.getRightChild(node), "RIGHT:  ", indent + " " * indentBy, indentBy)
            print(indent + nodeType, node)
            self.__pTree(self.getLeftChild(node), "LEFT:  ", indent + " " * indentBy, indentBy)
