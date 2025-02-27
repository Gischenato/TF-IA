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
from enum import Enum
#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AttackAgent', second = 'DefenseAgent'):
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
def parse_map(map_str):
  lines = map_str.strip().split('\n')
  grid = [list(line) for line in lines]
  return grid

from time import sleep
class BaseAgent(CaptureAgent):
    
  def bfs_distance_goals(self, pos1, enemies=[], goals=[]):
    def bfs(grid, start):
      rows, cols = len(grid), len(grid[0])
      queue = [(start, 0, Directions.STOP)]  # (position, distance)
      visited = set([start])
      
      directions = [Directions.EAST, Directions.WEST, Directions.SOUTH, Directions.NORTH]
      
      while queue:  
        curr, distance, _dir = queue.pop(0)
        
        if grid[curr[1]][curr[0]] == '-':
          return distance, _dir
        neighbors = [(curr[0] + 1, curr[1]), (curr[0] - 1, curr[1]), (curr[0], curr[1] + 1), (curr[0], curr[1] - 1)]
        
        for vizinho, direct in zip(neighbors, directions):
          if 0 <= vizinho[0] < cols and 0 <= vizinho[1] < rows:
            if grid[vizinho[1]][vizinho[0]] not in ['%'] and vizinho not in visited:
              if _dir != Directions.STOP:
                direct = _dir
              queue.append((vizinho, distance + 1, direct))
              visited.add(vizinho)
              
      return float('inf'), Directions.STOP  # Retorna infinito se não houver caminho

    grid = parse_map(self.layout)
    
    for pos in enemies:
      grid[len(grid) - pos[1] - 1][pos[0]] = '%'
    for pos in goals:
      grid[len(grid) - pos[1] - 1][pos[0]] = '-'
    
    # y must be inverted
    pos1 = (pos1[0], len(grid) - pos1[1] - 1)
    
    return bfs(grid, pos1)
  
  def bfs_distance(self, pos1, pos2, enemies=[]):
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
    # print(self.layout)
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
  def registerInitialState(self, gameState: GameState) -> None:
    super().registerInitialState(gameState)
    self.strategy = 'CAPSULE'
    self.strategies = {
      'CAPSULE': self.findCapsule,
      'FOOD': self.findNearFood,
      'RETURN': self.findCapsule
    }
    
  
  def chooseAction(self, gameState: GameState) -> Action:
    if self.seeking == self.start:
      if not gameState.getAgentState(self.index).isPacman:
        self.strategy = 'FOOD'
    # print(self.strategy)
    action = self.strategies[self.strategy](gameState)
    return action
  
  def setup(self, gameState: GameState) -> None:
    self.seeking = self.getCapsules(gameState)[0]
    self.moviments = 0
    self.ignoreGhosts = True

  def getOponentPositions(self, gameState: GameState):
    opponentBlockPos = []
    for opponentsIndex in self.getOpponents(gameState):
      opponentPos = gameState.getAgentPosition(opponentsIndex)
      if gameState.getAgentPosition(opponentsIndex) != None:
        opponentBlockPos.append(opponentPos)
    return opponentBlockPos
    
  # def returnToBase(self, gameState: GameState):
  #   current = gameState.getAgentPosition(self.index)
  #   dist, _dir = self.bfs_distance(self.start, current)
  #   if dist == 0:
  #     self.strategy = 'FOOD'
  #     return self.
  #   return _dir

  def findNearFood(self, gameState: GameState):
    isPacman = gameState.getAgentState(self.index).isPacman
    if isPacman:
      self.moviments += 1
    current = gameState.getAgentPosition(self.index)
    opponentBlockPos = self.getOponentPositions(gameState)
    food = self.getFood(gameState).asList()
    if len(food) <= 2:
      self.strategy = 'RETURN'
      return self.findCapsule(gameState)

    if self.moviments < 33:
      if self.ignoreGhosts or not isPacman:
        dist, _dir = self.bfs_distance_goals(current, goals=food)
      else:
        dist, _dir = self.bfs_distance_goals(current, enemies=opponentBlockPos, goals=food)
    else:
      self.strategy = 'RETURN'
      self.seeking = self.start
      self.moviments = 0
      self.ignoreGhosts = False
      return self.findCapsule(gameState)
    
    return _dir

  def findCapsule(self, gameState: GameState):
    # print(gameState.getAgentPosition(self.index))
    
    current = gameState.getAgentPosition(self.index)
    if current == self.seeking:
      self.strategy = 'FOOD'
      return self.findNearFood(gameState)

    opponentBlockPos = self.getOponentPositions(gameState)
      
    bestDist = 9999
    actions = gameState.getLegalActions(self.index)
    
    for action in actions:
      successor = self.getSuccessor(gameState, action)
      pos2 = successor.getAgentPosition(self.index)
      dist = self.bfs_distance(self.seeking,pos2, opponentBlockPos)
      
      if opponentBlockPos != None and gameState.getAgentState(self.index).isPacman:
        if not self.calcXNextMoves(gameState, 3, opponentBlockPos):
          # print("opponent is near")
          continue
      if dist < bestDist:
        bestAction = action
        bestDist = dist
    if bestDist == 9999:
      # print("random action")
      return Directions.STOP
    return bestAction
  
  def calcXNextMoves(self, gameState: GameState, moves, opponentPos=[]):
    possible = True
    for i in range(moves):
      bestDist = 9999
      bestAction = None
      actions = gameState.getLegalActions(self.index)
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.bfs_distance(self.seeking, pos2, opponentPos)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      if bestAction == None:
        bestAction = random.choice(actions)
      gameState = self.getSuccessor(gameState, bestAction)
      # print(gameState.getAgentPosition(self.index), opponentPos)
      for pos in opponentPos:
        if self.calculateDistance(gameState.getAgentPosition(self.index), pos) == 1:
          possible = False
          # print("opponent is near")
          break
      
    # print(possible)
    return possible
          
  def calculateDistance(self, pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
  
  def opponentIsNear():
    pass
    

class DefenseAgent(BaseAgent):
  def bfs_distance_foods(self, pos1, foods=[]):
      def bfs(grid, start):
        rows, cols = len(grid), len(grid[0])
        queue = [(start, 0, Directions.STOP)]  # (position, distance)
        visited = set([start])
        
        directions = [Directions.EAST, Directions.WEST, Directions.SOUTH, Directions.NORTH]
        
        while queue:  
          curr, distance, _dir = queue.pop(0)

          if grid[curr[1]][curr[0]] == '-' and distance <= 3:
            self.foods.remove((curr[0], len(grid) - curr[1] - 1))
            continue

          if grid[curr[1]][curr[0]] == '-' and distance > 3:
            return distance, _dir, (curr[0], len(grid) - curr[1] - 1)
          neighbors = [(curr[0] + 1, curr[1]), (curr[0] - 1, curr[1]), (curr[0], curr[1] + 1), (curr[0], curr[1] - 1)]
          
          for vizinho, direct in zip(neighbors, directions):
            if 0 <= vizinho[0] < cols and 0 <= vizinho[1] < rows:
              if grid[vizinho[1]][vizinho[0]] not in ['%'] and vizinho not in visited:
                if _dir != Directions.STOP:
                  direct = _dir
                queue.append((vizinho, distance + 1, direct))
                visited.add(vizinho)
                
        return float('inf'), Directions.STOP, self.start  # Retorna infinito se não houver caminho

      grid = parse_map(self.layout)
      
      for pos in foods:
        grid[len(grid) - pos[1] - 1][pos[0]] = '-'
      
      # y must be inverted
      pos1 = (pos1[0], len(grid) - pos1[1] - 1)
      
      return bfs(grid, pos1)


  def registerInitialState(self, gameState: GameState) -> None:
    super().registerInitialState(gameState)
    self.strategy = 'POSITION'
    self.strategies = {
      'POSITION': self.position,
      'POSITION2': self.position2
    }
    self.startAction = None
    self.foodDist = 0
    self.seeking =  None
    self.foods = self.getFoodYouAreDefending(gameState).asList()
  
  def chooseAction(self, gameState: GameState) -> Action:
    action = self.strategies[self.strategy](gameState)
    return action

  def getDefensiveFood(self, gameState: GameState):
    food = self.getFoodYouAreDefending(gameState).asList()
    return food

  def getOponentPositions(self, gameState: GameState):
    opponentBlockPos = []
    for opponentsIndex in self.getOpponents(gameState):
      opponentPos = gameState.getAgentPosition(opponentsIndex)
      if gameState.getAgentPosition(opponentsIndex) != None:
        opponentBlockPos.append(opponentPos)
    return opponentBlockPos
  
  def position(self, gameState: GameState):
    if self.startAction == None:
      for action in gameState.getLegalActions(self.index):
        if action != Directions.STOP:
          self.startAction = action
    elif self.startAction not in gameState.getLegalActions(self.index):
      self.strategy = 'POSITION2'
      return self.position2(gameState)
    return self.startAction

  def position2(self, gameState: GameState):
    current = gameState.getAgentPosition(self.index)
    opponentBlockPos = self.getOponentPositions(gameState)

    if gameState.getAgentState(self.index).isPacman:
      dist, _dir = self.bfs_distance_goals(current, goals=[self.start])
      return _dir

    if len(opponentBlockPos) > 0:
      dist, _dir = self.bfs_distance_goals(current, goals=opponentBlockPos)
      if dist < 4:
        return _dir
      
    if self.foodDist > 3:
      dist, _dir = self.bfs_distance_goals(current, goals=[self.seeking])
      self.foodDist -= 1
      if self.seeking == self.start:
        self.foods = self.getFoodYouAreDefending(gameState).asList()
        self.foodDist = 0
    else:
      if len(self.foods) < 3:
        self.foods = self.getFoodYouAreDefending(gameState).asList()
      dist, _dir, pos = self.bfs_distance_foods(current, foods=self.foods)
      if pos in self.foods:
        self.foods.remove(pos)
      self.seeking = pos
      self.foodDist = dist

    return _dir
  
  def opponentIsNear():
    pass