# Simple Pong in Python 3 for Beginners
# By Maxwell Diekhoff
# Part 1: Getting started

import turtle

wn = turtle.Screen()
wn.title("Pong By Maxwell Diekhoff")
wn.bgcolor("black")
wn.setup(width=800, height=600)
wn.tracer(0)



# Main game loop
while True:
    wn.update()