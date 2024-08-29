import pygame
import sys
from tetrimino import *
from ai import * 



class Board:
    def __init__(self) -> None:
        self.grid = np.zeros((25,10))
        self.game_over = False
                
        for i in range(10):
            self.grid[-1][i] = 1
        
        
    def check_clear(self):
        
        line_count = 0
        for i in range(0,len(self.grid)-1):
            flag = "tetris"
            for j in range(len(self.grid[0])):
                if self.grid[i][j] == 0:
                    flag = "not_tetris"
            
            if flag == "tetris":
                line_count +=1
                first_row = np.zeros((10)).reshape(-1,10)
                new_grid = np.delete(self.grid , [i], axis = 0)
                self.grid = np.concatenate((first_row, new_grid),axis=0).reshape(25,10)
        
        return line_count

    def check_spawn_safe(self):

        for j in range(8):
            for i in range(10):
                if self.grid[j][i] != 0:
                    return j
        
        return 8

    def check_game_over(self):
        for i in range(10):
            if self.grid[4][i] != 0:
                self.game_over = True
                return
    
    def display(self,surface):
        for i in range(4,len(self.grid)-1):
            for j in range(len(self.grid[0])):
                if self.grid[i][j] != 0:
                    #pygame.draw.rect(surface, COLORS[int(self.grid[i][j]-1)], pygame.Rect( j * CELL_SIZE + X_OFFSET , i * CELL_SIZE + Y_OFFSET , CELL_SIZE, CELL_SIZE))
                    surface.blit(COLORS_LIST[int(self.grid[i][j]-1)], (j * CELL_SIZE + X_OFFSET , i * CELL_SIZE + Y_OFFSET))
                    #pygame.draw.rect(surface, "lime", pygame.Rect( j * CELL_SIZE + X_OFFSET , i * CELL_SIZE + 6  0 , CELL_SIZE, CELL_SIZE),1)

class Score:
    def __init__(self) -> None:
        self.score = 0
        
    
    def display(self,surface,x,y):
        font = pygame.font.SysFont("Arial", 36)
        txtsurf = font.render(f"Score: {self.score}", True, (255,255,255))
        surface.blit(txtsurf,(x,y))
        
    def update_score_on_lines(self, level, lines):
        if lines == 1:
            self.score += 40 * (level + 1)
        elif lines == 2:
            self.score += 100 * (level + 1)
        elif lines == 3:
            self.score += 300 * (level + 1)
        elif lines == 4:
            self.score += 1200 * (level + 1)
    
    def update_score_on_moves(self, i):
        self.score += i
        

class Game:
    def __init__(self):
        self.WINDOW_HEIGHT = 800
        self.WINDOW_WIDTH = 800
        
        self.tetrimino_spawn = (210, 0)
        self.high_score_tracker = 0
        self.avg_score_tracker = 0
        self.highest_level_tracker = 0
        
        self.play_state = 3
        self.game_state = 0

        self.fall_time = 0
        self.fall_speed = 0.5
        self.level = 0
        self.lines_cleared = 0 #to increase level every 10 lines cleared
        self.move_counter = 0
        self.tetrimino = Tetrimino(self.tetrimino_spawn[0],self.tetrimino_spawn[1],type_ = np.random.randint(0,7))
        self.tetrimino.state = 0
        self.next_tetrimino = Tetrimino(BOARD_WIDTH+ CELL_SIZE*2 + X_OFFSET, BOARD_HEIGHT//2,type_ = np.random.randint(0,7))
        self.hold_tetrimino = None
        
        self.board = Board()
        self.score = Score()
        self.ai = AI()
    
    def restart_game(self):
        self.tetrimino = Tetrimino(self.tetrimino_spawn[0],self.tetrimino_spawn[1],type_ = np.random.randint(0,7))
        self.tetrimino.state = 0
        self.next_tetrimino = Tetrimino(BOARD_WIDTH+ CELL_SIZE*2 + X_OFFSET, BOARD_HEIGHT//2,type_ = np.random.randint(0,7))
        
        self.board = Board()
        self.score = Score()
        self.fall_time = 0
        self.fall_speed = 0.5
        self.lines_cleared = 0
        self.game_state = 1
        self.level = 0
        self.hold_tetrimino = None
        self.hold_piece_switch = 0
        
    
    def display_text(self, surface, text, x, y, color = 'white' ,size = 15):    
        font = pygame.font.SysFont("Arial", size)
        txtsurf = font.render(text, True, color)
        surface.blit(txtsurf,(x,y))
    
    def ai_playing(self,best_orient, target_cords):
        
        cap = 0
        while best_orient != self.tetrimino.orientation and cap <= 4:
                cap += 1
                self.tetrimino.change_orientation(self.board.grid)
                
        x_pos , y_pos = POSITIONS[self.tetrimino.type][self.tetrimino.orientation][0]
        target_x = target_cords[0][1]*CELL_SIZE + X_OFFSET
        
        cur_x = self.tetrimino.x + x_pos*CELL_SIZE
        
        
        if cur_x != target_x:
                self.move_counter += 1
                if cur_x < target_x:
                    self.tetrimino.move(1,0, self.board.grid)
                elif cur_x > target_x:
                    self.tetrimino.move(-1,0, self.board.grid)
                    
        if (cur_x == target_x and best_orient == self.tetrimino.orientation) or self.move_counter == 7:
            self.move_counter = 0
            self.score.update_score_on_moves( self.tetrimino.slam(self.board.grid) )
    
    
    def switch_hold(self):
        
        if self.hold_tetrimino is None:
            self.hold_tetrimino = Tetrimino(BOARD_WIDTH+ CELL_SIZE*4 + X_OFFSET, 9*CELL_SIZE, self.tetrimino.type)
            self.tetrimino = Tetrimino(self.tetrimino_spawn[0],self.tetrimino_spawn[1],type_ = self.next_tetrimino.type)
            self.next_tetrimino = Tetrimino(BOARD_WIDTH+ CELL_SIZE*4 + X_OFFSET, 3*CELL_SIZE,type_ = np.random.randint(0,7) )
            safe = self.board.check_spawn_safe()
                    
            for _ in range(safe-2):
                self.tetrimino.update()
                                                              
        elif self.hold_piece_switch == 0:
            temp = self.hold_tetrimino.type
            self.hold_tetrimino.type = self.tetrimino.type
            self.tetrimino.type = temp
            self.tetrimino.x, self.tetrimino.y = self.tetrimino_spawn
            safe = self.board.check_spawn_safe()
                    
            for _ in range(safe-2):
                self.tetrimino.update()
        
        self.hold_piece_switch = 1
        
        
    def main(self):
        pygame.init()
        clock = pygame.time.Clock()
        
        pygame.display.set_caption('Tetris')
        font = pygame.font.SysFont("Arial", 36)
        surface = pygame.display.set_mode((self.WINDOW_WIDTH,self.WINDOW_HEIGHT))

        

        #self.ai.load_weights()
        self.ai.load_best_performer()
        best_orient = target_cords = best_orient_H = target_cords_H = None
        
        for c in COLORS:
            img = pygame.image.load(f'assets/{c}.png').convert()
            img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            COLORS_LIST.append(img)
        

        while True:

            if self.game_state == 0:
                self.display_text(surface, "Press 's' to start !!",self.WINDOW_WIDTH//2 , self.WINDOW_HEIGHT//2, size=36)
                pygame.display.flip()

            if self.game_state == 3:
                pass
            
            
            if self.game_state == 2:###  game over
                
                txtsurf = font.render("Game Over", True, (255,255,255))
                surface.blit(txtsurf,(250,300))
                pygame.display.flip()
                
                if self.play_state != 3:
                    self.ai.set_score(self.score.score)
                    
                    if self.score.score > self.ai.highest_score and self.ai.population_size > 1:
                        self.ai.save_best_performer()
                        
                    self.high_score_tracker = max(self.score.score, self.high_score_tracker)
                    self.highest_level_tracker = max(self.level, self.highest_level_tracker)
                    self.avg_score_tracker = self.avg_score_tracker + (self.score.score - self.avg_score_tracker)/(self.ai.population_iterator+1)
                    
                    if self.ai.population_size != 1:
                        if self.ai.population_iterator+1 == self.ai.population_size:
                            self.avg_score_tracker = 0
                            self.ai.execute_genetic_algorithm()
                            self.ai.save_weights()
                        else:
                            self.ai.population_iterator +=1
                    
                    ##restart

                    self.restart_game()

                
                

            if self.game_state == 1: ##     game running
                
                self.fall_time += clock.get_rawtime()
                

                
                if self.tetrimino.state == 0:
                    
                    self.hold_piece_switch = 0
                        
                    self.tetrimino = Tetrimino(self.tetrimino_spawn[0],self.tetrimino_spawn[1],type_ = self.next_tetrimino.type)
                    
                    safe = self.board.check_spawn_safe()
                    
                    for _ in range(safe-2):
                        self.tetrimino.update()
                    
                    self.next_tetrimino = Tetrimino(BOARD_WIDTH+ CELL_SIZE*4 + X_OFFSET, 3*CELL_SIZE,type_ = np.random.randint(0,7) )
                    
                    if self.play_state != 3:
                        #predict best move
                        best_orient , target_cords, min_value = self.ai.best_move(self.tetrimino.type, POSITIONS, copy.deepcopy(self.board.grid))
                        
                        min_value_H = float('inf')
                        if self.hold_tetrimino is not None:
                            best_orient_H , target_cords_H, min_value_H = self.ai.best_move(self.hold_tetrimino.type, POSITIONS, copy.deepcopy(self.board.grid))
                        else:
                            self.switch_hold()
                        
                        if min_value_H < min_value:
                            self.switch_hold()
                            best_orient = best_orient_H
                            target_cords = target_cords_H


                
                    
                if self.board.game_over == True:
                    self.game_state = 2
                
                
                if self.fall_time / 1000 > self.fall_speed: ## tetrimino fall down at fall speed rate
                    self.fall_time = 0
                    self.tetrimino.update()
                
                
                if self.lines_cleared == 10:## level upgrade
                    self.lines_cleared = 0
                    self.level += 1
                    if self.fall_speed > 0.12:
                        self.fall_speed -= 0.1
                
                clock.tick()
                
                if self.play_state != 3:
                    self.ai_playing(best_orient, target_cords)#+++++++++ AI ++++++++++++
                
                
                self.tetrimino.check_collision(self.board.grid)
                self.board.check_game_over()
                
                lines = self.board.check_clear()
                self.lines_cleared += lines
                self.score.update_score_on_lines(self.level, lines)
                
                
                surface.fill("black")
                
                self.display_text(surface, f"Next", BOARD_WIDTH+ CELL_SIZE + X_OFFSET +10, 6*CELL_SIZE, size = 25)
                self.display_text(surface, f"Hold", BOARD_WIDTH+ CELL_SIZE + X_OFFSET +10, 12*CELL_SIZE, size = 25)
                
                self.display_text(surface, f"Population_size: {self.ai.population_size}", 430, BOARD_HEIGHT - 20)##**********
                self.display_text(surface, f"Specimen index: {self.ai.population_iterator}", 430, BOARD_HEIGHT)##**********
                self.display_text(surface, f"Generation: {self.ai.generation_count}", 430, BOARD_HEIGHT+20)##genetic algorithm info
                # self.display_text(surface, f"target: {target_x},current: {cur_x}", 600, BOARD_HEIGHT+40)##genetic algorithm info
                # self.display_text(surface, f"cords: {target_cords}", 600, BOARD_HEIGHT+60)##genetic algorithm info
                self.display_text(surface, f"highest level: {self.highest_level_tracker}", 430, BOARD_HEIGHT+40)##
                self.display_text(surface, f"highest score: {self.high_score_tracker}", 430, BOARD_HEIGHT+60)##
                self.display_text(surface, f"Average score: {self.avg_score_tracker:.2f}", 430, BOARD_HEIGHT+80)##

                ## MENU
                self.display_text(surface, "1. Load best weights", 650, BOARD_HEIGHT-50)
                self.display_text(surface, "2. Training mode", 650, BOARD_HEIGHT-30)
                self.display_text(surface, "3. Play mode", 650, BOARD_HEIGHT-10)
                
                if self.hold_tetrimino is not None:
                    self.hold_tetrimino.display(surface)
                self.next_tetrimino.display(surface)
                self.board.display(surface)
                self.tetrimino.display(surface)
                self.tetrimino.display_shadow(surface, self.board.grid)
                
                
                self.score.display(surface , BOARD_WIDTH+ CELL_SIZE + X_OFFSET +10, 14*CELL_SIZE)
                self.display_text(surface, f"Level {self.level}",  BOARD_WIDTH+ CELL_SIZE + X_OFFSET +10, 16*CELL_SIZE , size = 36)#game level
                
                pygame.draw.rect(surface, "white", pygame.Rect(X_OFFSET, 5*CELL_SIZE, BOARD_WIDTH, BOARD_HEIGHT),2) ## border
                pygame.draw.rect(surface, "white", pygame.Rect(BOARD_WIDTH+ CELL_SIZE + X_OFFSET, CELL_SIZE, 6*CELL_SIZE, 6*CELL_SIZE),2) ## border
                pygame.draw.rect(surface, "white", pygame.Rect(BOARD_WIDTH+ CELL_SIZE + X_OFFSET, 7*CELL_SIZE, 6*CELL_SIZE, 6*CELL_SIZE),2) ## border
                
                
                pygame.draw.rect(surface, "black", pygame.Rect(0, 0 , BOARD_WIDTH+X_OFFSET, 5*CELL_SIZE))#cover up
                pygame.draw.rect(surface, "black", pygame.Rect(0, 5*CELL_SIZE + BOARD_HEIGHT , BOARD_WIDTH+X_OFFSET, 5*CELL_SIZE))
                
                
                
                # for ii , jj in target_cords:
                #     pygame.draw.rect(surface, "hotpink1", pygame.Rect(jj*CELL_SIZE + X_OFFSET, ii*CELL_SIZE + Y_OFFSET, CELL_SIZE, CELL_SIZE),1)
                
                
                
                
                #self.ai.display(surface)
                
                pygame.display.flip()
                
            for event in pygame.event.get():  
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                
                if event.type == pygame.KEYDOWN:
                    if self.game_state == 1:
                        if event.key == pygame.K_LEFT:
                            self.tetrimino.move(-1,0, self.board.grid)
                        if event.key == pygame.K_RIGHT:
                            self.tetrimino.move(1,0, self.board.grid)
                        if event.key == pygame.K_DOWN:
                            self.tetrimino.move(0,1, self.board.grid)
                            self.score.update_score_on_moves(1)
                        if event.key == pygame.K_UP:
                            self.score.update_score_on_moves(self.tetrimino.slam(self.board.grid))
                        if event.key == pygame.K_SPACE:
                            self.tetrimino.change_orientation(self.board.grid)
                        if event.key == pygame.K_RSHIFT:
                            self.switch_hold()
                            
                            
                    if event.key == pygame.K_1:
                        self.ai.load_best_performer()
                        self.restart_game()
                        self.play_state=1 
                    if event.key == pygame.K_2:
                        self.ai.load_weights()
                        self.restart_game()
                        self.play_state=2
                    if event.key == pygame.K_3:
                        self.restart_game()
                        self.play_state=3             
                        
                        
                    if event.key == pygame.K_s:
                        self.game_state=1
                    
                    if event.key == pygame.K_p:
                        if self.game_state == 1:
                            self.game_state=3 ##paus
                        else:
                            self.game_state=1
                    
                    if self.game_state == 2:## game over
                        if event.key == pygame.K_SPACE:
                            ##restart
                            self.restart_game()
                            
                        
                        

if __name__ ==  '__main__':
    game = Game()
    game.main() 