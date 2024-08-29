
import copy
import pygame
import numpy as np
import pygame
from tetrimino import *
import copy
import random
import pickle


class Neural_network:
    def __init__(self,input_size, layers_data, activation: str = "tanh") -> None:
        
        self.layers = []
        self.activation = activation
        
        for i in range( len(layers_data) ):
            self.layers.append(self.create_layer(input_size, layers_data[i]))
            input_size = layers_data[i]
    
    def relu(self, x):
        return x * (x > 0)
            
    def predict(self, input_data ):
        
        y = input_data.T
                
        for i in range(0, len(self.layers)-1):
            y = np.dot(self.layers[i], y)
            y = np.tanh(y)
        
        y = np.dot(self.layers[-1], y)
        
        return y.reshape(-1)
    
    
    def create_layer(self, input_size, neurons):
        
        weights = np.random.uniform(0.0 , 5.0 ,(neurons,input_size))
        
        return weights
        
        

class AI:
    def __init__(self) -> None:
        self.nn_list = []
        self.population_size = 50
        self.population_iterator = 0
        self.generation_count = 0
        self.highest_score = 0
        self.grid_temp = []
        self.block_data = []
        self.input_data = []
        self.output_data = []
        self.gn = Genetic_algorithm(self.population_size) 
        
        for _ in range(self.population_size):
            model = {"nn": Neural_network(4, [8, 1] ), "score": 0 }
            self.nn_list.append(model)
    
    def save_best_performer(self):
        
        with open('best-weights.pickle', 'wb') as handle:
            pickle.dump([self.nn_list[self.population_iterator]], handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    def load_best_performer(self):
        try:
            with open('best-weights.pickle', 'rb') as handle:
                self.nn_list = pickle.load(handle)
                self.population_size = 1
        except:
            print("File not found!!")
    
    def save_weights(self):
        with open('weights.pickle', 'wb') as handle:
            pickle.dump(self.nn_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        with open('gen-count.pickle', 'wb') as handle2:
            pickle.dump(self.generation_count, handle2, protocol=pickle.HIGHEST_PROTOCOL)
            
        with open('highest_score.pickle', 'wb') as handle3:
            pickle.dump(self.highest_score, handle3, protocol=pickle.HIGHEST_PROTOCOL)
        
    def load_weights(self):
        self.population_size = 50
        try:
            with open('weights.pickle', 'rb') as handle:
                self.nn_list = pickle.load(handle)
            with open('gen-count.pickle', 'rb') as handle2:
                self.generation_count = pickle.load(handle2)
            with open('gen-highest_score.pickle', 'rb') as handle2:
                self.highest_score = pickle.load(handle2)
        except:
            for _ in range(self.population_size):
                model = {"nn": Neural_network(4, [8, 1] ), "score": 0 }
                self.nn_list.append(model)
    
    
    def display(self, surface):## display inputs to neural net
        y = 5
        font = pygame.font.SysFont("Arial", 12)
        for i ,data in enumerate(self.input_data):
            
            txtsurf = font.render(f"{data[0]:.2f}, {data[1]:.2f}, {data[2]:.2f}, {data[3]:.2f} = {self.output_data[i]:.2f} ", True, (255,255,255))
            surface.blit(txtsurf,(630,y))
            y += 12
            
    def set_score(self, score):
        self.nn_list[self.population_iterator]['score'] = score
        
    def find_col_heights(self,grid):
        heights = []
        
        for i in range(10):
            j = 0
            while j<25:
                if grid[j][i] != 0:
                    heights.append(24 - j)
                    break
                j += 1
        
        return np.array(heights)

    def find_sum_height_valleys(self,heights):

        return np.sum( (np.max(heights) - heights)>3 )*1.0
    
    
    def find_bumpiness(self, heights):
        
        differences = [abs(heights[i] - heights[i + 1]) for i in range(len(heights) - 1)]
    
        return sum(differences)*1.0

    
    def find_inplace_height(self, block_cords):
        
        max_height = 0
        
        for i , j in block_cords:
            max_height = max(max_height, i)
        
        return 24 - max_height
        
    
    def create_new_grid(self, grid, block_cords):
        grid_copy = copy.deepcopy(grid)

        
        for cords in block_cords:
            i = cords[0]
            j = cords[1]
            grid_copy[i][j] = 1

        return grid_copy
    
    def find_lines_cleared(self, new_grid, set_rows):

        
        line_counts = 0    
        for i in set_rows:

            found_line = True
            
            for j in range(10):
                if new_grid[i][j] == 0:
                    found_line = False
                    break
                    
            if found_line == True:
                line_counts += 1
        
        return line_counts
        

    def find_holes_created(self, new_grid, block_cords):
        hole_count = 0
        
        uniq = {}
        
        for i , j in block_cords:
            if j not in uniq:
                uniq[j] = i
            else:
                uniq[j] = max(uniq[j], i)
        
        #print(block_cords ,uniq )
        for key in uniq:
            row = uniq[key]
            cap = 0
            while cap < 5 and row<25 :
                if new_grid[row][key] == 0:
                    hole_count +=1
                
                row +=1
                cap +=1
            
            
        return hole_count
    
    def execute_genetic_algorithm(self):
        self.nn_list = self.gn.selection(self.nn_list)
        self.generation_count += 1
        self.population_iterator = 0
        
    
    def best_move(self, tetrimino_type, orientaions , grid):

        
        input_data = []
        move_data = []
        col_data = []
        orientation_data = []
        
        for o, orientation in enumerate(orientaions[tetrimino_type]):
            
            for j in range(10):
                
                valid , new_cords = self.find_move(orientation, grid, j)
                
                if valid:
                    new_grid = self.create_new_grid(grid, new_cords)
                    heights = self.find_col_heights(new_grid)
                    valleys = self.find_sum_height_valleys(heights)
                    bumpiness = self.find_bumpiness(heights)
                    holes_counts = self.find_holes_created(new_grid, new_cords)*1.0
                    height = self.find_inplace_height(new_cords)*1.0
                    col_data.append(j)
                    orientation_data.append(o)
                    move_data.append(new_cords)

                    input_data.append([valleys, bumpiness, holes_counts, height])
                    
        input_data = np.array(input_data)
        #standardize
        for i in range(0,input_data.shape[1]):
            std = np.std(input_data[:, i])
            mu = np.mean(input_data[:, i])
            for j in range(input_data.shape[0]):
                input_data[j][i] = ((input_data[j][i] - mu )/std)  if std !=0 else 0
                
        #normalization
        # for i in range(0,input_data.shape[1]):
        #     minn = np.min(input_data[:, i])
        #     maxx = np.max(input_data[:, i])
        #     for j in range(input_data.shape[0]):
        #         input_data[j][i] = ((input_data[j][i] - minn )/(maxx-minn))  if maxx-minn !=0 else 0
        
        self.input_data = input_data
        #self.block_data = move_data
        
        ## prediction
        
        model = self.nn_list[self.population_iterator]['nn']
        prediction = model.predict( input_data )
        self.output_data = prediction
        min_value = np.min(prediction)
        best_index = np.argmin(prediction)
        best_orientation  = orientation_data[best_index]
        
        return best_orientation , move_data[best_index], min_value
        
                
                        
    def find_move(self,ori, grid, j):
        
        
        valid = True
        
        for m, n in ori:
            if j+m < 0 or j+m >= 10:
                valid = False
                break
            
        row = 4
        if valid:
            while row < 25:
                row += 1
                for m, n in ori:
                    if row+n+1 >= 25 or row+n < 4 or grid[row+n+1][m+j] != 0:
                        new_cords = [ (row+n, j+m) for m , n in ori ]
                        return True, new_cords
                    
                
              
        return False , None
        
                          
                    
class Genetic_algorithm:
    
    def __init__(self, population_size) -> None:
        self.population_size = population_size
    
    def selection(self, nn_list):
        sorted_list = sorted(nn_list ,key = lambda x : x['score'], reverse=True)
        sorted_list = sorted_list[: int(self.population_size * 0.20)  ]
        
        new_population = [ self.crossover(random.choice(sorted_list), random.choice(sorted_list))  for _ in range(self.population_size)   ]
        return new_population

    
    def crossover(self,p1, p2):
        p1_copy = copy.deepcopy(p1)
        
        for i in range(len(p1['nn'].layers)):
            
            split = np.random.randint(0, p2["nn"].layers[i].shape[1] )
            #print(split)
            p1_copy["nn"].layers[i][:,:split] = p2["nn"].layers[i][:,: split]
        
        return self.mutation(p1_copy)
    
    def mutation(self,child):
        if np.random.randint(0,7) == 1:
            for i in range(len(child['nn'].layers)):
                if np.random.randint(0,2) == 1:
                    row = np.random.randint(0, child['nn'].layers[i].shape[0] )
                    col = np.random.randint(0, child['nn'].layers[i].shape[1] )
                    child['nn'].layers[i][row][col] = np.random.uniform(-0.5,0.5)
                    #print("pass")
        return child
            