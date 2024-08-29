import pygame
import numpy as np


X_OFFSET = 90
Y_OFFSET = 30

CELL_SIZE = 30
BOARD_HEIGHT = 600
BOARD_WIDTH = 300

COLORS_LIST = []

COLORS = ['cyan', 'red','green','purple', 'orange', 'blue' , 'yellow']
POSITIONS = [
    [[(-2,0), (-1,0), (0,0), (1,0)], [(0,-1), (0,1), (0,0), (0,2)], [(-2,1), (-1,1), (0,1), (1,1)], [(-1,-1), (-1,0), (-1,1), (-1,2)]],  # I block
    [[(0,-1), (0,0), (1,0), (0,1)], [(-1,0), (0,0), (1,0), (0,1)], [(0,1), (0,0), (-1,0), (0,-1)], [(1,0), (0,0), (-1,0), (0,-1)]],  # T block
    [[(0,0), (0,-1), (1,-1), (-1,0)], [(0,0), (0,-1), (1,0), (1,1)], [(0,0), (1,0), (0,1), (-1,1)], [(0,0), (-1,-1), (-1,0), (0,1)]],  # S block
    [[(0,0), (-1,-1), (0,-1), (1,0)], [(0,0), (1,-1), (1,0), (0,1)], [(0,0), (-1,0), (0,1), (1,1)], [(0,0), (0,-1), (-1,0), (-1,1)]],  # Z block
    [[(0,0), (1,0), (-1,0), (1,-1)], [(0,0), (0,-1), (0,1), (1,1)], [(0,0), (-1,0), (1,0), (-1,1)], [(0,0), (0,-1), (0,1), (-1,-1)]],  # L block
    [[(0,0), (-1,-1), (-1,0), (1,0)], [(0,0), (0,-1), (1,-1), (0,1)], [(0,0), (-1,0), (1,0), (1,1)], [(0,0), (0,-1), (0,1), (-1,1)]],  # J block
    [[(0,0), (0,-1), (1,-1), (1,0)],[(0,0), (0,-1), (1,-1), (1,0)],[(0,0), (0,-1), (1,-1), (1,0)],[(0,0), (0,-1), (1,-1), (1,0)]]  # O block (only one orientation)
]



class Tetrimino:
    def __init__(self, x, y ,type_ = np.random.randint(0,7)):
        self.x = x
        self.y = y
        self.orientation = 0
        self.type = type_
        self.state = 1
        
        
                    
    
    def check_collision(self ,arr):
       
        for a, b in POSITIONS[self.type][self.orientation]:
            i = abs((self.x+a*CELL_SIZE - X_OFFSET)//CELL_SIZE)
            j = abs((self.y+b*CELL_SIZE - Y_OFFSET)//CELL_SIZE + 1)
            if j<25 and arr[j][i] != 0:
                self.state = 0
                self.place_tetrimino(arr)
                return
                
                
    def place_tetrimino(self, arr):  
        for a, b in POSITIONS[self.type][self.orientation]:
            i = abs((self.x+a*CELL_SIZE - X_OFFSET)//CELL_SIZE)
            j = abs((self.y+b*CELL_SIZE - Y_OFFSET)//CELL_SIZE)
            arr[j][i]= self.type+1

        
        
    
    def display(self, surface):
        for a, b in POSITIONS[self.type][self.orientation]:
            surface.blit(COLORS_LIST[self.type], (self.x+a*CELL_SIZE, self.y+b*CELL_SIZE))
            #pygame.draw.rect(surface, self.color, pygame.Rect(self.x+a*CELL_SIZE, self.y+b*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            
    def display_shadow(self, surface, arr):
        
        
        x_ = self.x
        y_ = self.y - CELL_SIZE
        counter = 0
        while counter<30:
            y_ +=CELL_SIZE
            counter += 1
            
            for a, b in POSITIONS[self.type][self.orientation]:
                i = abs((x_+a*CELL_SIZE - X_OFFSET)//CELL_SIZE)
                j = abs((y_+b*CELL_SIZE - Y_OFFSET)//CELL_SIZE + 1)
                if j>=0 and i>=0 and j<25 and i<10 and arr[j][i] != 0:
                    for a, b in POSITIONS[self.type][self.orientation]:
                        pygame.draw.rect(surface, COLORS[self.type], pygame.Rect(x_+a*CELL_SIZE, y_+b*CELL_SIZE, CELL_SIZE, CELL_SIZE),1)
                    return
    
    def update(self):
        self.y = ((self.y//CELL_SIZE)+1)*CELL_SIZE
    
    def change_orientation(self,arr):
        
        if(len(POSITIONS[self.type]) == self.orientation+1):
            for a, b in POSITIONS[self.type][0]:
                m = self.x + a * CELL_SIZE
                n = self.y + b * CELL_SIZE
                if m > BOARD_WIDTH + X_OFFSET - CELL_SIZE or m < X_OFFSET:
                    return
                
                i = (self.x+a*CELL_SIZE - X_OFFSET)//CELL_SIZE
                j = (self.y+b*CELL_SIZE - Y_OFFSET)//CELL_SIZE
                if arr[j][i] != 0:
                    return
            
            self.orientation = 0
        else:
            for a, b in POSITIONS[self.type][self.orientation+1]:
                m = self.x + a * CELL_SIZE
                n = self.y + b * CELL_SIZE
                
                if m > BOARD_WIDTH + X_OFFSET - CELL_SIZE or m < X_OFFSET:
                    return
                
                i = (self.x+a*CELL_SIZE - X_OFFSET)//CELL_SIZE
                j = (self.y+b*CELL_SIZE - Y_OFFSET)//CELL_SIZE
                if arr[j][i] != 0:
                    return
                
                
            self.orientation +=1
        
        
    
    def move(self, sideways=0, down=0,arr = []):
        
        if sideways == -1:
            flag = True
            for a, b in POSITIONS[self.type][self.orientation]:
                if(self.x+a*CELL_SIZE <=X_OFFSET):
                    flag = False
                    
            for a, b in POSITIONS[self.type][self.orientation]:
                i = (self.x+a*CELL_SIZE - X_OFFSET)//CELL_SIZE
                j = (self.y+b*CELL_SIZE - Y_OFFSET)//CELL_SIZE + 1
                if i-1 >= 0 and arr[j][i-1] != 0:
                        flag = False
                    
            if flag == True:        
                self.x +=sideways*CELL_SIZE
                
                
        if sideways == 1:
            flag = True
            for a, b in POSITIONS[self.type][self.orientation]:
                if(self.x+a*CELL_SIZE >= BOARD_WIDTH+X_OFFSET-CELL_SIZE ):
                    flag = False
            
            for a, b in POSITIONS[self.type][self.orientation]:
                i = (self.x+a*CELL_SIZE - X_OFFSET)//CELL_SIZE
                j = (self.y+b*CELL_SIZE - Y_OFFSET)//CELL_SIZE + 1
                if i+1 < 10 and arr[j][i+1] != 0:
                        flag = False
                    
            if flag == True:
                self.x +=sideways*CELL_SIZE
            
        self.y +=down*CELL_SIZE
        
    def slam(self,arr):
        count = 0
        while True:
            if self.state == 0:
                return count
            count +=1
            self.y += CELL_SIZE
            self.check_collision(arr)
            