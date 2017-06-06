'''
Function that takes in two trees of opposite players and draws them out
            
        NOTE: THIS IS A FINNIKY WAY TO DRAW THE TREE AND IT MIGHT TAKE SOME TROUBLE TO GET IT TO WORK
        
needs networkx library and pydotplus library.
both can be installed using pip install

graphviz is a bit tricky: all it does is call an executable that takes a '.dot'
However, there are some gimmicks:
    1) you need to download the graphvyz executables such as dot.exe
    2) you need to install the python graphviz library
    3) you need to add the .exe to path from system variables
    4) If you did steps 1-3 and it doesn't work, try uninstalling pydot and reinstalling it, because sometimes it can't find the .exe unless you do that.

'''

import networkx as nx
import matplotlib.pyplot as plt
import pydot
import graphviz
import numpy as np


'''
first define a directional graph
Define the first node as one of our node objects: that of an empty board, and it's X's turn
iterate through the children of that node, for each child:
        look through nodes of other player for matching board. if found:
            let that found node be the input of "add_node_to_graph"
'''
def add_node_to_graph(digraph,parentNode, playerTree, opponentTree):
    myboard = parentNode.board
    for child in parentNode.children:
        childboard = np.array( myboard)
        childboard [ child[0]][child[1]] = playerTree.player
        childNode = opponentTree.search_for_board( childboard)
        if childNode != False:
            digraph.add_node ( childNode)
            digraph.add_edge ( parentNode, childNode)
            add_node_to_graph ( digraph, childNode, opponentTree, playerTree)
    return    
        
def draw_tree(player1, player2):
    G = nx.DiGraph()
    root_node = player1.knownStates[0]
    G.add_node(root_node)
    add_node_to_graph( G, root_node, player1,player2)
    pos = nx.nx_pydot.pydot_layout(G, prog='dot')
    nx.draw(G, pos, with_labels=False, arrows=False)
    plt.savefig('nx_test.png')
    return