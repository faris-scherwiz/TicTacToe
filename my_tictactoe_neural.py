'''
June 3: I want it to be stable: train by itself, then play against me. save and load.
when it plays agaist me, it should just pick the highest values. no exploration.
there are 255168

June4: I don't want any hard work, just be able to play X as well as O.
and add exception handling for the user input.
also add an option to exit game
add the computer shows all its possible moves and their values when playing a human

I want to make it such that in less than 10,000 games, both my X and O are unbeatable.
draw is the best you can get, and they always go for a victory if one is attainable.

things to add:
    1) ability to play against O
    2) print its children and their weights -> this will help me see how it thinks

    
More advanced:
    1) code optimization with cython?
    2) changing reward function depending on... depth?
    3) pruning: once one option meets certain conditions, stop testing the others
    4) how to grow a late-game database and attach it to the tree to destroy or reward certain nodes
    5) rollout by creating a new tree at the node, simulating games at its 
    

observations:
    1) there are games where there are 2 possible choices that will lead to a win, so computer is equally likely to choose either.
    it should choose the shorter one, where victory is guaranteed in the least amount of moves? This happens a lot.
    2) with just 2000 games, my X neural is unbeatable. with random rollout. what about my X?
    3) trained with 1000 games, O still plays terribly. X plays OK, it picks mid, but late game it reaches past its tree depth and picks randomly.
    
Even if I increase the rewards as a function of depth, it won't fix the problem of unknown parts of the tree being bad.
I need to prune much more than I'm creating even if it risks that I prune away the 'correct answer'.
    
'''

import random
import numpy as np
from operator import itemgetter
import time
import json
import sys

class tictac:
    def __init__ (self):
        self.board = np.zeros((3,3))
        self.winner = 0  #a flag that tells us when this game is over, and who won
    def check_winner(self):
        for i in range(3):
            if self.board[0,i] == self.board[1,i] == self.board[2,i] != 0:
                self.winner = self.board[1,i]
                return
            elif self.board[i,0] == self.board[i,1] == self.board[i,2] != 0:
                self.winner = self.board[i,0]
                return
        if self.board[0,0] == self.board[1,1] == self.board[2,2] != 0:
            self.winner = self.board[0,0]
            return
        elif self.board[2,0] == self.board[1,1] == self.board[0,2] != 0:
            self.winner = self.board[1,1]
            return      
        elif len(self.board[self.board ==0])==0:
            self.winner = 3
        else:
            self.winner = 0

    def allowed_moves(self):
        row = np.where(self.board==0)[0].tolist()
        col =np.where(self.board==0)[1].tolist()
        return zip(row,col)
     
    def clean_board(self):
        self.board = np.zeros((3,3))
        return
        
    def draw_board(self):
        board_symbols = {0:" ", 1:"X", 2:"O"}
        print ( '///////////////')
        print('    |    |')
        print(' ' + board_symbols[self.board[0][0]] + '  | ' + board_symbols[self.board[0][1]] + '  | ' + board_symbols[self.board[0][2]])
        print('    |    |')
        print('-----------')
        print('    |    |')
        print(' ' + board_symbols[self.board[1][0]] + '  | ' + board_symbols[self.board[1][1]] + '  | ' + board_symbols[self.board[1][2]])
        print('    |    |')
        print('-----------')
        print('    |    |')
        print(' ' + board_symbols[self.board[2][0]] + '  | ' + board_symbols[self.board[2][1]] + '  | ' + board_symbols[self.board[2][2]])
        print('    |    |')
        print ( ' ////////////////')
    
    #make_move(1,(0,2) ) puts an X in the bottom right of the board. No check if that spot was filled or not.
    #robustness: make sure player is either 1 or 2. and make sure move is legal.
    def make_move(self,player,move):
        self.board[move[0]][move[1]] = player
        #self.draw_board()
        self.check_winner()
        return move
        time.sleep(1)
        
        
class tree:
    def __init__(self, game, player):
        self.game = game
        self.player = player
            
        self.sel = True    #while tree is going, this variable tell us if we're still in known regions of the tree
        
        #array of known states, which is actually an array that contains node objects
        self.knownStates = []
        self.shortHistory = [ ]
  
    
    #opponent (2) picks their move randomly from the possible moves. should change this so they would pick a winning move if one exists
    def random_move(self):
        possible_moves = self.game.allowed_moves()
        chosen_move = random.choice(possible_moves)
        self.game.make_move( self.player, chosen_move)
        return chosen_move
        
        #human is player 2
    def human_move(self):
        self.game.draw_board()
        time.sleep(0.5)
        if (self.player == 1):
            human = 2
        else:
            human = 1
        try:
            mymove = input("type your move from (0,0) to (2,2):")
        except:
            self.game.clean_board()
            print "An Error occurred. resetting match"
            sys.exit() 
        
        if (type(mymove) != tuple):
            print "Input must be a tuple, such as (0,1)"
            self.human_move()
            return
        elif ( mymove in self.game.allowed_moves()):
            self.game.make_move(human,mymove)
            return True
        else:
            print "invalid move, try again"
            self.human_move()
            return

        
    #selection should iterate through history, picking nodes with the highest UBC, until we reach an unknown state
    #
    def selection(self):
        for i in self.knownStates:
            #iterate through all possible moves, and pick one with the highest UBC 
            trutharray = (i.board == self.game.board)
            if ( trutharray.all() ):
                bestMoveIndex = i.UBC()    # 'i' is a node. returns the move with the highest UBC.
                self.shortHistory.append( (i,bestMoveIndex) )
                self.game.make_move( self.player, i.children[bestMoveIndex])
                return True
                break
        self.sel = False
        self.expand()
        return False
        
    def select_best(self):
        for i in self.knownStates:
            #iterate through all possible moves, and pick one with the highest UBC 
            trutharray = (i.board == self.game.board)
            if ( trutharray.all() ):
                print zip( i.children, i.values.tolist())
                bestMoveIndex = i.best_move()    # 'i' is a node. returns the move with the highest UBC.
                self.shortHistory.append( (i,bestMoveIndex) )
                self.game.make_move( self.player, i.children[bestMoveIndex])
                return True
                break
        self.sel = False
        self.expand()
        return False
             
        #add current state to knownStates, thus we now know its children and their v values.
        #pick the child with the highest value               
    def expand(self):
        newNode = node(self.game)
        self.knownStates.append(newNode)
        bestMoveIndex = newNode.UBC()
        self.shortHistory.append( (newNode,bestMoveIndex) )
        self.game.make_move( self.player, newNode.children[bestMoveIndex])
        self.exp = False
              
    '''
    Pick a move at random from list of possible moves.
    Can be improved by watching for any winning moves and grabbing those.
    '''  
    def rollout(self):
        return self.random_move()

    '''
    Iterate through short history array, changing the value of each node in it
    '''
    def back_propagate(self):
        result = self.game.winner
        modifier = 0.0
        if (result == 3):
            #print "result is a draw"
            modifier = 0.5
        elif (result == self.player):
            #print "Player %d wins"%self.player
            modifier = 1.0
        elif(result != self.player):
            #print "Player %d loses"%self.player
            modifier = -1.0
                
        for visitedNode,childIndex in self.shortHistory:
            #print "adjusting values of node %d by %.3f"%(childIndex, modifier)
            visitedNode.values[childIndex] = visitedNode.values[childIndex] + modifier
        self.shortHistory = []
        self.game.clean_board()
        self.sel = True
        self.exp = False
        return
    
    '''
    Selection, expand, rollout, propagate
    first, check if this tree is player 1 or 2.
    if it's player 2, let human start first, then proceed as if it's player 1.
    however, we need to take care of the fact that 'human' needs to write
    
    '''
    def play_human(self):
        if self.player == 2:
            self.human_move()
        while True:
            if (self.game.winner == 0):
                self.take_turn(best=True)
            if (self.game.winner == 0):
                self.human_move()
            else:
                break
        self.game.draw_board()
        self.back_propagate()
        self.game.winner = 0

    '''
    makes 1 move on the board, following the tree
    if best is True, then UBC formula won't be followed and the highest value choices will be taken
    '''         

    def take_turn(self, best=False):
        if self.sel == True:
            if best == True:
                return self.select_best()
            else:
                return self.selection()
        else:
            return self.rollout()
            
    '''Save the known nodes and values to the file ``filename``.'''      
    def save_tree(self, filename):
        data = { "boards": [], "children":[], "values":[], "n":[]}
        for node in self.knownStates:
            data["boards"].append ( node.board.tolist())
            data["children"].append( node.children)
            data["values"].append( node.values.tolist())
            data["n"].append ( node.n.tolist() )
        f = open(filename, "w")
        json.dump(data, f)
        f.close()
        
        

 #node is a known position on the 3x3 plane, with a value, and known possible moves   
 #in the initialization of a node I should get all possible moves and assign a value to each one   
 #values are random numbers taken from standard distribution, absolute values.
class node:
    def __init__(self,game):
        self.board = np.array(game.board)
        self.children = game.allowed_moves()
        self.num_of_children = len (self.children)
        self.values = abs( np.random.randn (self.num_of_children,1) )
        self.n = np.zeros_like( self.values)    #number of times child was used
        self.t = max(1,self.n.sum() )         #number of times this parent was used
        self.c = np.sqrt(2)
        
    #find UBC for all child nodes, and return the move with the highest UBC
    def UBC(self):
        first_term  = np.divide ( self.values,self.n,out=np.ones_like(self.values),where=self.n!=0)
        second_term = self.c * np.divide ( np.log(self.t), self.n, out=np.ones_like(self.n),where=self.n!=0)
        upperbounds = first_term + second_term
        bestMoveIndex = np.argmax(upperbounds)
        self.n[ bestMoveIndex] = self.n[bestMoveIndex] + 1
        self.t = self.n.sum()
        return bestMoveIndex
    
    def best_move(self):
        bestMoveIndex = np.argmax(self.values)
        self.n[ bestMoveIndex] = self.n[bestMoveIndex] + 1
        self.t = self.n.sum()
        return bestMoveIndex

'''
Load a tictac tree from the file ``filename``.  Returns an instance of Tree.
'''
def load_tree( filename, player):

    f = open(filename, "r")
    data = json.load(f)
    f.close()
    g = tictac()
    mytree = tree(g,player)
    n=0
    for oneState in data["boards"]:
        newnode = node ( mytree.game)
        newnode.board  = np.array( oneState )
        newnode.children = [ (a,b) for a,b in data["children"][n] ]
        newnode.values = np.array( data["values"][n] )
        newnode.n = np.array( data["n"][n] )
        mytree.knownStates.append(newnode)
        n = n + 1
    return mytree
    

def play_game(game, player1, player2):
    while True:
        if ( game.winner == 0):
            player1.take_turn()
        if (game.winner== 0):
            player2.take_turn()
        else:
            break
    player1.back_propagate()
    player2.back_propagate()
    game.winner = 0
    
g = tictac()
p1 = tree(g,1)
p2 = tree(g,2)
    