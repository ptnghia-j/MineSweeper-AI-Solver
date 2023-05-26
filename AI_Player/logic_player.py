import random
import sys
import pygame
from time import sleep
import matplotlib.pyplot as plt
import copy

sys.path.append('../')
from mine_sweeper import MineSweeper

GAME_PLAYED = 0
GAME_WON = 0
WIN_RATE = [0]

'''
Rule: 
  Flaw of this game design: I haven't fixed this bug yet so will just follow the rule below for now:

  Access to clicked_grid is known to the player, player can freely query this list
  Access to grid is not known to the player, play can only query the list on the tile that is opened
  Access to grid when the tile is not opened is cheating

  i.e if clicked_grid[i][j] = False, access to grid[i][j] is cheating
  but if clicked_grid[i][j] = True, access to grid[i][j] is not cheating

  Also access to grid[i][j] to check the mine is cheating unless it is to determine the loss of the game
'''


'''
Set-Logic Player Class:
  Algorithm :
  1. First move: randomly open at one of the four corners of the board

  2. Strategy 1: 
  For each open tile, check the number of unopened tiles around it
  if the number in the tile is equal to the number of unopened tiles around it,
  then flag all the unopened tiles around it

  if the number in the tile is equal to the number of flags around it,
  then open all the unopened tiles around it

  3. Strategy 2: 
    For a pair of open tile adjacent to each other:
    let nfn_a = set of unopened tiles 
    let nfn_b = set of unopened tiles

    let a_val = value of tile a - number of flags around tile a
    let b_val = value of tile b - number of flags around tile b

    if a_val > b_val:
      if a_val - b_val = nfn_a - nfn_b:
        flag all tiles in nfn_a - nfn_b
        open all tiles in nfn_b - nfn_a
    else:
      if b_val - a_val = nfn_b - nfn_a:
        flag all tiles in nfn_b - nfn_a
        open all tiles in nfn_a - nfn_b

  4. If no move can be made, randomly open a tile
  '''
class logicPlayer(MineSweeper):

  def play_simply(self):
    old_state = None
    new_state = copy.deepcopy(self.clicked_grid)
    
    pygame.init()
    self.init_display()

    # Make the first move at the top left corner
    self.click_register(0,0)

    while True:
      pygame.display.update()
      self.clock.tick(60)
  
      if self.game_failed is False and self.game_won is False:
        old_state = copy.deepcopy(new_state)
        new_state = copy.deepcopy(self.clicked_grid)
        self.play() if new_state != old_state else self.play(no_move=True)
        if(new_state == old_state):
          print("no change, apply random")
          #self.play(no_move=True)
          
      else:
        self.plot_win_rate()

        # Reset the game
        self.face_click()
        self.game_failed = False

      self.update_timer()

  def play(self, no_move=False):
    

    self.strategy_1()
    self.strategy_2()

    self.win_test()
    if (self.game_failed is False
      and self.game_won is False):

      # ! NOTE: take this sleep command out to generate the statistics faster
      #sleep(1)
      self.display_tiles()

    if no_move is True:
      # Pick one in the unopened tiles
      tile = self.search_tiles(open=False, early_stop=True)
      print("Tile list: ", tile)
      print("Randomly picking tile at: {} {}", tile[0][0], tile[0][1])
    
      self.click_register(tile[0][0], tile[0][1])

        
    self.display_top_bar()
    self.win_test()

  def strategy_1(self):
    # same as algorithm 1
    no_move = True
    open_tiles = self.search_tiles(open=True)

    for tile in open_tiles:
      x, y = tile
      unopened_tiles, flag_count = self.neighbors_and_flags(x, y)
        
      if self.grid[y][x] == (len(unopened_tiles) + flag_count) and len(unopened_tiles) > 0:
        self.flag_tiles(unopened_tiles)
        no_move = False
          
      if self.grid[y][x] == flag_count and len(unopened_tiles) > 0:
        self.open_tiles(unopened_tiles)
        no_move = False

    return no_move
  
  def strategy_2(self):
    no_move = True
    open_tiles = self.search_tiles(open=True)

    numbered_tiles = self.numbered_tiles(open_tiles)
    open_pairs = []
    for i in range(len(numbered_tiles)):
      first_tile = numbered_tiles[i]

      for direction in [(0,1), (0,-1), (1,0), (-1,0)]:
        second_tile = (first_tile[0] + direction[0], first_tile[1] + direction[1])
        if self.is_valid_tile(second_tile[0], second_tile[1]) and second_tile in numbered_tiles:
          open_pairs.append((first_tile, second_tile))
    
 
    # For each pair of open adjacent tiles, check if the number of unopened tiles around them
    # is equal to the difference between the value of the tiles and the number of flags around them
    for pair in open_pairs:
      tile_a = pair[0]
      tile_b = pair[1]

      unopened_a, flag_a = self.neighbors_and_flags(tile_a[0], tile_a[1])
      unopened_b, flag_b = self.neighbors_and_flags(tile_b[0], tile_b[1])

      nfn_a = set(unopened_a)
      nfn_b = set(unopened_b)

     
      a_val = self.grid[tile_a[1]][tile_a[0]] - flag_a
      b_val = self.grid[tile_b[1]][tile_b[0]] - flag_b

      
      no_move = self.set_operation(nfn_a, nfn_b, a_val, b_val) if a_val > b_val else self.set_operation(nfn_b, nfn_a, b_val, a_val)

    return no_move
  
  def plot_win_rate(self):
    global GAME_PLAYED, GAME_WON
    GAME_PLAYED += 1
    if self.game_won:
      GAME_WON += 1
    print("Game won: ", GAME_WON) if self.game_won else print("Game lost", GAME_PLAYED - GAME_WON)
    curr_rate = GAME_WON/GAME_PLAYED
    WIN_RATE.append(curr_rate)
    print("Win rate: ", curr_rate)
    
    
    # Plot the win rate as the game progresses
    plt.ion()
    plt.plot(WIN_RATE)
    plt.xlabel("Number of games played")
    plt.ylabel("Win rate")
    plt.show()



    
  def search_tiles(self, open=False, early_stop=False):
    '''
    Returns a list of tiles that are either opened or unopened
    '''
    tiles = []
    for i in range(self.width):
      for j in range(self.height):
        if self.clicked_grid[j][i] == open:
          tiles.append((i,j))
          if early_stop:
            return tiles

    return tiles
  
  def numbered_tiles(self, tiles):
    '''
    Returns a list of tiles that are numbered
    '''
    return [tiles[i] for i in range(len(tiles)) if str(self.grid[tiles[i][1]][tiles[i][0]]).isdigit()]

  def is_valid_tile(self, x, y):
    return x >= 0 and x < self.width and y >= 0 and y < self.height
  
  def face_click(self):
      '''
      Override method to reset the game
      '''
      self.__init__()
      self.play_simply()

  def neighbors_and_flags(self, x, y, open=False):
    '''
    Returns the number of neighbors and flags around a tile
    '''
    neighbors = []
    flags = 0
    for i in range(x-1, x+2):
      for j in range(y-1, y+2):
        if self.is_valid_tile(i, j):
          
          if self.clicked_grid[j][i] is open:
            neighbors.append((i,j))

          if self.clicked_grid[j][i] == "F":
            flags += 1
    return neighbors, flags
  
  def flag_tiles(self, tiles):
    '''
    Flag all the tiles in the list
    '''
    for tile in tiles:
      self.right_click_register(tile[0], tile[1])


  def open_tiles(self, tiles):
    '''
    Open all the tiles in the list
    '''
    for tile in tiles:
      self.click_register(tile[0], tile[1])


  def set_operation(self, bigger, smaller, bigger_val, smaller_val):
    no_move = True
    if bigger_val - smaller_val == len(bigger - smaller):
      self.flag_tiles(bigger - smaller)
      self.open_tiles(smaller - bigger)
      no_move = False
    return no_move

if __name__ == "__main__":
  player = logicPlayer()
  player.play_simply()