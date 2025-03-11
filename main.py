import random
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.config import Config
from kivy.properties import BoundedNumericProperty

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')

Builder.load_file('InputBox.kv')
Builder.load_file('GameButton.kv')
Builder.load_file('NumberButton.kv')
Builder.load_file('GamePage.kv')

class GameButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class NumberButton(GameButton):
    value = 0
    index = -1
    game_page = None

    def __init__(self, value, gp, **kwargs):
        self.game_page = gp
        self.value = value
        self.count = gp.arrayLength
        self.index = len(gp.numberBtns)-1
        self.text = str(value)
        super().__init__(**kwargs)
    
    def numSelect(self):
        if self.game_page.selected_index == -1:
            self.is_selected = not self.is_selected
            self.game_page.selected_index = self.index
            for nb in self.game_page.numberBtns:
                nb.is_neibor = nb.index <= self.index+1 and nb.index >= self.index-1
        elif self.is_neibor:
            self.is_selected = not self.is_selected
        else:
            print("Inactive")
        

class InputBox(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class GamePage(Widget):
    arrayLength = BoundedNumericProperty(15, min=15, max=25, errorhandler=lambda x: 25 if x > 25 else 15)
    values = []
    points = []
    numberBtns = []
    selected_index = -1

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
        self.values = [random.randint(1,6) for x in range(self.arrayLength)]
        self.numberBtns = []

        for i in self.values:
            numberBtn = NumberButton(i,self)
            self.numberBtns.append(numberBtn)
            self.numberListBox.add_widget(numberBtn)


class AIGameApp(App):
    def build(self):
        page = GamePage()
        return page

if __name__ == "__main__":
    AIGameApp().run()