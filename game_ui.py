import random
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
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

# Spēļu pogu klase standartizētam noformējumam
class GameButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# Ciparu pāris
class NumberButton(BoxLayout):
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

        if self.value[1] == -1:
            self.game_page.removePair(self.index)
            self.game_page.values.pop(self.index)
            self.game_page.log(f"Removing solo number -> {self.value[0]}")
            #self.game_page.addPoints(-1)
    
    def numSelect(self):
        new_value = self.value[0] + self.value[1]
        self.game_page.log(f"Choosen pair {self.value}, gained {new_value}")
        #self.game_page.addPoints(1)
        if new_value >= 7:
            new_value -= 6
            self.game_page.log(f"New number over 6: {new_value+6} -> {new_value}")
            self.game_page.addPoints(1)
        self.game_page.values[self.index] = (new_value,-1)
        self.game_page.regenerate()

    def update(self, new_index):
        self.index = new_index
        self.count = len(self.game_page.values)*2
        
# Spēļu texta lauka klase standartizētam noformējumam
class InputBox(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# Spēles galvenā "lapa"
class GamePage(Widget):
    arrayLength = BoundedNumericProperty(15, min=15, max=25, errorhandler=lambda x: 25 if x > 25 else 15)
    values = []
    points = []
    numberBtns = []
    point_count = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def lengthInput(self, text):
        try:
            self.arrayLength = int(text)
        except:
            self.arrayLength = 0
        self.arrayLenghtInput.text = str(self.arrayLength)
    
    def startGame(self):
        self.arrayLenghtInput.visible = False
        self.startGameBtn.visible = False
        self.gameBox.visible = True

        self.values = [(random.randint(1,6),random.randint(1,6)) for x in range((int)(self.arrayLength/2))]
        if self.arrayLength%2 != 0:
            self.values.append((random.randint(1,6),-1))
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
        self.log(f"Points: {self.point_count} [{("+" if points > 0 else "")}{points}]")
    
    def regenerate(self):
        temp = []
        for i in self.values:
            temp.append(i[0])
            if i[1] != -1:
                temp.append(i[1])
        
        l = len(temp)
        self.values = [(temp[x*2],temp[x*2+1]) for x in range((int)(l/2))]
        if l%2 != 0:
            self.values.append((temp[l-1],-1))
        
        self.numberListBox.clear_widgets()

        if l == 1:
            num_is_pair = temp[0]%2==0
            point_is_pair = self.point_count%2==0
            self.log(f"No more numbers. Final number: [{temp[0]}]. Points: [{self.point_count}]. Winner - {"FIRST" if num_is_pair and point_is_pair else "SECOND" if not num_is_pair and not point_is_pair else "TIE"}")
            return
        
        self.numberBtns = []
        for i in self.values:
            numberBtn = NumberButton(self)
            self.numberBtns.append(numberBtn)
            self.numberListBox.add_widget(numberBtn)
            numberBtn.setup(i)
        
    def log(self, msg):
        self.logBox.text += "\n" + msg

# Kivi aplikācijas klase
class AIGameApp(App):
    def build(self):
        page = GamePage()
        return page