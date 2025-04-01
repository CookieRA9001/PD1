import copy
from kivy.clock import Clock

class StateNode():
    childrenNodes = []
    gameState = None
    depth = 0
    heuristic_value = 0
    is_end_node = False

    def __init__(self, gameState):
        self.childrenNodes = []
        self.is_end_node = False
        self.gameState = gameState

    def addChildNode(self, childNode):
        for child in self.childrenNodes:
            if child.gameState == childNode.gameState:
                return
            
        self.childrenNodes.append(childNode)

    def getChildrenNodes(self):
        return self.childrenNodes
    
class GameState:
    numberPairs = []
    points = 0
    depth = 0
    startingPlayer = 0

    def __init__(self, numberPairs, points, depth, startingPlayer):
        self.numberPairs = numberPairs
        self.points = points
        self.depth = depth
        self.startingPlayer = startingPlayer

    def __eq__(self, other):
        if self.numberPairs == other.numberPairs and self.points == other.points and self.depth == other.depth and self.startingPlayer == other.startingPlayer:
            return True

        return False

class AIPlayer:    
    maxTreeDepth = 3
    gameState = None
    gameTree = None
    algorithm = None
    bestMoveIndex = 0

    def __init__(self, gameState, algorithm):
        self.gameState = gameState
        self.algorithm = algorithm
        self.gameTree = self.generateGameTree()
        self.maxTreeDepth = self.gameState.depth + 3

    def findBestMove(self, dt):
        if self.algorithm == "MinMax":
            bestMoveNode = self.minmax(self.gameTree, True)
            self.bestMoveIndex = self.gameTree.getChildrenNodes().index(bestMoveNode)
            return self.bestMoveIndex
        
        alpha = float('-inf')
        beta = float('inf')
        bestMoveNode = self.alphaBeta(self.gameTree, True, alpha, beta)
        self.bestMoveIndex = self.gameTree.getChildrenNodes().index(bestMoveNode)
        return 

    def updateGameState(self, newGameState):
        self.gameState = newGameState
        self.maxTreeDepth = self.gameState.depth + 3
        Clock.schedule_once(self.generateGameTreeWrapper, 0)
    
    def makeMove(self, gameState, pair, pairIndex):
        newGameState = copy.deepcopy(gameState)
        newGameState.depth += 1
        if pair[1] == 0:
            newGameState.points -= 1
            newGameState.numberPairs[pairIndex] = (-1,-1)
        else:
            new_value = pair[0] + pair[1]
            newGameState.points += 1
            if new_value >= 7:
                new_value -= 6
                newGameState.points += 1
            newGameState.numberPairs[pairIndex] = (new_value,-1)

        tempPairs = []
        for pair in newGameState.numberPairs:
            if pair[0] > 0:
                tempPairs.append(pair[0])
            if pair[1] > 0:
                tempPairs.append(pair[1])

        l = len(tempPairs)
        newGameState.numberPairs = [(tempPairs[x*2],tempPairs[x*2+1]) for x in range((int)(l/2))]
        if l%2 != 0:
            if l != 1:
                newGameState.numberPairs.append((tempPairs[l-1], 0))
            else:
                newGameState.numberPairs.append((tempPairs[0], -1))

        return newGameState
    
    def generateGameTreeWrapper(self, dt):
        self.gameTree = self.generateGameTree()
        return

    def generateGameTree(self, rootNode = None):
        if rootNode is None or not isinstance(rootNode, StateNode):
            rootNode = StateNode(self.gameState)

        if rootNode.gameState.depth >= self.maxTreeDepth:
            return rootNode
        
        for index, pair in enumerate(rootNode.gameState.numberPairs):
            newGameState = self.makeMove(rootNode.gameState, pair, index)
            childNode = StateNode(newGameState)
            if newGameState.numberPairs[0][1] == -1 or newGameState.depth == self.maxTreeDepth:
                childNode.is_end_node = True
        
            rootNode.addChildNode(childNode)

        for childNode in rootNode.getChildrenNodes():
            if not childNode.is_end_node:
               self.generateGameTree(childNode)

        return rootNode

    # Heiristiskā novērtējuma funkcija. 
    def evaluateEndNode(self, node):
        startingPlayer = self.gameState.startingPlayer
        heuristic_pair = 0
        heuristic_odd = 0

        # pārbaude, vai tas ir spēles beigas stāvoklis
        if len(node.gameState.numberPairs) == 1 and node.gameState.numberPairs[0][1] == -1:
            isPointsEven = node.gameState.points % 2 == 0
            isResultNumberEven = node.gameState.numberPairs[0][0] % 2 == 0

            if startingPlayer == 1:
                # Uzvarošs gājiens
                if isPointsEven and isResultNumberEven:
                    node.heuristic_value = 100
                # Zaudējošs gājiens
                elif not isPointsEven and not isResultNumberEven:
                    node.heuristic_value = -100
                # Neizšķirts gājiens
                else:
                    node.heuristic_value = 0
            else:
                # Zaudējošs gājiens
                if isPointsEven and isResultNumberEven:
                    node.heuristic_value = -100
                # Uzvarošs gājiens
                elif not isPointsEven and not isResultNumberEven:
                    node.heuristic_value = 100
                # Neizšķirts gājiens
                else:
                    node.heuristic_value = 0

            return node

        if node.gameState.points % 2 == 0:
            heuristic_pair += 1
            heuristic_odd -= 1
        else:
            heuristic_odd += 1
            heuristic_pair -= 1
        
        for pair in node.gameState.numberPairs:
            if pair[1] != -1 and pair[1] != 0:
                result = pair[0] + pair[1]
                if result % 2 == 0:
                    heuristic_pair += 1
                    heuristic_odd -= 1
                    if result > 6 and node.gameState.points + 1 % 2 == 0:
                        heuristic_pair += 1
                        heuristic_odd -= 1
                    elif result > 6 and node.gameState.points + 1 % 2 != 0:
                        heuristic_odd += 1
                        heuristic_pair -= 1
                else:
                    heuristic_odd += 1
                    heuristic_pair -= 1
                    if result > 6 and node.gameState.points + 1 % 2 != 0:
                        heuristic_pair += 1
                        heuristic_odd -= 1
                    elif result > 6 and node.gameState.points + 1 % 2 == 0:
                        heuristic_odd += 1
                        heuristic_pair -= 1
            elif pair[1] == 0:
                if node.gameState.points % 2 == 0:
                    heuristic_pair -= 1
                    heuristic_odd += 1
                else:
                    heuristic_pair += 1
                    heuristic_odd -= 1
                    
        if startingPlayer == 1:
            node.heuristic_value = heuristic_pair 
        else:
            node.heuristic_value = heuristic_odd

        return node

    def minmax(self, rootNode, maximizingPlayer):
        if rootNode.is_end_node:
            return self.evaluateEndNode(rootNode)
        if maximizingPlayer:
            bestHeuristicValue = float('-inf')
        else:
            bestHeuristicValue = float('inf')

        bestMove = None
        for childNode in rootNode.getChildrenNodes():
            evaluatedNode = self.minmax(childNode, not maximizingPlayer)
            
            if maximizingPlayer:
                if evaluatedNode.heuristic_value > bestHeuristicValue:
                    bestHeuristicValue = evaluatedNode.heuristic_value
                    bestMove = childNode
            else:
                if evaluatedNode.heuristic_value < bestHeuristicValue:
                    bestHeuristicValue = evaluatedNode.heuristic_value
                    bestMove = childNode

        return bestMove

    def alphaBeta(self, rootNode, maximizingPlayer, alpha, beta):
        if rootNode.is_end_node:
            return self.evaluateEndNode(rootNode)
        if maximizingPlayer:
            bestHeuristicValue = float('-inf')
        else:
            bestHeuristicValue = float('inf')
            
        bestMove = None
        for childNode in rootNode.getChildrenNodes():
            evaluatedNode = self.alphaBeta(childNode, not maximizingPlayer, alpha, beta)
            if maximizingPlayer:
                if evaluatedNode.heuristic_value > bestHeuristicValue:
                    bestHeuristicValue = evaluatedNode.heuristic_value
                    alpha = max(alpha, bestHeuristicValue)
                    bestMove = childNode
                    if beta <= alpha:
                        break
            else:
                if evaluatedNode.heuristic_value < bestHeuristicValue:
                    bestHeuristicValue = evaluatedNode.heuristic_value
                    beta = min(beta, bestHeuristicValue)
                    bestMove = childNode
                    if beta <= alpha:
                        break

        return bestMove

