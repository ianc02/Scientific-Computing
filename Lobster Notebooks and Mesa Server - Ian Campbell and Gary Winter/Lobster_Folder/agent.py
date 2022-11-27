import math
import random

from mesa import Agent
from mesa.time import SimultaneousActivation


def get_distance(pos_1, pos_2):
    """ Get the distance between two point

    Args:
        pos_1, pos_2: Coordinate tuples for both points.

    """
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx ** 2 + dy ** 2)

class Ocean(Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos

    def get_pos(self):
        return self.pos

class Lobster(Agent):

    def __init__(self, unique_id, pos, model, moore=True):
        super().__init__(unique_id, model)
        self.pos = pos
        self.state = "Wander"
        self.moore = moore
        self.timer = random.randint(0, 10)
        self.count = 0
        self.counts = [0]
        self.models = model
        self.schedule = SimultaneousActivation(self.models)
        self.turn = 0

    def lob_pos(self):
        return self.pos

    def change_state(self, state):
        self.state = state

    def caught(self):
        if self.state == "Caught":
            self.schedule.remove(self)

    def step(self):
        self.turn += 1
        self.move_north()
        self.count += 1
        self.counts.append(self.count)

    def heat_locater(self):
        heat = [n for n in self.model.grid.get_neighbors(self.pos, self.moore) if type(n) is Heat_Spot]
        for h in heat:
            heat_p = h.track()
            return heat_p

    def move_north(self):
        moves = []
        heat = self.heat_locater()
        if heat is not None:
            next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
            for move in next_moves:
                if move[1] not in heat:
                    moves.append(move)
        if len(moves) == 0:
            return None
        next_move = random.choice(moves)
        self.model.grid.move_agent(self, next_move)
        self.neighbor_move()



    def neighbor_move(self):
        lobsters = [n for n in self.model.grid.get_neighbors(self.pos, self.moore) if type(n) is Lobster]
        for l in lobsters:
            if l.pos[1] > self.pos[1]:
                l.neighbor_move()
        if random.random() < 0.25:
            if self.pos[1]+1 < self.model.size():
                self.model.grid.move_agent(self, (self.pos[0],self.pos[1]+1))


class Boat(Agent):

    def __init__(self, unique_id, pos, model, home, moore=True):
        super().__init__(unique_id, model)
        self.home = home
        self.pos = pos
        self.size = "Small"
        self.state = "Search"
        self.moore = moore
        self.amount = 0
        self.turn = 0
        self.unable = False

    def step(self):
        self.turn += 1
        if self.state == "Search":
            if (self.size == "Small" and self.pos[1]<26) or self.size == "Big":
                if self.pos[1] < 4 + self.turn//5:
                    self.smart_move()
                else:
                    self.random_move()
                if self.catch():
                    if self.able_to_return():
                        self.state = "Return"
            else:
                self.unable = True
                self.state = "Return"
        else:
            if self.pos == self.home.pos:
                if not self.unable:
                    self.state = "Search"
                if self.size == "Big":
                    self.model.big_count += self.amount
                else:
                    self.model.small_count += self.amount
                self.amount = 0

            else:
                self.return_home()


    def able_to_return(self):
        if self.size == "Big" and self.amount == 10:
            return True
        elif self.size == "Small" and self.amount == 5:
            return True
        else:
            return False

    def return_home(self):
        """
        This makes the Boat able to return to Port
        """
        neighbors = [n.get_pos() for n in self.model.grid.get_neighbors(self.pos, self.moore) if type(n) is Ocean]

        # Narrow down to the nearest ones to home
        min_dist = min([get_distance(self.home.pos, pos) for pos in neighbors])
        final_candidates = [
            pos for pos in neighbors if get_distance(self.home.pos, pos) == min_dist
        ]
        self.random.shuffle(final_candidates)
        self.model.grid.move_agent(self, final_candidates[0])


    def catch(self) -> bool:
        neighbors = self.model.grid.get_neighbors(self.pos, self.moore, True)
        for n in neighbors:
            if type(n) == Lobster:
                if n.state == "Wander":
                    self.model.grid.move_agent(self,n.pos)
                    self.amount += 1
                    n.state = "Caught"
                    return True


        return False

    def random_move(self):
        while True:
            try:
                next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
                next_move = random.choice(next_moves)
                self.model.grid.move_agent(self, next_move)
            except:
                pass
            else:
                break

    def smart_move(self):
        x = self.pos[0]
        y = self.pos[1]
        self.model.grid.move_agent(self, (x, y+1))

    def in_storage(self):
        self.model.big_count += self.amount
class Home(Agent):
    """
    The home of the ants, recording how much food has been harvested.
    """

    def __init__(self, unique_id, pos, model, size):
        """
        Records the unique_id with the super, and saves the pos.
        Initializes the food amount to 0.
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.amount = 0
        self.size = size

    def add(self, amount):
        """
        Add the amount to the home amount
        """
        self.amount += amount

    def pos(self):
        return self.pos

    def size(self):
        return self.size


class Heat_Spot(Agent):

    def __init__(self, unique_id, model, pos, moore=True):
        super().__init__(unique_id, model)
        self.moore = moore
        self.pos = pos
        self.count = 4
        self.turn = 0
        self.tracks = [0,1,2,3,4]

    def step(self):
        self.turn += 1
        if self.turn%5 == 0:
            self.model.grid.move_agent(self, (self.pos[0], self.count))
            self.count += 1
            self.tracks.append(self.count)

    def get_pos(self):
        return self.pos

    def track(self):
        return self.tracks