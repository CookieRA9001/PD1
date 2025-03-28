class StateNode():
    parentNode = None
    gameState = None
    heuristic_value = 0

    def __init__(self, parentNode, gameState):
        self.parentNode = parentNode
        self.gameState = gameState

    def addChildNode(self, childNode):
        self.childrenNodes.append(childNode)

    def getChildrenNodes(self):
        return self.childrenNodes

    def getParentNode(self):
        return self.parentNode
    
class GameState:
    numberPairs = []
    points = 0
    depth = 0
    startingPlayer = 0

    def __init__(self, numberPairs, points, depth):
        self.numberPairs = numberPairs
        self.points = points
        self.depth = depth


class AIPlayer:    
    maxTreeDepth = 5
    gameState = None

    def __init__(self, gameState):
        self.gameState = gameState

    def getBestMove(self):
        return self.gameState.getBestMove()

    def updateGameState(self, newGameState):
        self.gameState = newGameState

    def generateGameTree(self, rootNode):
        if rootNode is None:
            rootNode = StateNode(None, self.gameState)

        if rootNode.gameState.depth >= self.maxTreeDepth:
            return rootNode
        
        for pair in rootNode.gameState.numberPairs:
            newGameState = self.gameState.makeMove(pair)
            childNode = StateNode(rootNode, newGameState)
            rootNode.addChildNode(childNode)

        for childNode in rootNode.getChildrenNodes():
            self.generateGameTree(childNode)

        return rootNode

    def evaluateGameTree(self, node):
        if node.gameState.depth == self.maxTreeDepth:
            return self.evaluateEndNode(node)

        maxPoints = 0
        for childNode in node.getChildrenNodes():
            points = self.evaluateGameTree(childNode)
            if points > maxPoints:
                maxPoints = points

        return maxPoints

    def evaluateEndNode(self, node):
        if node.gameState.points % 2 == 0:
            return 1
        else:
            return -1
