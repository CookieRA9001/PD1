import random
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.behaviors import HoverBehavior
from kivy.lang import Builder
from kivy.config import Config
from kivy.properties import BoundedNumericProperty
from AI_player_logic import AIPlayer, GameState;
from kivy.clock import Clock
from kivy.logger import Logger

# Kivi aplikācijas iestatījumi
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')

# Importē .kv failu izkārtojumus
Builder.load_file('InputBox.kv')
Builder.load_file('GameButton.kv')
Builder.load_file('NumberButton.kv')
Builder.load_file('GamePage.kv')
Builder.load_file('GameStateBox.kv')

# Spēļu pogu klase standartizētam noformējumam
class GameButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# Ciparu pāris
class NumberButton(BoxLayout, HoverBehavior):
    value = (0,0)
    index = -1
    game_page = None

    def __init__(self, gp, **kwargs):
        super().__init__(**kwargs)
        self.game_page = gp
        self.count = gp.arrayLength
        self.index = len(gp.numberBtns)

    def setup(self, value):
        self.value = value
        self.num1.text = str(self.value[0])
        self.num2.text = str(self.value[1])

        if self.value[1] == 0:
            self.is_leftover = True
    
    def numSelect(self, isAiMove = False):
        new_value = 'XX'
        if self.value[1] == 0:
            self.game_page.gameStateBox.addPoints(-1)
            self.game_page.gameStateBox.gameState.numberPairs[self.index] = (-1,-1)
        else:
            new_value = self.value[0] + self.value[1]
            self.game_page.gameStateBox.addPoints(1)
            if new_value >= 7:
                new_value -= 6
                self.game_page.gameStateBox.addPoints(1)
            self.game_page.gameStateBox.gameState.numberPairs[self.index] = (new_value,-1)
        self.game_page.gameStateBox.update(self.value, new_value)
        self.game_page.regenerate(isAiMove)

    def update(self, new_index):
        self.index = new_index
        self.count = len(self.game_page.gameStateBox.gameState.numberPairs) * 2
        
# Spēļu texta lauka klase standartizētam noformējumam
class InputBox(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class GameStateBox(BoxLayout):
    lastMove = (0, 0)
    gameState = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def addPoints(self, points):
        self.gameState.points += points

    def update(self, lastMove, newValue):
        self.lastMove = lastMove
        self.lastMoveNum1.text = str(lastMove[0])
        self.lastMoveNum2.text = str(lastMove[1])
        self.lastMoveNum1.visible = True
        if newValue == 'XX':
            self.lastMoveNum2.visible = False
            self.lastMoveSign.visible = False
        else:
            self.lastMoveNum2.visible = True
            self.lastMoveSign.visible = True

        self.lastMoveResult.text = str(newValue)
        self.totalPointsBox.text = "Punktu skaits: " + str(self.gameState.points)
        self.lastMoveBox.text = "Pēdējais gājiens: "

    def refreshNewState(self, gameState, startingPlayer):
        self.gameState = gameState
        self.update((0,0), '0')
        self.gameStateTitle.text = startingPlayer + " iet"

    def showFinalResult(self):
        self.lastMoveBox.text = "Pēdējais skaitlis: "
        self.lastMoveNum1.visible = False
        self.lastMoveNum2.visible = False
        self.lastMoveSign.visible = False
        self.lastMoveResult.end = True

# Spēles galvenā "lapa"
class GamePage(Widget):
    arrayLength = BoundedNumericProperty(5, min=5, max=25, errorhandler=lambda x: 25 if x > 25 else 5)
    players = ['Cilvēks', 'Dators']
    numberBtns = []
    startingPlayer = 0
    currentPlayer = 0
    aiPlayer = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def lengthInput(self, text):
        try:
            self.arrayLength = int(text)
        except:
            self.arrayLength = 0
        self.arrayLenghtInput.text = str(self.arrayLength)
    
    def startGame(self):
        self.startSettingBox.opacity = 0
        self.startSettingBox.disabled = True
        self.startSettingBox.visible = False
        self.gameStateBox.gameStateBody.visible = True
        self.gameBox.visible = True
        self.startingPlayer = self.players.index(self.dropdownStartingPlayer.text)
    
        values = [(random.randint(1,6),random.randint(1,6)) for x in range((int)(self.arrayLength/2))]
        if self.arrayLength%2 != 0:
            values.append((random.randint(1,6),0))
        self.numberBtns = []

        for i in values:
            numberBtn = NumberButton(self)
            self.numberBtns.append(numberBtn)
            self.numberListBox.add_widget(numberBtn)
            numberBtn.setup(i)

        newGameState = GameState(values, 0, 0, self.startingPlayer)
        self.currentPlayer = self.startingPlayer
        if self.startingPlayer == 0:
            self.numberListBox.disabled = False
        
        self.gameStateBox.refreshNewState(newGameState, self.players[self.startingPlayer])
        self.aiPlayer = AIPlayer(self.gameStateBox.gameState, self.dropdownAILogic.text)

        if self.startingPlayer == 1:
            self.numberListBox.disabled = True
            Clock.schedule_once(self.aiPlayer.generateGameTreeWrapper, 0)
            Clock.schedule_once(self.aiPlayer.findBestMove, 0)
            Clock.schedule_once(self.numberBtns[self.aiPlayer.bestMoveIndex].numSelect, 1)

    def removePair(self, numIndex):
        self.numberListBox.remove_widget(self.numberBtns[numIndex])
        self.numberBtns.remove(self.numberBtns[numIndex])
        i = 0
        for nb in self.numberBtns:
            nb.update(i)
            i += 1
    
    def regenerate(self, isAiMove = False):
        if not isAiMove:
            self.numberListBox.disabled = True
        else:
            self.numberListBox.disabled = False

        temp = []
        for i in self.gameStateBox.gameState.numberPairs:
            if i[0] > 0:
                temp.append(i[0])
            if i[1] > 0:
                temp.append(i[1])
        
        l = len(temp)
        self.gameStateBox.gameState.numberPairs = [(temp[x*2],temp[x*2+1]) for x in range((int)(l/2))]
        if l%2 != 0:
            self.gameStateBox.gameState.numberPairs.append((temp[l-1],0))
        
        self.numberListBox.clear_widgets()

        if l == 1:
            num_is_pair = temp[0]%2==0
            point_is_pair = self.gameStateBox.gameState.points % 2==0
            winner = "Neizšķirts!"
            if num_is_pair and point_is_pair:
                winner = self.players[self.startingPlayer] + " uzvarēja!"
            elif not num_is_pair and not point_is_pair:
                winner = self.players[1-self.startingPlayer] + " uzvarēja!"

            self.gameStateBox.gameStateTitle.text = winner 
            self.restoreStartingState()
            return

        self.currentPlayer = 1 - self.currentPlayer
        self.gameStateBox.gameStateTitle.text = self.players[self.currentPlayer] + " iet"

        self.numberBtns = []
        for i in self.gameStateBox.gameState.numberPairs:
            numberBtn = NumberButton(self)
            self.numberBtns.append(numberBtn)
            self.numberListBox.add_widget(numberBtn)
            numberBtn.setup(i)
        
        if not isAiMove:
            self.aiPlayer.updateGameState(self.gameStateBox.gameState)
            Clock.schedule_once(self.aiPlayer.findBestMove, 0)
            Clock.schedule_once(self.numberBtns[self.aiPlayer.bestMoveIndex].numSelect, 1)
        
    def restoreStartingState(self):
        self.gameStateBox.showFinalResult()
        self.startSettingBox.visible = True
        self.gameBox.visible = False
        self.numberListBox.clear_widgets()
        self.numberBtns = []

# Kivi aplikācijas klase
class AIGameApp(App):
    def build(self):
        page = GamePage()
        return page