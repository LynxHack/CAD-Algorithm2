import heapq
import math
import time
import threading

import itertools
from copy import copy, deepcopy
import random
from colors import COLORS
from collections import deque

import random
import numpy as np
import copy

try:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter 
except ImportError:
    # for Python3
    from tkinter import *   ## notice lowercase 't' in tkinter here
import os

## Takes in a filename and return the created grid and list of routes to be wired
def parseFile(filename):
    with open(filename) as f:
        ## Get general problem information
        info = f.readline().split(' ')
        numcells = int(info[0])
        numconn = int(info[1])
        numrows = int(info[2])
        numcols = int(info[3])

        ## return the info on the sinks
        content = f.readlines()
        data = [x.strip() for x in content]
        nets = []
        for net in data:
            ## skip over empty rows
            if net == '':
                continue
            nets.append(list(map(lambda x: int(x), net.split(' '))))
        return nets, numcells, numconn, numrows, numcols

## Takes in a coordinate, color, and the existing canvas to draw a color in the grid
def drawcell(i, j, color, c):
    # print(sizex*i,sizey*j)
    c.create_rectangle(sizex*i,sizey*j,sizex*(i+1),sizey*(j+1), fill=color)

## Draw a line between two coordinates
def drawline(i1, j1, i2, j2, c):
    x1 = sizey * (2 * i1 + 1) / 2
    x2 = sizey * (2 * i2 + 1) / 2
    y1 = sizex * (2 * j1 + 1) / 2
    y2 = sizex * (2 * j2 + 1) / 2
    print(x1, x2, y1, y2)
    c.create_line(x1, y1, x2, y2, fill='black')

## draw the updated grid colors
def updategrid(grid, c):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            value = grid[i][j]
            colorid = value % len(COLORS)
            if colorid == 0 and value > len(COLORS):
                colorid += 1
            drawcell(i, j, COLORS[colorid], c)

# Draw the connected lines between each cell (not used to prevent overhead)
def updateconn(conn, loc, c):
    for i in range(len(conn)):
        numconn = conn[i][0]
        start = conn[i][1]
        for j in range(2, len(conn[i])):
            # print(i, j, len(conn), len(conn[0]))
            end = conn[i][j]
            print(conn[i], start, end)
            drawline(loc[start][0], loc[start][1], loc[end][0], loc[end][1], c)

# Calculate the half perim of one net
def halfperim(net, loc):
    minx = float('inf')
    maxx = float('-inf')
    miny = float('inf')
    maxy = float('-inf')

    ## iterate through each coord in net and see max and min val
    for i in range(1, len(net)):
        coordx = loc[net[i]][0] 
        coordy = loc[net[i]][1]
        minx = min([coordx, minx])
        maxx = max([coordx, maxx])
        miny = min([coordy, miny])
        maxy = max([coordy, maxy])

    return (maxx - minx) + (maxy - miny)

## goes through all the nets and calculate the sum of cost
def getcost(nets, loc):
    sum = 0
    for i in range(len(nets)):
        sum += halfperim(nets[i], loc)
    return sum

## Grab a random coordinate from the grid
def getOneCoord(grid):
    i1 = random.sample(range(0, len(grid)), 1)[0]
    j1 = random.sample(range(0, len(grid[0])), 1)[0]
    return [i1, j1]

## Grab two random coordinates from the grid
def getTwoCoords(grid):
    i1 = random.sample(range(0, len(grid)), 1)[0]
    i2 = random.sample(range(0, len(grid)), 1)[0]
    j1 = 0
    j2 = 0

    ## if same row is picked make sure two distinct columns are picked
    if i1 == i2:
        cols = random.sample(range(0, len(grid[0])), 2)
        j1 = cols[0]
        j2 = cols[1]
    ## Otherwise pick any other two columns
    else:
        j1 = random.sample(range(0, len(grid[0])), 1)[0]
        j2 = random.sample(range(0, len(grid[0])), 1)[0]
    return [[i1, j1], [i2, j2]]

## First randomize location of all placements (numcells), 
def initplacement(grid):
    indices = random.sample(range(0, len(grid) * len(grid[0])), numcells)
    for k in range(len(indices)):
        i = int(indices[k] / len(grid[0]))
        j = int(indices[k] % len(grid[0]))
        grid[i][j] = k
        locations[k] = [i, j]
    return locations

## Go through sim anneal iterations
def simAnneal(grid, nets, c):
    ## first place the grid and get the locations
    loc = initplacement(grid)
    ## temperature is between 0 and 1 non inclusive
    temp = numcells
    # t0 = temp
    ## rate at which temp decreases, lower is faster
    alpha = 0.999
    # k = 1

    num_noswaps = 0
    currcost = getcost(nets, loc)

    ## Iterate until end condition
    while True:
        # end condition
        if num_noswaps > 1000:
            break

        ## Choose two random cells to swap
        coords = getTwoCoords(grid)
        
        samp1 = coords[0]
        samp2 = coords[1]

        print("Cost: ", currcost, "Temp: ", temp, num_noswaps)
        toswap = [0, 0]
        toswap[0] = grid[samp1[0]][samp1[1]]
        toswap[1] = grid[samp2[0]][samp2[1]]
        
        ## redo if both are just blank cells
        if toswap[0] == 0 and toswap[1] == 0:
            continue

        ## perform swap of coordinates
        loc[toswap[0]] = samp2
        loc[toswap[1]] = samp1

        ## calculate cost delta, if new placement - old, do a swap first, 
        # swap back later if needed
        newcost = getcost(nets, loc)
        deltac = newcost - currcost
        r = random.random()

        ## See if should swap
        if r < np.exp(-deltac/temp):
            ## swap it in the grid officially
            t = grid[samp1[0]][samp1[1]]
            grid[samp1[0]][samp1[1]] = grid[samp2[0]][samp2[1]]
            grid[samp2[0]][samp2[1]] = t

            ## rerender the graphics just for the two cells, don't need to rerender everything
            color1 = toswap[1] % len(COLORS)
            color2 = toswap[0] % len(COLORS)
            if color1 == 0 and toswap[1] > len(COLORS):
                color1 += 1
            if color2 == 1 and toswap[0] > len(COLORS):
                color2 += 1
            if graphicsEnabled:
                drawcell(samp1[0], samp1[1], COLORS[color1], c)
                drawcell(samp2[0], samp2[1], COLORS[color2], c)

            ## update the new cost
            if newcost != currcost:
                num_noswaps = 0
                currcost = newcost
            else:
                num_noswaps += 1
        else:
            ## swap assignment back, don't want this swap
            loc[toswap[0]] = samp1
            loc[toswap[1]] = samp2
            num_noswaps += 1

        ## reduce temperature via constant scaling (Oldenburg)
        temp *= alpha

        ## reduce temperature via inverse log schedule
        # temp = temp / math.log(k+1)
        
        ## reduce via exponential decay
        # temp = math.exp(-alpha*k) * t0
        # k += 1
    print("Final cost: ", currcost)
    return currcost

## Main function
if __name__== "__main__":
    filename = sys.argv[1]
    graphicsEnabled =  True
    if len(sys.argv) > 2:
        graphicsEnabled = sys.argv[2]

    nets, numcells, numconn, numrows, numcols = parseFile("./ass2_files/"+filename+".txt")

    root = Tk()

    grid = [[0 for x in range(numcols)] for y in range(numrows)]
    sizex = 1000/numcols
    sizey = 500/numrows
    locations = [0] * (numcells)


    # set up white grids
    frame = Frame(root, width=1000, height=1000)
    frame.pack()
    c = Canvas(frame, bg='white', width=1000, height=1000)
    c.focus_set()
    c.pack()

    # Run algorithm in background via a thread
    updategrid(grid, c)

    thread = threading.Thread(target = simAnneal, args = (grid, nets, c))
    thread.start()

    # simAnneal(grid)
    # print(locations)
    updategrid(grid, c)
    root.mainloop()


