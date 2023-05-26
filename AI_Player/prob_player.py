import random

import pygame
from time import sleep
import matplotlib.pyplot as plt
import copy
from logic_player import logicPlayer
import numpy as np
import csv
import sys

sys.path.append('../')

GAME_PLAYED = 0
GAME_WON = 0
WIN_RATE = [0]


'''
Probability - Artificial Neural Network 
Approach: 
  1. same the first 3 rules as by logicPlayer
  2. when no move can be made, rather than randomly open an unopened tile,
  greedily pick the tile with lowest probability of being a mine
  3. use ANN to dictate should the probability of a tile being a mine is reasonable to make progress
  or should we back up with second to lowest probability tile
'''

class probabilityPlayer(logicPlayer):

  def local_prob_calc(self):
    # calculate the probability of all unopened tiles, by taken into account the number of mines 
    # and the number of unopened tiles around it
    # matrix is of size (height, width)
    heuristic_prob = np.zeros((self.height, self.width))
    unopened_tiles = self.search_tiles()
    for u_tile in unopened_tiles:
      count = 0
      neighbors, flags = self.neighbors_and_flags(u_tile[0], u_tile[1], open=True)

      # if the tile is not surrounded by any opened tiles, 
      # then the probability of it being a mine is the number of mines left / number of unopened tiles

      if len(neighbors) == 0:
        heuristic_prob[u_tile[1]][u_tile[0]] = self.bomb_left / len(unopened_tiles)
        count += 1

      else:
        for neighbor in neighbors:
          # get the number of unopened tiles around the neighbor
          n_neighbors, n_flags = self.neighbors_and_flags(neighbor[0], neighbor[1], open=False)
          mine_left = self.grid[neighbor[1]][neighbor[0]] - n_flags
          n_unopened_tiles = len(n_neighbors)

          # probability of the unopened depends on the number indicated on the neighbor tile and known mines and unopened tiles around it
          heuristic_prob[u_tile[1]][u_tile[0]] += mine_left / n_unopened_tiles
          # also increase the incident count of the unopened tile
          count += 1

      # normalize the probability
      heuristic_prob[u_tile[1]][u_tile[0]] /= count
        
    return heuristic_prob

  
  def play(self, no_move=False):
      

    self.strategy_1()
    self.strategy_2()

    self.win_test()
    if (self.game_failed is False
      and self.game_won is False):
      # sleep(1)
      self.display_tiles()

    if no_move is True:
      # calculate the probability of each tile, pick the one with lowest probability of being a mine
      candidate_tiles = self.search_tiles(open=False)
      heuristic_prob = self.local_prob_calc()
    
      
      # pick the candidate tile with lowest probability
      temp = 1
      tile_to_pick = None
      for tile in candidate_tiles:
        if heuristic_prob[tile[1]][tile[0]] <= temp:
          temp = heuristic_prob[tile[1]][tile[0]]
          tile_to_pick = tile

      x, y = tile_to_pick

      
      # generate the data for ANN supervised learning
      # the data will be collected from the neighbors of the best candidate tile
      # from top left clockwise corresponding to columns 1 - 8 and 
      # the column 9 will contain the probability of the best candidate tile
      # the last column will be the label of the data, 1 if tile does contain a mine, 0 otherwise
      # file name: depend on the configuration of the game, 
      # should use different name for different configuration to collect suitable data
      # 9: mine, 0: empty, -1: out of bound, 10 : unknown
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

      
      #print("Row checking before model: {}".format(row))
      print("Will pick tile at: {}, with probability: {} ".format(tile_to_pick, heuristic_prob[y][x]))
      self.click_register(x,y)

      row.append(heuristic_prob[y][x])
      row.append(1 if self.game_failed else 0)
      data.append(row)

      self.csv_writer(data)
        
    self.display_top_bar()
    self.win_test()

  def csv_writer(self, data):
      # write the data to csv file
      dir = '../data/'
      file_name = 'data_80_45.csv'
      datapath = dir + file_name

      with open(datapath, 'a') as f:
        writer = csv.writer(f)
        writer.writerows(data)

if __name__ == "__main__":


  # #  Leave this commented since it easily mess up the dataset 
  # # Only for running for the first time, 
  # #  or can just manually create the file and write the header, 
  # fields = ['top_left', 'top', 'top_right', 'left', 'center', 'right', 'bottom_left', 'bottom', 'bottom_right', 'probability', 'has_mine']
  # # write the data to csv file
  
  # dir = '../data/'
  # file_name = 'data_custom_80_45_743.csv'
  # datapath = dir + file_name

  # with open(datapath, 'a') as f:
  #   writer = csv.writer(f)
  #   writer.writerow(fields)

  player = probabilityPlayer()
  player.play_simply()
