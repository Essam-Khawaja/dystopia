class State:
    def __init__(self, game):
        self.game = game
        self.previousState = None

    def Update(self, deltaTime, actions):
        pass

    def Render(self, surface):
        pass

    def EnterState(self):
        if len(self.game.stateStack) > 1:
            self.previousState = self.game.stateStack[-1]
        self.game.stateStack.append(self)

    def ExitState(self):
        self.game.stateStack.pop()