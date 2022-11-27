import mesa
from .model import World
from .agent import Lobster, Boat, Heat_Spot, Home, Ocean
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import ModularServer

# If you would rather see pictures, copy and paste code from file "Picture Server"
# into this file in place of current code. The same goes for "Shape Server" with shapes.

def agent_portrayal(agent):
    portrayal = {}
    if type(agent) is Ocean:
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["Color"] = "#00FFFF"
    elif type(agent) is Lobster:
        if agent.state == "Wander":
            portrayal["Shape"] = "circle"
            portrayal["r"] = .5
            portrayal["Color"] = "#FF0000"
            portrayal["Filled"] = "true"
            portrayal["scale"] = 0.9
            portrayal["Layer"] = 1
        else:
            portrayal["Color"] = "#00FFFF"
            portrayal["Shape"] = "rect"
            portrayal["Filled"] = "true"
            portrayal["Layer"] = 0
            portrayal["w"] = 1
            portrayal["h"] = 1

    elif type(agent) is Boat:
        if agent.size == "Big":
            portrayal["Shape"] = "circle"
            portrayal["r"] = 1.5
            portrayal["Color"] = "#008000"
            portrayal["Filled"] = "true"
            portrayal["scale"] = .9
            portrayal["Layer"] = 2
        elif agent.size == "Small":
            portrayal["Shape"] = "circle"
            portrayal["r"] = .8
            portrayal["Color"] = "#000000"
            portrayal["Filled"] = "true"
            portrayal["scale"] = .9
            portrayal["Layer"] = 2
    elif type(agent) is Heat_Spot:
        portrayal["Shape"] = "rect"
        portrayal["h"] = 1.1
        portrayal["w"] = 1.1
        portrayal["Layer"] = 3
        portrayal["Filled"] = "true"
        portrayal["Color"] = "#FFFF00"
    elif type(agent) is Home:
        portrayal["Shape"] = "rect"
        portrayal["h"] = 2
        portrayal["w"] = 2
        portrayal["Layer"] = 2
        portrayal["Filled"] = "true"
        portrayal["Text"] = "Port"
        portrayal["Color"] = "#5D313F"
    return portrayal


# derived from Conway Game of Life
# Make a world that is 30x30, on a 500x500 display.
canvas_element = CanvasGrid(agent_portrayal, 53, 53, 750, 750)

# derived from schelling
model_params = {
    "height": 53,
    "width": 53,
    "movement": UserSettableParameter("slider", "Random Movement", 0.3, 0, 1, 0.1),
    "sim_length": UserSettableParameter("slider", "Simulation Length", 244, 30, 300, 10),
    "density": UserSettableParameter("slider", "Density", 0.5, 0, 1, 0.1)}

server = ModularServer(World, [canvas_element], "Lobster Model", model_params)
