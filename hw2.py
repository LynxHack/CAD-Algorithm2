import heapq
import math
import time
import threading

import itertools
from copy import copy, deepcopy
import random
from colors import COLORS
from collections import deque

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
        # print(nets, numcells, numconn, numrows, numcols)
        return nets, numcells, numconn, numrows, numcols

# ## Takes in a coordinate, color, and the existing canvas to draw a color in the grid
def drawcell(i, j, color, c):
    # print(sizex*i,sizey*j)
    c.create_rectangle(sizex*i,sizey*j,sizex*(i+1),sizey*(j+1), fill=color)

def drawline(i1, j1, i2, j2, c):
    x1 = sizey * (2 * i1 + 1) / 2
    x2 = sizey * (2 * i2 + 1) / 2
    y1 = sizex * (2 * j1 + 1) / 2
    y2 = sizex * (2 * j2 + 1) / 2
    print(x1, x2, y1, y2)
    c.create_line(x1, y1, x2, y2, fill='black')

# ## draw the updated grid colors
def updategrid(grid, c):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            value = grid[i][j]
            colorid = value % len(COLORS)
            drawcell(i, j, COLORS[colorid], c)

def updateconn(conn, loc, c):
    for i in range(len(conn)):
        numconn = conn[i][0]
        start = conn[i][1]
        for j in range(2, len(conn[i])):
            # print(i, j, len(conn), len(conn[0]))
            end = conn[i][j]
            print(conn[i], start, end)
            drawline(loc[start][0], loc[start][1], loc[end][0], loc[end][1], c)

# filename = sys.argv[1]
filename = "alu2"
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
        # print(coordx, coordy, minx, maxx, miny, maxy)
        minx = min([coordx, minx])
        maxx = max([coordx, maxx])
        miny = min([coordy, miny])
        maxy = max([coordy, maxy])

    ## afterwards, return the final cost of half perimeter
    return (maxx - minx) + (maxy - miny)

## goes through all the nets and calculate the sum of cost
def getcost(nets, loc):
    sum = 0
    for i in range(len(nets)):
        sum += halfperim(nets[i], loc)
    return sum

## First randomize location of all placements (numcells), 
# can just place them all together for now
def initplacement(grid):
    for k in range(numcells):
        row = k % len(grid[0])
        col = int((k - row) / len(grid[0]))
        grid[col][row] = k
        locations[k] = [col, row]
    return locations

def getTwoCoords(grid):
    indices = random.sample(range(0, len(grid) * len(grid[0])), 2)
    j1 = int(indices[0] % len(grid[0]))
    i1 = int((indices[0] - j1) / len(grid))
    j2 = int(indices[1] % len(grid[1]))
    i2 = int((indices[1] - j2) / len(grid))
    return [[i1, j1], [i2, j2]]
## Goes through sim anneal
import random
import numpy as np
import copy
def simAnneal(grid, nets, c):
    ## first place the grid and get the locations
    loc = initplacement(grid)
    ## temperature is between 0 and 1 non inclusive
    temp = 0.6
    ## rate at which temp decreases, lower is faster
    alpha = 0.8
    # k = 0

    num_noswaps = 0
    currcost = getcost(nets, loc)

    ## Iterate until end condition
    while True:
        # end condition
        if num_noswaps > 10:
            print("Final cost: ", currcost)
            return currcost

        ## Choose two random cells to swap -> ex. [23, 56] TODO, fix this
        # toswap = random.sample(range(1, numcells), 2)
        coords = getTwoCoords(grid)
        
        samp1 = coords[0]
        samp2 = coords[1]
        toswap = [0, 0]

        ## check if swapping two cells, or just a cell with an empty
        bothcells = True

        if grid[samp1[0]][samp1[1]] == 0 and grid[samp2[0]][samp2[1]] == 0:
            continue
        elif grid[samp1[0]][samp1[1]] != 0 and grid[samp2[0]][samp2[1]] != 0:
            toswap[0] = grid[samp1[0]][samp1[1]]
            toswap[1] = grid[samp2[0]][samp2[1]]
            t = loc[toswap[0]]
            loc[toswap[0]] = loc[toswap[1]]
            loc[toswap[1]] = t
        elif 
        ## calculate cost delta, if new placement - old, do a swap first, 
        # swap back later if needed
        # newloc = copy.deepcopy(loc)
        # t = loc[toswap[0]]
        # loc[toswap[0]] = loc[toswap[1]]
        # loc[toswap[1]] = t

        newcost = getcost(nets, loc)
        deltac = newcost - currcost
        r = random.random()

        ## See if should swap
        if r < np.exp(-deltac/temp):
            # loc = newloc
            ## swap it in the grid officially
            pt1 = loc[toswap[0]]
            pt2 = loc[toswap[1]]
            print(pt1, pt2)
            t = grid[pt1[0]][pt1[1]]
            grid[pt1[0]][pt1[1]] = grid[pt2[0]][pt2[1]]
            grid[pt2[0]][pt2[1]] = t

            ## rerender the graphics just for the two cells, don't need to rerender everything
            drawcell(pt1[0], pt1[1], COLORS[toswap[1]], c)
            drawcell(pt2[0], pt2[1], COLORS[toswap[0]], c)
            # updategrid(grid, c)

            currcost = newcost
            num_noswaps = 0
        else:
            ## swap assignment back, don't want this wap
            if bothcells:
                t = loc[toswap[0]]
                loc[toswap[0]] = loc[toswap[1]]
                loc[toswap[1]] = t
                num_noswaps += 1
            else:

        
        ## reduce temperature via constant scaling (Oldenburg)
        temp *= alpha



        ## reduce temperature exponential decay (to be tested)
        ## temp = temp / log(k+1)
        ## k += 1

# result = simAnneal(grid, nets)
# updateconn(nets, locations, c)

thread = threading.Thread(target = simAnneal, args = (grid, nets, c))
thread.start()

# simAnneal(grid)
# print(locations)
updategrid(grid, c)
root.mainloop()


