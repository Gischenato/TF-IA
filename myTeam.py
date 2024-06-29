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

class BaseAgent(CaptureAgent):
  def registerInitialState(self, gameState: GameState) -> None:
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
    self.capsule = self.getCapsules(gameState)[0]

  def findCapsule(self, gameState: GameState):
    current = gameState.getAgentPosition(self.index)
    opponentBlockPos = None
    for opponentsIndex in self.getOpponents(gameState):
      opponentPos = gameState.getAgentPosition(opponentsIndex)
      if gameState.getAgentPosition(opponentsIndex) != None:
        opponentBlockPos = opponentPos
    if current == self.capsule:
        pass
    bestDist = 9999
    actions = gameState.getLegalActions(self.index)
    for action in actions:
      successor = self.getSuccessor(gameState, action)
      pos2 = successor.getAgentPosition(self.index)
      dist = self.getMazeDistance(self.capsule,pos2)
      if opponentBlockPos != None:
        if self.calcXNextMoves(self.getSuccessor(gameState, action), 3, opponentPos):
          print("opponent is near")
          continue
      if dist < bestDist:
        bestAction = action
        bestDist = dist
    if bestDist == 9999:
      return random.choice(actions)
    return bestAction
  
  def calcXNextMoves(self, gameState: GameState, moves, opponentPos):
    if moves == 0:
      return False
    for action in gameState.getLegalActions(self.index):
      successor = gameState.generateSuccessor(self.index, action)
      if successor.getAgentPosition(self.index) == opponentPos:
        return True
      if self.calcXNextMoves(successor, moves - 1, opponentPos):
        return True
    return False
  
  def opponentIsNear():
    pass
    

class DefenseAgent(BaseAgent):
  def chooseAction(self, gameState: GameState) -> Action:
    actions = gameState.getLegalActions(self.index)
    return random.choice(actions)