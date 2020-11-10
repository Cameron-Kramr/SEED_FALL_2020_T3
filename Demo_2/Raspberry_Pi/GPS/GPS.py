#Author: Cameron Kramr
#11/9/2020
#GPS code takes nodes and relative positions and converts them to 
#Absolute positions

import time
import numpy as np
import numpy.matlib
import pygame as pg
import matplotlib
import matplotlib.pyplot as plt


class GPS_System():
    def __init__(self):
    
        #When system first initializes, need to establish a node as the world node
        self.World_Established = False
        
        #Stores all the seen nodes and their position in the node matrix
        self.Nodes = dict()
        
        #Node Position Matrices
        self.Tnode = np.zeros((3,1,1))    #Node Relative Matrix
        self.Tw = np.zeros((3,1))    #Node Relative to world matrix
        
        #Covariance matrices
        self.Q = np.zeros((3,1,1))
        self.R = np.zeros((3,1,1))
        
        self.K = np.zeros((3,1,1))
        self.P = np.zeros((3,1,1))
        
        self.default_K = 0
        self.default_R = 1
        self.default_Q = 2
        self.default_P = 3
        
    def calc_Tnode(self, nodes):
        for i in nodes:
            for j in nodes:
                if(j != i):
                    diff = np.array(i[1]) - np.array(j[1])
                    self.Tnode[:,self.Nodes[i[0]], self.Nodes[j[0]]] = diff
                    self.Tnode[:,self.Nodes[j[0]], self.Nodes[i[0]]] = -diff

    def update(self, nodes):
        #print(nodes)
        self.add_Nodes(nodes)

        self.calc_Tnode(nodes)
        n = len(self.Nodes)

        for i in range(len(self.Tw)):
            #Variable Matrices:
            Twpk1 = self.Tw[i,:]
            Tnode = self.Tnode[i,:,:]
            Ppk1 = self.P[i,:,:]

            #Static Control Matrices:
            Q = self.Q[i,:,:]
            R = self.R[i,:,:]

            #Take Take Measurements
            Twmk = (1/n*np.ones((n,n)))@Twpk1 - 1/n*np.ones(n)@Tnode

            #Calc error covariance matrix
            Pmk = 1/n*np.ones((n,n))@Ppk1@(1/n*np.ones((n,1))) + Q

            yk = Twpk1 - Twmk
            Kk = Pmk@np.linalg.inv(R + Pmk)

            #Update measurement
            self.Tw[i,:] = Twmk + Kk@yk
            self.P[i,:] = (np.eye(n) - Kk)@Pmk


    def calc_node_Tw(self, nodes, node = (-1,[0,0,0])):
        output = np.zeros((3,1))
        count = len(nodes)
        #Performs simple averaging of all node positions
        for i in nodes:
            if(node[0] != i[0] and i[0] in self.Nodes):
                output[:,0] += (self.Tw[:,self.Nodes[i[0]]] - i[1] + node[1])
            else:
                count -= 1
        #print("DONE CAlculating")
        return output/count

    #Establishes the world
    def Establish_World(self, node):
        if(self.World_Established == False):
            self.Nodes[0] = node[0]
            
            #Node is at it's translation vector
            self.Tw[:,0] = node[1]
            
            #Create proper arrays
            self.Q[:,0,0] = self.default_Q
            self.R[:,0,0] = self.default_R
            self.K[:,0,0] = self.default_K
            self.P[:,0,0] = self.default_P
            
    #adds new node into node dictionary and updates all required matrices
    def add_Nodes(self, nodes):
        for node in nodes:
            #print(node)
            if not node[0] in self.Nodes:
                index = len(self.Nodes)
                self.Nodes[node[0]] = index
                
                #Don't do this if the world isn't established
                if(self.World_Established):
                    self.K = np.insert(np.insert(self.K, index, 0, axis = 1), index, 0, axis = 2)
                    self.R = np.insert(np.insert(self.R, index, 0, axis = 1), index, 0, axis = 2)
                    self.Q = np.insert(np.insert(self.Q, index, 0, axis = 1), index, 0, axis = 2)
                    self.P = np.insert(np.insert(self.P, index, 0, axis = 1), index, 0, axis = 2)
                    self.Tnode = np.insert(np.insert(self.Tnode, index, 0, axis = 1), index, 0, axis = 2)
                    
                    #Add translation vectors
                    self.Tw = np.insert(self.Tw, index, 0, axis = 1)
                    self.Tw[:, index] = self.calc_node_Tw(nodes, node = node)[:,0]
                    
                else:
                    self.World_Established = True
                    self.Tw[:,0] = node[1]
                
                #Set Default Values
                self.K[:,index,index] = self.default_K
                self.R[:,index,index] = self.default_R
                self.Q[:,index,index] = self.default_Q
                self.P[:,index,index] = self.default_P

if __name__ == "__main__":
    node_1 = (1, np.array([14, 6, 0]))
    node_2 = (2, np.array([2, 2, 8]))
    node_3 = (3, np.array([3, 3, 3]))
    node_4 = (4, np.array([1, 2, 4]))
    
    nodes = [node_1, node_2, node_3, node_4]
    
    Global_Pos = GPS_System()
    
    #Global_Pos.add_Nodes(nodes)

    #Global_Pos.calc_Tnode(nodes)
    
    #print(str(Global_Pos.Tnode))
    #print(str(Global_Pos.Tw))

    tests = 1000

    Twks = np.zeros((3,4,tests))
    Twkrs = np.zeros((3,4,tests))

    for i in range(tests):
        node_1_r = (1, np.array(node_1[1]) + np.random.randn(3))
        node_2_r = (2, np.array(node_2[1]) + np.random.randn(3))
        node_3_r = (3, np.array(node_3[1]) + np.random.randn(3))
        node_4_r = (4, np.array(node_4[1]) + np.random.randn(3))

        nodes = [node_1_r, node_2_r, node_3_r, node_4_r]
        Global_Pos.update(nodes)

        Twks[:,:,i] = Global_Pos.Tw
        Twkrs[:,:,i] = np.concatenate((
                    np.array(node_1_r[1]).reshape((3,1)),
                    np.array(node_2_r[1]).reshape((3,1)),
                    np.array(node_3_r[1]).reshape((3,1)),
                    np.array(node_4_r[1]).reshape((3,1))), axis = 1)
        #print("~~~~~~~~~~~~~~~")
        #print(str(Global_Pos.Tw))
        #print(str(Global_Pos.P))
    twkx, = plt.plot(Twks[0,0,:], label = 'Twks: X')
    twkrx, = plt.plot(Twkrs[0,0,:], label = 'Twkrs: X')
    twky, = plt.plot(Twks[1,0,:], label = 'Twks: Y')
    twkry, = plt.plot(Twkrs[1,0,:], label = 'Twkrs: Y')
    twkz, = plt.plot(Twks[2,0,:], label = 'Twks: Z')
    twkrz, = plt.plot(Twkrs[2,0,:], label = 'Twkrs: Z')
    plt.legend(handles = [twkx, twkrx, twky, twkry, twkz, twkrz])
    plt.show()
