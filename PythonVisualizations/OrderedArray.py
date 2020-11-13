import random
from tkinter import *

try:
    from drawable import *
    from VisualizationApp import *
    from SortingBase import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *
    from .SortingBase import *

class OrderedArray(SortingBase):

    def __init__(self, title="Ordered Array", **kwargs):
        super().__init__(title=title, **kwargs)

        # Fill in initial array values with random but ordered integers
        # The display items representing these array cells are created later
        for i in sorted([random.randrange(self.valMax) 
                         for i in range(self.size-1)]):
            self.list.append(drawable(i))
        
        self.display()

        self.buttons = self.makeButtons()

    # ARRAY FUNCTIONALITY

    insertCode = '''
def insert(self, item={val}):
   if self.__nItems >= len(self.__a):
      raise Exception("Array overflow")

   j = self.__nItems
   while 0 < j and self.__a[j - 1] > item:
      self.__a[j] = self.__a[j-1]
      j -= 1

   self.__a[j] = item
   self.__nItems += 1
'''

    def insert(self, val, code=insertCode):
        canvasDims = self.widgetDimensions(self.canvas)
        
        self.startAnimations()
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))

        self.highlightCode('self.__nItems >= len(self.__a)', 
                           callEnviron, wait=0.1)
        if len(self.list) >= self.size:
            self.highlightCode(
                'raise Exception("Array overflow")', callEnviron, wait=0.2,
                color=self.EXCEPTION_HIGHLIGHT)
            self.cleanUp(callEnviron)
            return

        self.highlightCode('j = self.__nItems', callEnviron, wait=0.1)
        j = len(self.list)
        indexJ = self.createIndex(j, 'j')
        callEnviron |= set(indexJ)

        startPosition = self.tempCoords(j)
        cell = self.createCellValue(startPosition, val)
        if cell[1] is None:
            cell = cell[:1]
        itemLabel = self.canavas.create_text(
            *self.tempLabelCoords(j, self.VARIABLE_FONT), text='item', 
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        newItem = cell + (itemLabel,)
        callEnviron += set(newItem)
        
        self.list.append(drawable(None))
        self.highlightCode('0 < j and self.__a[j - 1] > item', callEnviron)
        
        #  Move bigger items right
        while 0 < j and self.list[j-1].val > val:
            self.wait(0.1) # Pause to compare values

            self.highlightCode('self.__a[j] = self.__a[j-1]', callEnviron)
            self.assignElement(j - 1, j, callEnviron, sleepTime=0.01)
            
            self.highlightCode('j -= 1', callEnviron)
            self.moveItemsBy((indexJ,) + newItem, (-self.CELL_WIDTH, 0), 
                             sleepTime=0.01)
            
        self.wait(0.1) # Pause for last loop comparison
        
        self.highlightCode('self.__a[j] = item', callEnviron, wait=0.1)
        
        # Move the new cell into the array
        toPositions = (self.cellCoords(j),)
        if len(cell) > 1:
            toPositions += (self.cellCenter(j),)
        self.moveItemsTo(cell, toPositions, sleepTime=0.01)

        self.canvas.delete(self.list[j].display_shape) # Delete items covered
        if self.list[j].display_val:   # by the new item
            self.canvas.delete(self.list[j].display_val)
        self.list[k] = drawable(
            val, self.canvas.itemconfigure(cell[0], 'fill')[-1], *cell)
        callEnviron ^= set(cell)  # New item is no longer temporary
        
        # Move nItems pointer
        self.highlightCode('self.__nItems += 1', callEnviron)
        self.moveItemsBy(self.nItems, (self.CELL_WIDTH, 0))
        self.wait(0.1)        

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron) 

    findCode = '''
def find(self, item={val}):
   lo = 0
   hi = self.__nItems-1
   
   while lo <= hi:
      mid = (lo + hi) // 2
      if self.__a[mid] == item:
         return mid
      elif self.__a[mid] < item:
         lo = mid + 1
      else: 
         hi = mid - 1
         
   return lo
'''
    
    def find(self, val, code=findCode):
        callEnviron = self.createCallEnvironment(code=code.format(**locals()))
        self.startAnimations()

        self.highlightCode('lo = 0', callEnviron)
        lo = 0
        loIndex = self.createIndex(lo, 'lo', level=1)
        callEnviron |= set(loIndex)
        self.wait(0.1)

        self.highlightCode('hi = self.__nItems-1', callEnviron)
        hi = len(self.list) - 1
        hiIndex = self.createIndex(hi, 'hi', level=3)
        callEnviron |= set(hiIndex)
        self.wait(0.1)

        midIndex = None

        while lo <= hi:
            self.highlightCode('lo <= hi', callEnviron, wait=0.1)

            self.highlightCode('mid = (lo + hi) // 2', callEnviron)
            mid = (lo + hi) // 2
            if midIndex:
                midCoords = self.indexCoords(mid, level=2)
                self.moveItemsTo(midIndex, (midCoords, midCoords[:2]),
                                 sleepTime=0.01)
            else:
                midIndex = self.createIndex(mid, 'mid', level=2)
                self.wait(0.1)
                
            self.highlightCode('self.__a[mid] == item', callEnviron, wait=0.1)
            if self.list[mid].val == val:
                callEnviron.add(self.createFoundCircle(mid))
                self.highlightCode('return mid', callEnviron, wait=0.1)
                self.cleanUp(callEnviron)
                return mid

            self.highlightCode('self.__a[mid] < item', callEnviron, wait=0.1)
            if self.list[mid].val < val:
                self.highlightCode('lo = mid + 1', callEnviron)
                lo = mid + 1
                loCoords = self.indexCoords(lo, level=1)
                self.moveItemsTo(loIndex, (loCoords, loCoords[:2]),
                                 sleepTime=0.01)
            else:
                self.highlightCode('hi = mid - 1', callEnviron)
                hi = mid - 1
                hiCoords = self.indexCoords(hi, level=3)
                self.moveItemsTo(hiIndex, (hiCoords, hiCoords[:2]),
                                 sleepTime=0.01)
                
        self.wait(0.1)        # Pause for final loop comparison
        self.highlightCode('return lo', callEnviron)
        self.cleanUp(callEnviron)
        return lo

    def removeFromEnd(self):
        
        # pop a Drawable from the list
        if len(self.list) == 0:
            self.setMessage('Array is empty!')
            return
        callEnviron = self.createCallEnvironment()         
        
        self.startAnimations()  
   
        #move nItems pointer
        self.moveItemsBy(self.nItems, (-self.CELL_SIZE, 0))
        
        n = self.list.pop()

        # delete the associated display objects

        items = (n.display_shape, n.display_val)
        callEnviron |= set(items)
        self.moveItemsOffCanvas(items, N, sleepTime=0.02)

        # Clean up animations
        self.cleanUp(callEnviron)
        
    def assignElement(
            self, fromIndex, toIndex, callEnviron,
            steps=CELL_SIZE // 2, sleepTime=0.01):
        fromDrawable = self.list[fromIndex]

        # get positions of "to" cell in array
        toPositions = (self.cellCoords(toIndex), self.cellCenter(toIndex))

        # create new display objects as copies of the "from" cell and value
        newCell = self.copyCanvasItem(fromDrawable.display_shape)
        newCellVal = self.copyCanvasItem(fromDrawable.display_val)
        callEnviron |= set([newCell, newCellVal])

        # Move copies to the desired location
        self.moveItemsTo((newCell, newCellVal), toPositions, steps=steps,
                         sleepTime=sleepTime)

        # delete the original "to" display value and the new display shape
        self.canvas.delete(self.list[toIndex].display_val)
        self.canvas.delete(self.list[toIndex].display_shape)

        # update value and display value in "to" position in the list
        self.list[toIndex].display_val = newCellVal
        self.list[toIndex].val = self.list[fromIndex].val
        self.list[toIndex].display_shape = newCell
        self.list[toIndex].color = self.list[fromIndex].color
        callEnviron ^= set([newCell, newCellVal])

        # update the window
        self.window.update()

    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return (self.ARRAY_X0 + self.CELL_SIZE * cell_index, self.ARRAY_Y0,  # at index
                self.ARRAY_X0 + self.CELL_SIZE * (cell_index + 1) - self.CELL_BORDER,
                self.ARRAY_Y0 + self.CELL_SIZE - self.CELL_BORDER)

    def cellCenter(self, index):  # Center point for array cell at index
        half_cell = (self.CELL_SIZE - self.CELL_BORDER) // 2
        return add_vector(self.cellCoords(index), (half_cell, half_cell))

    def createArrayCell(self, index):  # Create a box representing an array cell
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        rect = self.canvas.create_rectangle(
            *add_vector(cell_coords,
                        (-half_border, -half_border,
                         self.CELL_BORDER - half_border, self.CELL_BORDER - half_border)),
            fill=None, outline=self.CELL_BORDER_COLOR, width=self.CELL_BORDER)
        self.canvas.lower(rect)
        return rect

    def createCellValue(self, indexOrCoords, key, color=None):
        """Create new canvas items to represent a cell value.  A square
        is created filled with a particular color with an text key centered
        inside.  The position of the cell can either be an integer index in
        the Array or the bounding box coordinates of the square.  If color
        is not supplied, the next color in the palette is used.
        An event handler is set up to update the VisualizationApp argument
        with the cell's value if clicked with any button.
        Returns the tuple, (square, text), of canvas items
        """
        # Determine position and color of cell
        if isinstance(indexOrCoords, int):
            rectPos = self.cellCoords(indexOrCoords)
            valPos = self.cellCenter(indexOrCoords)
        else:
            rectPos = indexOrCoords
            valPos = divide_vector(add_vector(rectPos[:2], rectPos[2:]), 2)
        if color is None:
            # Take the next color from the palette
            color = drawable.palette[OrderedArray.nextColor]
            OrderedArray.nextColor = (OrderedArray.nextColor + 1) % len(drawable.palette)

        cell_rect = self.canvas.create_rectangle(
            *rectPos, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=str(key), font=self.VALUE_FONT, fill=self.VALUE_COLOR)
        handler = lambda e: self.setArgument(str(key))
        for item in (cell_rect, cell_val):
            self.canvas.tag_bind(item, '<Button>', handler)

        return cell_rect, cell_val

    def display(self):
        self.canvas.delete("all")

        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)
        
        # draw an index pointing to the last item in the list
        self.nItems = self.createIndex(len(self.list), "nItems", level = -1, color = 'black')

        # go through each Drawable in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated Drawables
            n.display_shape, n.display_val = self.createCellValue(
                i, n.val, n.color)

            n.color = self.canvas.itemconfigure(n.display_shape, 'fill')[-1]

        self.window.update()

    def randomFill(self):
        callEnviron = self.createCallEnvironment()        
        # Clear the list so new values can be entered
        self.list=[] 
        size = self.size
        
        # Create a list of random numbers and sort them
        a = [random.randrange(90) for i in range(size)]
        a.sort()
        
        # Append and draw them to the list and draw them
        for i in a:
            self.list.append(drawable(i))
        self.display()            
        self.cleanUp(callEnviron)
        
    def newArraySize(self, val):
        callEnviron = self.createCallEnvironment()  
        # Clear Array and reset size and list
        self.canvas.delete("all")
        self.size = val
        self.list = []
        self.display()
        
        self.cleanUp(callEnviron)
        
    def search(self, val):

        callEnviron = self.createCallEnvironment()
        self.startAnimations()
       
        lo = 0                             #Point to lo
        indexLo = self.createIndex(lo, 'lo',level= 1)
        callEnviron |= set(indexLo)
        hi = len(self.list)-1              # Point to hi
        indexHi = self.createIndex(hi, 'hi', level = 3)
        callEnviron |= set(indexHi)
        mid = (lo + hi) // 2               # Point to the midpoint
        indexMid = self.createIndex(mid, 'mid', level = 2)
        callEnviron |= set(indexMid)            
        while lo <= hi:
            mid = (lo + hi) // 2           # Select the midpoint
            if self.list[mid].val == val:  # Did we find it at midpoint?  
                posShape = self.canvas.coords(self.list[mid].display_shape)

                # Highlight the found element with a circle
                foundCircle = self.canvas.create_oval(
                    *add_vector(
                        posShape,
                        (self.CELL_BORDER, self.CELL_BORDER, -self.CELL_BORDER, -self.CELL_BORDER)),
                    outline=self.FOUND_COLOR)
                callEnviron.add(foundCircle) 
                
                self.wait(0.3)

                self.cleanUp(callEnviron)
                return mid                 # Return the value found 
        
            elif self.list[mid].val < val: # Is item in upper half?
                deltaXLo = (mid - lo) + 1
                self.moveItemsBy(indexLo, (self.CELL_SIZE*deltaXLo, 0))
                lo = mid + 1               # Yes, raise the lo boundary
                deltaXMid = ((hi - lo) // 2) + 1
                self.moveItemsBy(indexMid, (self.CELL_SIZE*deltaXMid, 0))
               
            else:                         # Is item in lower half? 
                deltaXHi = (mid -hi) - 1 
                self.moveItemsBy(indexHi, (self.CELL_SIZE*deltaXHi, 0))
                hi = mid - 1              # Yes, lower the hi boundary 
                deltaXMid = ((lo- hi) //2) -1
                self.moveItemsBy(indexMid, (self.CELL_SIZE* deltaXMid, 0))
        
        self.cleanUp(callEnviron)
        return lo                         #val not found 
    
            
    def remove(self, val):
        callEnviron = self.createCallEnvironment()         
    
        self.startAnimations()
        index = self.search(val)
        
        found = self.list[index].val == val
        if found:    # Record if value was found
            n = self.list[index]

            # Slide value rectangle up and off screen
            items = (n.display_shape, n.display_val)
            self.moveItemsOffCanvas(items, N, sleepTime=0.01)
            callEnviron |= set(items)

            #decrement nItems pointer  
            self.moveItemsBy(self.nItems, (-self.CELL_SIZE, 0), sleepTime=0.01)
            
            # Create an index for shifting the cells
            kIndex = self.createIndex(index, 'k', level = -2)
            callEnviron |= set(kIndex)
            
            # Slide values from right to left to fill gap
            for i in range(index+1, len(self.list)):
                self.assignElement(i, i - 1, callEnviron)
                self.moveItemsBy(kIndex, (self.CELL_SIZE, 0), sleepTime=0.01)
    
            # delete the last, duplicate cell from the list and as a drawable 
            n = self.list.pop()
            self.canvas.delete(n.display_shape)
            self.canvas.delete(n.display_val)     

        self.cleanUp(callEnviron)
        return found
        
    def fixCells(self):       # Move canvas display items to exact cell coords
        for i, drawItem in enumerate(self.list):
            self.canvas.coords(drawItem.display_shape, *self.cellCoords(i))
            self.canvas.coords(drawItem.display_val, *self.cellCenter(i))
        self.window.update()

    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        self.fixCells()       # Restore cells to their coordinates in array


    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        newSizeArrayButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1, validationCmd=vcmd)        
        searchButton = self.addOperation(
            "Search", lambda: self.clickSearch(), numArguments=1, validationCmd=vcmd)
        randomFillButton = self.addOperation(
            "Random Fill", lambda: self.randomFill())        
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1, validationCmd=vcmd)
        deleteValueButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1, validationCmd=vcmd)
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", lambda: self.removeFromEnd())
        #this makes the pause, play and stop buttons 
        self.addAnimationButtons()
        return [searchButton, insertButton, deleteValueButton, newSizeArrayButton, randomFillButton,
                deleteRightmostButton]

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val
            
    # Button functions
    def clickSearch(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        elif len(self.list) == 0: 
            self.setMessage("The array is empty.")
        else:
            result = self.search(val)
            if self.list[result].val == val:
                msg = "Found {}!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()

    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            result = self.insert(val)
            self.setMessage("Value {} inserted".format(val) if result else
                            "Array overflow")
        self.clearArgument()

    def clickDelete(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            result = self.remove(val)
            if result:
                msg = "Value {} deleted!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()
    
    def clickNew(self):
        val = self.validArgument()
        # If the number of cells desired wouldn't fit on the screen, error message
        if val is None or self.window.winfo_width() <= self.ARRAY_X0 + (val+1) * self.CELL_SIZE:
            self.setMessage("This array size is too big to display")    
        elif val == 0:
            self.setMessage("This array size is too small")                
        else:
            self.newArraySize(val)        
        self.clearArgument()    

if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    array = OrderedArray()

    array.runVisualization()

