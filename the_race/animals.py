import random

racers = (
    (":alien:", "special"),
    (":ambulance:", "fast"),
    (":baby_chick:", "slow"),
    (":bird:", "fast"),
    (":bug:", "slow"),
    (":cat2:", "fast"),
    (":donkey:", "steady"),
    (":dolphin:", "fast"),
    (":shark:", "steady"),
    (":black_bird:", "fast"),
    (":horse:", "fast"),
    (":horse_racing:", "special"), 
    (":red_car:", "fast"),
    (":blue_car:", "steady"),
    (":race_car:", "fast"),
    (":taxi:", "fast"),
    (":rocketmario:", "special"),
    (":man_bouncing_ball:", "slow"),
    (":man_biking:", "steady"),
    (":man_cartwheeling:", "slow"),
    (":man_in_manual_wheelchair:", "slow"),
    (":man_in_motorized_wheelchair:", "steady"),
    (":runpepe:", "fast"),
    (":woman_running:", "steady"),
    (":polarrun:", "fast"),
    (":edrun:", "steady"),
    (":pom:", "fast"),
    (":scooty:", "fast"),
    (":goose:", "steady"),
    (":danceadhd_girl:", "fast"),
    (":zoom:", "fast"),
    (":runBoi:", "fast"),
    (":kangaroo:", "fast"),
    (":camel:", "steady"),
    (":cactus:", "special"),
    (":chipmunk:", "fast"),
    (":cherries:", "special"),
    (":cow2:", "abberant"),
    (":crab:", "slow"),
    (":crocodile:", "slow"),
    (":dog2:", "steady"),
    (":dove:", "fast"),
    (":dragon:", "special"),
    (":duck:", "slow"),
    (":eagle:", "fast"),
    (":eggplant:", "special"),
    (":elephant:", "abberant"),
    (":fish:", "steady"),
    (":flamingo:", "fast"),
    (":flying_saucer:", "special"),
    (":fire_engine:", "fast"),
    (":ghost:", "special"),
    (":goat:", "slow"),
    (":lizard:", "slow"),
    (":gorilla:", "steady"),
    (":hippopotamus:", "abberant"),
    (":bee:", "fast"),
    (":kangaroo:", "steady"),
    (":leopard:", "predator"),
    (":lobster:", "slow"),
    (":man_biking:", "slow"),
    (":monkey:", "fast"),
    (":ox:", "abberant"),
    (":octopus:", "steady"),
    (":penguin:", "slow"),
    (":pig2:", "slow"),
    (":racehorse:", "fast"),
    (":rainbow:", "special"),
    (":rat:", "fast"),
    (":rhinoceros:", "abberant"),
    (":rooster:", "slow"),
    (":scorpion:", "slow"),
    (":sheep:", "abberant"),
    (":ship:", "abberant"),
    (":snail:", "slow"),
    (":snowman:", "special"),
    (":sunflower:", "special"),
    (":swan:", "slow"),
    (":tiger2:", "predator"),
    (":tractor:", "abberant"),
    (":unicorn:", "special"),
    (":police_car:", "special"),
    (":rabbit2:", "fast"),
    (":whale:", "abberant"),
    (":moyai:", "abberant"),
    (":toilet:", "special"),  
    (":turkey:", "slow"),
    (":turtle:", "slow"),
    (":helicopter:", "special"),
    (":bat:", "fast"),
    (":brain:", "special"),
    (":bread:", "steady"),
)

specials = (
    (":alien:", "special"),
    (":alien:", "special"),
    (":cactus:", "special"),
    (":cherries:", "special"),
    (":dragon:", "special"),
    (":eggplant:", "special"),
    (":flying_saucer:", "special"),
    (":ghost:", "special"),
    (":rainbow:", "special"),
    (":unicorn:", "special"),
    (":police_car:", "special"),
    (":helicopter:", "special"),
    (":brain:", "special"),
    (":toilet:", "special"),  
    (":snowman:", "special"),
    (":sunflower:", "special"),
)

slowboys = (
    (":baby_chick:", "slow"),
    (":bug:", "slow"),
    (":cow2:", "abberant"),
    (":crab:", "slow"),
    (":crocodile:", "slow"),
    (":duck:", "slow"),
    (":goat:", "slow"),
    (":lizard:", "slow"),
    (":hippopotamus:", "abberant"),
    (":lobster:", "slow"),
    (":man_biking:", "slow"),
    (":penguin:", "slow"),
    (":pig2:", "slow"),
    (":rhinoceros:", "abberant"),
    (":rooster:", "slow"),
    (":scorpion:", "slow"),
    (":sheep:", "abberant"),
    (":ship:", "abberant"),
    (":snail:", "slow"),
    (":swan:", "slow"),
    (":tractor:", "abberant"),
    (":whale:", "abberant"),
    (":turkey:", "slow"),
    (":turtle:", "slow"),
    (":moyai:", "abberant"),
)

class Animal:
    def __init__(self, emoji, _type):
        self.emoji = emoji
        self._type = _type
        self.track = "•   " * 20
        self.position = 80
        self.turn = 0
        self.current = self.track + self.emoji

    def move(self):
        self._update_postion()
        self.turn += 1
        return self.current

    def _update_postion(self):
        distance = self._calculate_movement()
        self.current = "".join(
            (
                self.track[: max(0, self.position - distance)],
                self.emoji,
                self.track[max(0, self.position - distance) :],
            )
        )
        self.position = self._get_position()

    def _get_position(self):
        return self.current.find(self.emoji)

    def _calculate_movement(self):
        if self._type == "slow":
            return random.randint(1, 3) * 3
        elif self._type == "fast":
            return random.randint(0, 4) * 3

        elif self._type == "steady":
            return 2 * 3

        elif self._type == "abberant":
            if random.randint(1, 100) >= 85:
                return 5 * 3
            else:
                return random.randint(0, 2) * 3

        elif self._type == "predator":
            if self.turn % 2 == 0:
                return 0
            else:
                return random.randint(1, 6) * 3

        elif self._type == ":unicorn:":
            if self.turn % 3:
                return random.choice([len("blue"), len("red"), len("green")]) * 3
            else:
                return 0

        else:
            if self.turn == 1:
                return 14 * 3
            elif self.turn == 2:
                return 0
            else:
                return random.randint(0, 2) * 3
