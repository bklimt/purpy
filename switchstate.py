
class SwitchState:
    on: set[str]

    def __init__(self):
        self.on = set()

    def turn_on(self, s: str):
        print(f'turning on {s}')
        self.on.add(s)

    def turn_off(self, s: str):
        print(f'turning off {s}')
        if s in self.on:
            self.on.remove(s)

    def toggle(self, s: str):
        print(f'toggling {s}')
        if s in self.on:
            self.on.remove(s)
        else:
            self.on.add(s)

    def is_on(self, s: str) -> bool:
        return s in self.on

    def apply_command(self, s):
        if s[0] == '~':
            self.toggle(s[1:])
        elif s[0] == '!':
            self.turn_off(s[1:])
        else:
            self.turn_on(s)

    def is_condition_true(self, s):
        if s[0] == '!':
            return not self.is_on(s[1:])
        else:
            return self.is_on(s)
