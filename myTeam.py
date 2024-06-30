# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

import random

import util
from capture import GameState
from captureAgents import CaptureAgent
from game import Action
from game import Directions
from util import nearestPoint
from collections import deque

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AttackAgent', second = 'BaseAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########
from time import sleep
class BaseAgent(CaptureAgent):
  
  def bfs_distance(self, pos1, pos2, enemies=[]):
    def parse_map(map_str):
      lines = map_str.strip().split('\n')
      grid = [list(line) for line in lines]
      return grid
    
    def bfs(grid, start, goal):
      # print("\033[H\033[J", end="")
      # for l in grid:
      #   print("".join(l))
      rows, cols = len(grid), len(grid[0])
      queue = [(start, 0)]  # (position, distance)
      visited = set([start])
      
      while queue:  
        curr, distance = queue.pop(0)
        
        if curr == goal:
          return distance
        
        for vizinho in [(curr[0] + 1, curr[1]), (curr[0] - 1, curr[1]), (curr[0], curr[1] + 1), (curr[0], curr[1] - 1)]:
          if 0 <= vizinho[0] < cols and 0 <= vizinho[1] < rows:
            if grid[vizinho[1]][vizinho[0]] not in ['%'] and vizinho not in visited:
              visited.add(vizinho)
              queue.append((vizinho, distance + 1))
      
      return float('inf')  # Retorna infinito se não houver caminho
    
    grid = parse_map(self.layout)
    for pos in enemies:
      grid[len(grid) - pos[1] - 1][pos[0]] = '%'
    # y must be inverted
    pos1 = (pos1[0], len(grid) - pos1[1] - 1)
    pos2 = (pos2[0], len(grid) - pos2[1] - 1)    
    # print(grid)
    return bfs(grid, pos1, pos2)
  
  
  def registerInitialState(self, gameState: GameState) -> None:
    self.layout = str(gameState.data.layout)
    print(self.layout)
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.setup(gameState)

  def chooseAction(self, gameState: GameState) -> Action:
    actions = gameState.getLegalActions(self.index)
    return random.choice(actions)

  def getSuccessor(self, gameState: GameState, action: Action) -> GameState:
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor


  def setup(self, gameState: GameState) -> None:
    pass
  
class AttackAgent(BaseAgent):
  def chooseAction(self, gameState: GameState) -> Action:
    action = self.findCapsule(gameState)
    return action
  
  def setup(self, gameState: GameState) -> None:
    self.seeking = self.getCapsules(gameState)[0]

  def findNearFood(self, gameState: GameState):
    print(self.getFood(gameState).asList())

  def findCapsule(self, gameState: GameState):
    # print(gameState.getAgentPosition(self.index))
    
    current = gameState.getAgentPosition(self.index)
    if current == self.seeking:
      print("Capsule found")
      self.findNearFood(gameState)
      
    # my_dist = self.bfs_distance(current, self.capsule)
    # other_dist = self.getMazeDistance(current, self.capsule)
    # print(self.capsule)
    # print(my_dist, other_dist)
    opponentBlockPos = []
    for opponentsIndex in self.getOpponents(gameState):
      opponentPos = gameState.getAgentPosition(opponentsIndex)
      if gameState.getAgentPosition(opponentsIndex) != None:
        opponentBlockPos.append(opponentPos)
    bestDist = 9999
    actions = gameState.getLegalActions(self.index)
    for action in actions:
      successor = self.getSuccessor(gameState, action)
      pos2 = successor.getAgentPosition(self.index)
      dist = self.bfs_distance(self.seeking,pos2, opponentBlockPos)
      if opponentBlockPos != None:
        if not self.calcXNextMoves(gameState, 3, opponentBlockPos):
          print("opponent is near")
          continue
      if dist < bestDist:
        bestAction = action
        bestDist = dist
    if bestDist == 9999:
      print("random action")
      return Directions.STOP
    return bestAction
  
  def calcXNextMoves(self, gameState: GameState, moves, opponentPos=[]):
    possible = True
    for i in range(moves):
      bestDist = 9999
      actions = gameState.getLegalActions(self.index)
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.bfs_distance(self.seeking, pos2, opponentPos)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      gameState = self.getSuccessor(gameState, bestAction)
      # print(gameState.getAgentPosition(self.index), opponentPos)
      for pos in opponentPos:
        if self.calculateDistance(gameState.getAgentPosition(self.index), pos) == 1:
          possible = False
          print("opponent is near")
          break
      
    # print(possible)
    return possible
          
  def calculateDistance(self, pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
  
  def opponentIsNear():
    pass
    

class DefenseAgent(BaseAgent):
  def chooseAction(self, gameState: GameState) -> Action:
    actions = gameState.getLegalActions(self.index)
    return random.choice(actions)