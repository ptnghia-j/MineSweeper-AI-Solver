import random

import pygame
from time import sleep
import matplotlib.pyplot as plt
import copy
from prob_player import probabilityPlayer
import numpy as np
import csv
import sys

sys.path.append('../')
from ANN_Model.ANN_model import sc

from tensorflow.keras.models import load_model

GAME_PLAYED = 0
GAME_WON = 0
WIN_RATE = [0]


'''
Artificial Neural Network 
Approach: 
  1. same the first 4 rules as by probabilityPlayer
  2. use ANN to dictate should the probability of a tile being a mine is reasonable to make progress
  or should we back up with second to lowest probability tile
  Advantage:
  - This is the process of correcting the heuristic probability to align with the actual probability of a tile being a mine
  based on the learning of the model about the mine distribution probability of the game
  - Allow the player to make open move when the alternative is safe enough to make progress when the greedy algorithm
  seems not to be able to make progress

'''

class neuralNetPlayer(probabilityPlayer):

  def __init__(self):
    super().__init__()
    self.model = load_model('../ANN_Model/ann_model.h5')
    self.model.summary()

  def play(self, no_move=False):

    self.strategy_1()
    self.strategy_2()

    self.win_test()
    if (self.game_failed is False
      and self.game_won is False):
      #sleep(1)
      self.display_tiles()

    if no_move is True:
      # calculate the probability of each tile, pick the one with lowest probability of being a mine
      candidate_tiles = self.search_tiles(open=False)
      heuristic_prob = self.local_prob_calc()
    
      count = 1
      # keep picking the candidate tile with lowest probability until the neural network says it is a safe move
      first_lowest = self.get_i_th_lowest_prob_tile(candidate_tiles, heuristic_prob, None, count)
      second_chance_first_lowest = None
   
      second_chance_first_lowest = self.second_chance_lowest_prob_tile(candidate_tiles, heuristic_prob, first_lowest, count)
      count += 1

      
      second_lowest = self.get_i_th_lowest_prob_tile(candidate_tiles, heuristic_prob, first_lowest, count)
      second_chance_second_lowest = None
      
      second_chance_second_lowest = self.second_chance_lowest_prob_tile(candidate_tiles, heuristic_prob, second_lowest, count)
      count += 1

      third_lowest = None
      # when the board gets too big, we might want to back up with the third lowest probability tile
      if self.width >= 60 and self.height >= 32 and second_lowest is not None:
        third_lowest = self.get_i_th_lowest_prob_tile(candidate_tiles, heuristic_prob, second_lowest, count)

      '''
      For Code Explanation: please view the probabilityPlayer class for this block of code
      '''
      if first_lowest is None:
        first_lowest = candidate_tiles[random.randint(0, len(candidate_tiles)-1)]
      tile_to_pick = first_lowest
      x, y = tile_to_pick

      data = []
      row = []
      for i in range(x-1, x+2):
        for j in range(y-1, y+2):
          if i == x and j == y:
            row.append(10)
            continue
          if self.is_valid_tile(i, j):
            if self.clicked_grid[j][i] == "F":
              row.append(9)
            elif self.clicked_grid[j][i] == False:
              row.append(10)
            elif self.clicked_grid[j][i] == True:
              row.append(self.grid[j][i]) 
          else:
            row.append(-1)

      """
      - Feed the configuration of lowest probability tile to the ANN to predict the chance of it having a mine
      - EXTRA ATTEMPT: Try the second chance of the same tier of probability before moving on
      - Advantage: open addressing same tier
      
      if this EXTRA ATTEMPT fail then: 
      
      - we update the heuristic probability of the lowest probability to the next lowest probability
      to address that the heuristic estimation is not accurate based on the learning of the model
      - This helps the models to gradually collect more accurate probability aligned with the actual probability
      - however, we don't want to overestimate the probability of a tile being a mine, so we only update the heuristic
      with up to 2 back up (when the board is big enough)
      - Also provide open addressing
      """

      pred = self.ann_predict(copy.deepcopy(row), heuristic_prob[y][x], 1)

      # !!! IMPORTANT: always check for availability of candidate tiles, chances are that there is none such exists
      # and we are actually at the end of the game

      # try second chance of the 1st tier of lowest probability
      if pred and second_chance_first_lowest is not None:
        print("Second chance for the #{} lowest probability tile".format(1))
        tile_to_pick = second_chance_first_lowest
        x, y = tile_to_pick

        pred = self.ann_predict(copy.deepcopy(row), heuristic_prob[y][x], 1)


      # if second fail then we need to move on to the backups

      if pred and second_lowest is not None:
        print("Back up to the second lowest probability tile")
        
        tile_to_pick = second_lowest
        x, y = tile_to_pick

        pred = self.ann_predict(copy.deepcopy(row), heuristic_prob[y][x], 2)

        # try second chance of the 2nd tier of lowest probability
        if pred and second_chance_second_lowest is not None:
          print("Second chance for the #{} lowest probability tile".format(2))
          tile_to_pick = second_chance_second_lowest
          x, y = tile_to_pick

          pred = self.ann_predict(copy.deepcopy(row), heuristic_prob[y][x], 2)

        # if all other attempts fail then we need to move on to the third lowest probability tile
        if pred and third_lowest is not None:
            print("Back up to the third lowest probability tile")
            tile_to_pick = third_lowest
      
      print("Will pick tile at: {}, with probability: {} ".format(tile_to_pick, heuristic_prob[tile_to_pick[1]][tile_to_pick[0]]))
      self.click_register(tile_to_pick[0], tile_to_pick[1])

      row.append(heuristic_prob[tile_to_pick[1]][tile_to_pick[0]])
      row.append(1 if self.game_failed else 0)
      data.append(row)

      self.csv_writer(data)
        
    self.display_top_bar()
    self.win_test()

  def get_i_th_lowest_prob_tile(self, candidates, h_prob, low_bound_tile, count):
    '''
    Get the i-th lowest probability tile
    '''
    print("Getting the #{} lowest probability tile ...".format(count))

    # Shrinking the upper bound until we find the i-th lowest probability tile
    upper_bound = 1
    lower_bound = h_prob[low_bound_tile[1]][low_bound_tile[0]] if low_bound_tile is not None else 0
    next_lowest = None
    for tile in candidates:
      curr_val = h_prob[tile[1]][tile[0]]
      if curr_val <= upper_bound and curr_val > lower_bound:
        upper_bound = curr_val
        next_lowest = tile
    return next_lowest
  
  def second_chance_lowest_prob_tile(self, candidates, h_prob, low_bound_tile, count):
    print("Second chance to get the #{} lowest probability tile ...".format(count))
    # Shrinking the upper bound until we find the second tile with same probability as the lowest probability tile
    upper_bound = 1
    # Early return if no such second lowest probability tile exists
    if low_bound_tile is None: return None
    lower_bound = h_prob[low_bound_tile[1]][low_bound_tile[0]] 

    for tile in candidates:
      curr_val = h_prob[tile[1]][tile[0]]
      if curr_val <= upper_bound and curr_val == lower_bound and tile != low_bound_tile:
        return tile
    return None
    

  def ann_predict(self, row, curr_low_prob, count):
    '''
    Predict the probability of the i_th lowest probability tile to have a mine
    by the ANN model
    '''
    print("Predicting #{} lowest probability tile to have a mine ...".format(count))

    row.append(curr_low_prob)
    probed_data = [row]
    print(probed_data)

    pred = (self.model.predict(np.array(probed_data)) > 0.5)[0][0]
    return pred

if __name__ == "__main__":

  print("Before choosing to use Neural Network, please make sure there is data in {}". format('wherever you put the data'))
  print("If there is no data, please run probabilityPlayer first to generate the data")
  
  player = neuralNetPlayer()
  player.play_simply()