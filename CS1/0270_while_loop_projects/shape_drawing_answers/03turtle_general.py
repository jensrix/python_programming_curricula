import turtle

tommy = turtle.Turtle()

sides = 180 #Change this to change the shape! Lots of sides makes a circle
angle = 360/sides #Calculate the angle you need to turn to make a regular shape with the given number of sides.
side_length = 600/sides #shorten the side length when there are more sides

tommy.speed(1)
tommy.pendown()
tommy.color('green')

#Introduce a loop to shorten our code:
i = 0
while i<sides:
    i = i+1
    tommy.forward(side_length)
    tommy.left(angle)

turtle.done()