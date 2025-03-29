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
    
    def numSelect(self):
        self.game_page.gameStateBox.lastMoveNum1.text = str(self.value[0])
        self.game_page.gameStateBox.lastMoveNum2.text = str(self.value[1])
        if self.value[1] == 0:
            self.game_page.addPoints(-1)
            self.game_page.values[self.index] = (-1,-1)
        else:
            new_value = self.value[0] + self.value[1]
            self.game_page.addPoints(1)
            if new_value >= 7:
                new_value -= 6
                self.game_page.addPoints(1)
            self.game_page.values[self.index] = (new_value,-1)
        self.game_page.regenerate()
        self.game_page.gameStateBox.update(self.game_page.point_count, self.value)

    def update(self, new_index):
        self.index = new_index
        self.count = len(self.game_page.values)*2
        
# Spēļu texta lauka klase standartizētam noformējumam
class InputBox(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class GameStateBox(BoxLayout):
    totalPoints = 0
    lastMove = (0, 0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

    def update(self, totalPoints, lastMove):
        self.totalPoints = totalPoints
        self.lastMove = lastMove
        self.totalPointsBox.text = "Punktu skaits: " + str(self.totalPoints)
        self.lastMoveBox.text = "Pēdējais gājiens: " + str(self.lastMove)


# Spēles galvenā "lapa"
class GamePage(Widget):
    arrayLength = BoundedNumericProperty(5, min=5, max=25, errorhandler=lambda x: 25 if x > 25 else 5)
    players = { 
        0:'Cilvēks',
        1:'Dators' 
    }
    values = []
    points = []
    numberBtns = []
    point_count = 0
    startingPlayer = 0
    gameHistory = []
    currentPlayer = 0

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
        
        if self.dropdownStartingPlayer.text == self.players[0]:
            self.startingPlayer = 0
        else:
            self.startingPlayer = 1

        self.gameStateBox.gameStateTitle.text = self.players[self.startingPlayer] + " gājiens"
        self.values = [(random.randint(1,6),random.randint(1,6)) for x in range((int)(self.arrayLength/2))]
        if self.arrayLength%2 != 0:
            self.values.append((random.randint(1,6),0))
        self.numberBtns = []

        for i in self.values:
            numberBtn = NumberButton(self)
            self.numberBtns.append(numberBtn)
            self.numberListBox.add_widget(numberBtn)
            numberBtn.setup(i)

    def removePair(self, numIndex):
        self.numberListBox.remove_widget(self.numberBtns[numIndex])
        self.numberBtns.remove(self.numberBtns[numIndex])
        i = 0
        for nb in self.numberBtns:
            nb.update(i)
            i += 1

    def addPoints(self, points):
        self.point_count += points
    
    def regenerate(self):
        temp = []
        for i in self.values:
            if i[0] > 0:
                temp.append(i[0])
            if i[1] > 0:
                temp.append(i[1])
        
        l = len(temp)
        self.values = [(temp[x*2],temp[x*2+1]) for x in range((int)(l/2))]
        if l%2 != 0:
            self.values.append((temp[l-1],0))
        
        self.numberListBox.clear_widgets()

        if l == 1:
            num_is_pair = temp[0]%2==0
            point_is_pair = self.point_count%2==0
            winner = "Neizšķirts!"
            if num_is_pair == point_is_pair:
                winner = self.players[self.startingPlayer] + " uzvarēja!"
                self.updateGameHistory(self.startingPlayer)
            elif not num_is_pair and not point_is_pair:
                winner = self.players[1-self.startingPlayer] + " uzvarēja!"
                self.updateGameHistory(1-self.startingPlayer)

            self.gameStateBox.gameStateTitle.text = winner 
            self.gameHistory.append(winner)
            self.restoreStartingState()
            return
        
        self.currentPlayer = 1 - self.currentPlayer
        self.gameStateBox.gameStateTitle.text = self.players[self.currentPlayer] + " gājiens"
        self.numberBtns = []
        for i in self.values:
            numberBtn = NumberButton(self)
            self.numberBtns.append(numberBtn)
            self.numberListBox.add_widget(numberBtn)
            numberBtn.setup(i)
        
    def updateGameHistory(self, winner):
        self.gameHistory.append({'winner': winner, 'points': self.point_count})

    def restoreStartingState(self):
        self.gameStateBox.gameStateBody.visible = False
        self.startSettingBox.visible = True
        self.gameBox.visible = False
        self.point_count = 0
        self.values = []
        self.numberListBox.clear_widgets()
        self.numberBtns = []

# Kivi aplikācijas klase
class AIGameApp(App):
    def build(self):
        page = GamePage()
        return page