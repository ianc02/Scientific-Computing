from .agent import Lobster, Boat, Heat_Spot, Home, Ocean
import random
from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


class World(Model):
    def __init__(self, height=53, width=53, num_lobsters=300, num_boats=82, movement=0.3, density=0.6, sim_length=30):
        super().__init__()
        # All the params for the model
        self.height = height
        self.width = width
        self.density = density
        self.lobster = num_lobsters
        self.boat = num_boats
        self.sim_length = sim_length
        self.movement = movement

        # Holds all the local lobsters and boats in the model
        self.lobster_loc = []
        self.all_boat_loc = []
        self.small_boat_loc = []
        self.big_boat_loc = []
        self.heat_spot_loc = []

        # Advances and Plots out the model
        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(height, width, torus=False)
        self.dc_lobster = DataCollector({"Lobster": lambda m: self.lobster_count})
        self.dc_big = DataCollector({"Big": lambda m: self.big_count})
        self.dc_small = DataCollector({"Small": lambda m: self.small_count})

        self.lobster_count = 0
        self.big_count = 0
        self.small_count = 0

        port1 = (13, 0)
        port2 = (26, 0)
        port3 = (39, 0)

        Port1 = self.big_port = Home(self.next_id(), port1, self, "big")
        self.grid.place_agent(Port1, port1)
        self.schedule.add(Port1)
        Port2 = self.big_port = Home(self.next_id(), port2, self, "big")
        self.grid.place_agent(Port2, port2)
        self.schedule.add(Port2)
        Port3 = self.big_port = Home(self.next_id(), port3, self, "big")
        self.grid.place_agent(Port3, port3)
        self.schedule.add(Port3)

        for (contents, x, y) in self.grid.coord_iter():
            cell = Ocean(self.next_id(), (x, y), self)
            self.grid.place_agent(cell, (x, y))
            self.schedule.add(cell)
        for i in range(self.width):
            new_loc = (i, 3)
            heat = Heat_Spot(self.next_id(), self, new_loc)
            self.grid.place_agent(heat, new_loc)
            self.schedule.add(heat)


        for boat in range(self.boat):
            new_loc = (random.randint(0, self.width-1), random.randint(0, 3))
            r = random.random()
            x = random.random()
            if x < .33:
                new_boat = Boat(self.next_id(), new_loc, self, Port1)
            elif x < .66:
                new_boat = Boat(self.next_id(), new_loc, self, Port2)
            else:
                new_boat = Boat(self.next_id(), new_loc, self, Port3)
            if r < self.density:
                new_boat.size = "Small"
                self.small_boat_loc.append(new_boat)
            elif r > self.density:
                new_boat.size = "Big"
                self.big_boat_loc.append(new_boat)
            self.grid.place_agent(new_boat, new_loc)
            self.schedule.add(new_boat)

        for lobster in range(self.lobster):
            new_loc = (random.randint(0, self.height-1), random.randint(4, self.height-1))
            new_lob = Lobster(self.next_id(), new_loc, self)
            self.grid.place_agent(new_lob, new_loc)
            self.schedule.add(new_lob)

        self.running = True

    def size(self):
        return self.width
    def step(self):
        """
        Advance the model by one step.
        """
        self.schedule.step()
        self.count_lobster()
        # If the model passes the simulation length the simulation ends
        self.dc_lobster.collect(self)
        self.dc_big.collect(self)
        self.dc_small.collect(self)
        if self.schedule.time == self.sim_length:
            for agent in self.schedule.agents:
                if type(agent) == Boat:
                    agent.in_storage()
            self.dc_lobster.collect(self)
            self.dc_big.collect(self)
            self.dc_small.collect(self)
            self.running = False




    def count_type(self, agent_condition):
        """
        Helper method to count boats and lobsters in a given model.
        """
        count = 0
        for agent in self.schedule.agents:
            if agent.state == agent_condition:
                count += 1
        return count

    def count_lobster(self):
        self.lobster_count = 0
        for x in range(self.width):
            for y in range(self.height-1):
                spot_agents = self.grid.get_cell_list_contents([(x, y)])
                for agent in spot_agents:
                    if type(agent) == Lobster:
                        if agent.state == "Wander":
                            self.lobster_count += 1
