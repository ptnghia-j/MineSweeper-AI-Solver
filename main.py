import pygame
import matplotlib.pyplot as plt
import copy
import numpy as np
import csv

from time import sleep
from AI_Player.logic_player import logicPlayer
from AI_Player.prob_player import probabilityPlayer
from AI_Player.neural_net_player import neuralNetPlayer

from ANN_Model.ANN_model import sc

from tensorflow.keras.models import load_model

GAME_PLAYED = 0
GAME_WON = 0
WIN_RATE = [0]

user_input = input("Human Player or AI Player? (h/a): ")

if user_input == 'h':
    session = MineSweeper()
    session.game_loop()
elif user_input == 'a':
    more_input = input("Player with Logic(l), Probability(p) or with Neural Network(n)? (l/p/n): ")
    if more_input == 'l':
        player = logicPlayer()
        player.play_simply()

    elif more_input == 'p':
        player = probabilityPlayer()
        player.play_simply()

    elif more_input == 'n':

        print("Before choosing to use Neural Network, please make sure there is data in {}". format('wherever you put the data'))
        print("If there is no data, please run the probability player first to generate data")
        
        player = neuralNetPlayer()
        player.play_simply()