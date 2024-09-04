import cv2
from math import pi, sin, ceil
from fractions import Fraction as fr
import os

#==============================================================================================================================

ascii_char_list = [' ','.',':','-','=','+','*','#','%','@'] #mutable

def getMeanOfSquare(matrix: list[list[int]], start: tuple[int], xRadius: int, yRadius: int) -> int:
    '''
    ex) start = (1,3), scale = 3
    [[(1,3),(2,3),(3,3)],
     [(1,4),(2,4),(3,4)],
     [(1,5),(2,5),(3,5)]]
    return = mean of values of matrix above
    '''
    value_list: list = []
    startX, startY = start

    w, h = getResolution(matrix)

    for y in range(startY - yRadius, startY + yRadius):
        for x in range(startX - xRadius, startX + xRadius):
            if (0 < x < w) and (0 < y < h):
                value = getValue(matrix, x, y)
                value_list.append(value)

    if len(value_list) == 0:
        mean = 0
    else:
        mean = sum(value_list) / len(value_list)

    return int(round(mean, 0))

def changeRes(matrix: list[list[int]], newWidth: int):
    xold, yold = getResolution(matrix)
    xnew = newWidth
    ynew = int(round(xnew / xold * yold, 0))
    xadder, yadder = fr(xold, xnew), fr(yold, ynew)
    xrad, yrad = ceil(round(xadder, 0)/2), ceil(round(yadder, 0)/2)
    xcur, ycur = 0, 0
    selectedx = []
    selectedy = []
    newMatrix = []

    #select centre pixels
    while ycur < yold:
        selectedy.append(round(ycur))
        ycur += yadder
    while xcur < xold:
        selectedx.append(round(xcur))
        xcur += xadder
    
    for y in selectedy:
        new_row = []
        for x in selectedx: 
            new_value = getMeanOfSquare(matrix, (x,y), xrad, yrad)
            new_row.append(new_value)
        newMatrix.append(new_row)
    
    matrix.clear()
    matrix.extend(newMatrix)

def resolutionReduction(matrix: list[list[int]], reducing_pixel) -> None:

    oldX, oldY = getResolution(matrix = matrix)
    remainY = oldY
    currentY = 0

    if (reducing_pixel > oldX) or (reducing_pixel > oldY):
        return [[0]]

    new_matrix = []
    while remainY >= reducing_pixel:
        new_row = []
        remainX = oldX
        currentX = 0

        while remainX >= reducing_pixel:
            new_value = getMeanOfSquare(matrix, (currentX, currentY), reducing_pixel, reducing_pixel)
            currentX += reducing_pixel
            remainX -= reducing_pixel
            new_row.append(new_value)

        if remainX >= (reducing_pixel / 2):
            new_value = getMeanOfSquare(matrix, (currentX, currentY), remainX, reducing_pixel)
            currentX += reducing_pixel
            remainX -= reducing_pixel
            new_row.append(new_value)

        currentY += reducing_pixel
        remainY -= reducing_pixel
        new_matrix.append(new_row)

    if remainY >= (reducing_pixel / 2):
        new_row = []
        remainX = oldX
        currentX = 0
        while remainX >= reducing_pixel:
            new_value = getMeanOfSquare(matrix, (currentX, currentY), reducing_pixel, remainY)
            currentX += reducing_pixel
            remainX -= reducing_pixel
            new_row.append(new_value)

        if remainX >= (reducing_pixel / 2):
            new_value = getMeanOfSquare(matrix, (currentX, currentY), remainX, remainY)
            currentX += reducing_pixel
            remainX -= reducing_pixel
            new_row.append(new_value)

        currentY += reducing_pixel
        remainY -= reducing_pixel
        new_matrix.append(new_row)
    
    matrix.clear()
    matrix.extend(new_matrix)

def grayscaleToAsciiscale(grayscale: int, ascii_index: int) -> int: #grayscale: 0~255 -> Asciiscale: 0~ascii_index
    if (grayscale >= 0) and (grayscale <= 255):
        asciiscale = int(round(grayscale * ascii_index / 255, 0))
    elif grayscale < 0: #exception 1
        asciiscale = 0
    elif grayscale > 255: #exception 2
        asciiscale = ascii_index
    return asciiscale

def grayImageToAsciiImage(matrix: list[list[int]], ascii_char_list: list[str]) -> None:
    
    ascii_index = len(ascii_char_list) - 1

    Xres, Yres = getResolution(matrix = matrix)
    for y in range(Yres):
        for x in range(Xres):
            matrix[y][x] = grayscaleToAsciiscale(matrix[y][x], ascii_index)

def getResolution(matrix: list[list[int]]) -> tuple[int]:
    Xlength = len(matrix[0])
    Ylength = len(matrix)
    return Xlength, Ylength

def getValue(matrix: list[list[int]], x: int, y: int) -> int:
    return matrix[y][x]

class Screen:

    def __init__(self, matrix: list[list[int]], ascii_char_list: list[str]) -> None:
        self.matrix = matrix
        self.ascii_char_list = ascii_char_list
        self.ascii_index = len(ascii_char_list) - 1

    def getString(self) -> str:
        temp_string = ''
        for row in self.matrix:
            for ascii_scale in row:
                temp_string += self.ascii_char_list[ascii_scale] + ' '
            temp_string += '\n'
        temp_string.rstrip('\n')
        return temp_string

    def __str__(self) -> str:
        return self.getString()

    def updateScreen(self, matrix: list[list[int]]) -> None:
        '''
        Update self.matrix to the given matrix when the size of both matrix is the same.
        '''
        self.matrix = matrix

    def reverseContrast(self) -> None:
        '''
        mutate the given screen
        '''
        Xres, Yres = getResolution(self.matrix)
        for y in range(Yres):
            for x in range(Xres):
                self.matrix[y][x] = self.ascii_index - self.matrix[y][x]

    def contrastEnhancement(self, multiplier: float = 100, factor: int = 1) -> None:
        '''
        mutate the given screen
        '''
        matrix = self.matrix
        k = multiplier / 100
        c = self.ascii_index/(2*pi)

        def f(x):
            y = x -  c*k*sin(x/c)
            return round(y)
        
        Xres, Yres = getResolution(matrix = matrix)
        for y in range(Yres):
            for x in range(Xres):
                for t in range(factor):
                    matrix[y][x] = f(matrix[y][x])

    def createTextFile(self, file_name: str, path_dl: str = ".\\") -> str:
    #def createTextFile(self, file_name: str) -> str:
        file_num = 0
        saved = False

        #path_dl = ".\\"

        while not saved:
            new_file_name = f'{file_name}-{file_num}.txt'
            path_file = f'{path_dl}\\{new_file_name}'
            try:
                txt_file = open(path_file,'x')
            except:
                file_num += 1
            else:
                txt_file.close()
                txt_file = open(path_file, 'w')
                txt_file.write(str(self))
                saved = True
                txt_file.close()

        print(f'image saved as {new_file_name}')
        return new_file_name

    def createTextFileAndRun(self, file_name: str) -> None:
        path = self.createTextFile(file_name)
        os.system(path)

def convertImageToAsciiArt(path_img: str, newWidth: int = 200, contrast_factor: int = 0, reverse: bool = False, ascii_char_list: list[str] = [' ']) -> Screen | None:
    
    image = cv2.imread(path_img, 0) # 0 : IMREAD_GRAYSCALE

    image_matrix = list(image)
    for y in range(len(image_matrix)):
        image_matrix[y] = list(image_matrix[y]) #change type of row of matrix from <class 'numpy.ndarray'> to <class 'list'>
        for x in range(len(image_matrix[y])):
            image_matrix[y][x] = int(image_matrix[y][x]) #change type of element of matrix from <class 'numpy.uint8'> to <class 'int'>

    temp = image_matrix[:]

    oldxRes = getResolution(image_matrix)[0]

    if newWidth != oldxRes:
        changeRes(temp, newWidth = newWidth)
    grayImageToAsciiImage(temp, ascii_char_list)
    ascii_image_matrix = temp

    screen = Screen(ascii_image_matrix, ascii_char_list)

    if contrast_factor != 0:
        screen.contrastEnhancement(factor = contrast_factor)

    if reverse:
        screen.reverseContrast()
    
    return screen

#==============================================================================================================================

if __name__ == '__main__':
    ascii_char_list_1 = [' ', '.', "'", '`', '^', '"', ',', ':', ';', 'I', 'l', '!', 'i', '>', '<', '~', '+', '_', '-', '?', ']', '[', '}', '{', '1', ')', '(', '|', '\\', '/', 't', 'f', 'j', 'r', 'x', 'n', 'u', 'v', 'c', 'z', 'X', 'Y', 'U', 'J', 'C', 'L', 'Q', '0', 'O', 'Z', 'm', 'w', 'q', 'p', 'd', 'b', 'k', 'h', 'a', 'o', '*', '#', 'M', 'W', '&', '8', '%', 'B', '@', '$'] #ver.1 
    ascii_char_list_2 = [' ','.',':','-','=','+','*','#','%','@']
    ascii_char_list_3 = [' ','=','@']

    path = "C:\\Users\\ychn0\\Downloads\\1330715.png"
    newxRes = 300
    contrast_factor = 1

    screen = convertImageToAsciiArt(path_img = path, newWidth= newxRes, contrast_factor = contrast_factor, ascii_char_list = ascii_char_list_2)
    screen.createTextFileAndRun('my_art')