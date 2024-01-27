from __future__ import division
from __future__ import print_function
import sys
from math import sqrt
import time
import queue as Q
import resource

moves = {'Up':1, 'Down':2, 'Left':3, 'Right':4}
    
class NPuzzle(object):
    
    def __init__(self, board):
        self.board = board
        
    def actions(self, state):
        n = int(sqrt(len(state.board)))
        x = self.board.index(0)
        moves_list = []
        
        if x > n-1:
            moves_list.append('Up')
        if x < len(self.board)-n:
            moves_list.append('Down')
        if x % n != 0:
            moves_list.append('Left')
        if x % n != n-1:
            moves_list.append('Right')
        return moves_list
    
    def reverse_action(self,state):
        n = int(sqrt(len(state.board)))
        x = self.board.index(0)
        move_list = []
        
        if x % n != n-1:
            move_list.append('Right')
        if x % n != 0:
            move_list.append('Left')
        if x < len(self.board)-n:
            move_list.append('Down')
        if x > n-1:
            move_list.append('Up')
        return move_list
    
    def result(self, state, action):
        size = int(sqrt(len(state.board)))
        new = list(state.board)
        x = state.board.index(0)
        if (action == 'Up'):
            new[x], new[x-size] = new[x-size], new[x]
            return NPuzzle(tuple(new))
        if (action == 'Down'):
            new[x], new[x+size] = new[x+size], new[x]
            return NPuzzle(tuple(new))
        if (action == 'Left'):
            new[x], new[x-1] = new[x-1], new[x]
            return NPuzzle(tuple(new))
        if (action == 'Right'):
            new[x], new[x+1] = new[x+1], new[x]
            return NPuzzle(tuple(new))

    def goal_test(self, state, goal):
        return state.board == goal
      
    def path_cost(self, c, state1, action, state2):
        return c + 1
    
    def __repr__(self):
        return str(self.board)
    
    def __eq__(self, other):
        return self.board == other.board and isinstance(other, NPuzzle)
    

class NPuzzleState(object):

    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1
        self.f = self.path_cost + self.manhattan()
    
    def neighbors(self):
        x = []
        for action in self.state.actions(self.state):
            x.append(NPuzzleState(self.state.result(self.state, action), 
                                  self, 
                                  action, 
                                  self.state.path_cost(self.path_cost, 
                                                       self.state,
                                                       action, 
                                                       next)))
        return x
    
    def reverse_neighbors(self):
        x = []
        for action in self.state.reverse_action(self.state):
            x.append(NPuzzleState(self.state.result(self.state, action), 
                                  self, 
                                  action, 
                                  self.state.path_cost(self.path_cost, 
                                                       self.state,
                                                       action, 
                                                       next)))
        return x
    
    def manhattan(self):
        w = int(sqrt(len(self.state.board)))
        return sum((abs(i//w - self.state.board.index(i)//w) + 
                    abs(i%w - self.state.board.index(i)%w) 
                    for i in self.state.board if i != 0))
        
    def __eq__(self, other):
        return self.state.board == other.state.board and isinstance(other, NPuzzleState)

    def __hash__(self): 
        return hash(str(self.state.board))
        
    def __repr__(self):
        return str(self.state.board)
    
    def __lt__(self, other):
        if self.f < other.f:
            return True
        elif self.f == other.f:
            if moves[self.action] < moves[other.action]:
                return True
            elif self.action == other.action:
                return self.depth > other.depth
            return False
        else:
            return False
        
              
class Solver:

    def __init__(self, initialBoard):
        self.nPuzzleState = NPuzzleState(initialBoard)
        self.path_to_goal = []
        self.cost_of_path = 0
        self.nodes_expanded = 0
        self.fringe_size = 0
        self.max_fringe_size = 0
        self.search_depth = 0
        self.max_search_depth = 0
        self.goal = tuple(range(0,len(initialBoard.board)))

    def __success(self, node):
        self.cost_of_path = node.path_cost
        self.search_depth = node.depth
        while node.parent is not None:
            self.path_to_goal.insert(0, node.action)
            node = node.parent       
        return None
        
    def __failure(self):
        print('Cannot find solution')
        return None

    def bfs_search(self):
        frontier = Q.Queue()
        frontier.put(self.nPuzzleState)
        frontier_U_explored = set()
        frontier_U_explored.add(self.nPuzzleState)
        
        while frontier:
            node = frontier.get()
            
            if node.state.goal_test(node.state, self.goal):
                return self.__success(node)
            self.nodes_expanded += 1
            
            for neighbor in node.neighbors():
                if neighbor not in frontier_U_explored:
                    frontier_U_explored.add(neighbor)
                    frontier.put(neighbor)
                    if neighbor.depth > self.max_search_depth:
                        self.max_search_depth = neighbor.depth
            
        return self.__failure
    
    def dfs_search(self):
        frontier = []  
        frontier.append(self.nPuzzleState)
        frontier_U_explored = set()
        frontier_U_explored.add(self.nPuzzleState)
        
        while frontier:
            node = frontier.pop()
            
            if node.state.goal_test(node.state, self.goal):
                return self.__success(node)
            self.nodes_expanded += 1            
            
            for neighbor in node.reverse_neighbors():
                if neighbor not in frontier_U_explored:
                    frontier.append(neighbor)
                    frontier_U_explored.add(neighbor)
                    if neighbor.depth > self.max_search_depth:
                        self.max_search_depth = neighbor.depth
        
        return self.__failure   
    
    from queue import PriorityQueue

    def astar(self, f_limit=sys.maxsize):
        frontier = Q.PriorityQueue()
        frontier.put((0, self.nPuzzleState))
        frontier_set = set()
        frontier_set.add(self.nPuzzleState)
        d = f_limit
    
        while not frontier.empty():
            f, node = frontier.get()
            frontier_set.remove(node)
    
            if node.state.goal_test(node.state, self.goal):
                return node
            self.nodes_expanded += 1
    
            for neighbor in node.neighbors():
                if neighbor not in frontier_set:
                    if neighbor.f < d:
                        frontier.put((neighbor.f, neighbor))
                        frontier_set.add(neighbor)
    
                        if neighbor.depth > self.max_search_depth:
                            self.max_search_depth = neighbor.depth
    
        return False



    def A_star_search(self):
        result = self.astar()
        if result:
            return self.__success(result)
        return self.__failure

def main():

  if len(sys.argv) < 3:
    print("Usage: python puzzle.py [method] [board]")
    sys.exit()
  
  method = sys.argv[1]
  board = sys.argv[2].split(',')
  board = [int(x) for x in board] 
  board = tuple(board)

  game = NPuzzle(board)
  solution = Solver(game)

  start_time = time.time()

  if method == 'bfs':
    solution.bfs_search()
  elif method == 'dfs':  
    solution.dfs_search()
  elif method == 'ast':
    solution.A_star_search()
  
  end_time = time.time()
  running_time = end_time - start_time

  max_ram_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

  with open('output.txt', 'w') as f:
      f.write('path_to_goal:' + str(solution.path_to_goal) +'\n')
      f.write('cost_of_path:' + str(solution.cost_of_path) +'\n')
      f.write('nodes_expanded:' + str(solution.nodes_expanded) + '\n')
      f.write('search_depth:' + str(solution.search_depth) + '\n')
      f.write('max_search_depth:' + str(solution.max_search_depth) + '\n')
      f.write('running_time:' + str(running_time) + '\n')
      f.write('max_ram_usage:' + str(max_ram_usage) + '\n')

if __name__ == '__main__':
  main()