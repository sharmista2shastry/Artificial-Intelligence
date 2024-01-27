#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 17:27:44 2023

@author: sharmistashastry
"""

"""
Each sudoku board is represented as a dictionary with string keys and
int values.
e.g. my_board['A1'] = 8
"""

import sys
import time
import statistics

ROW = 'ABCDEFGHI'
COL = '123456789'

class CSP:
    def __init__(self, board):
        self.board = board
        self.variables = list(board.keys())
        self.domains = {}
        for cell in self.variables:
            if board[cell] == 0:
                self.domains[cell] = [i for i in range(1, 10)]
            else:
                self.domains[cell] = [board[cell]]
        self.constraints = self.getConstraints()

    def getConstraints(self):
        """Returns a list of constraints for the Sudoku puzzle."""
        constraints = []
        for cell in self.variables:
            for neighbor in self.getNeighbors(cell):
                if neighbor != cell:
                    constraints.append((cell, neighbor))
        return constraints

    def getNeighbors(self, cell):
        """Returns a list of neighbors of the cell."""
        neighbors = []
        for row in ROW:
            for col in COL:
                if row == cell[0] or col == cell[1] or ((ROW.index(row) // 3) == (ROW.index(cell[0]) // 3) and (COL.index(col) // 3) == (COL.index(cell[1]) // 3)):
                    neighbor = row + col
                    if neighbor != cell:
                        neighbors.append(neighbor)
        return neighbors

def print_board(board):
    """Helper function to print board in a square."""
    print("-----------------")
    for i in ROW:
        row = ''
        for j in COL:
            row += (str(board[i + j]) + " ")
        print(row)
    
            
def board_to_string(board):
    """Helper function to convert board dictionary to string for writing."""
    ordered_vals = []
    for r in ROW:
        for c in COL:
            ordered_vals.append(str(board[r + c]))
    return ''.join(ordered_vals)


def findEmptySpaces(board):
    """Takes a board and returns a list of empty spaces."""
    empty_spaces = []
    for row in ROW:
        for col in COL:
            if board[row + col] == 0:
                empty_spaces.append((row, col))
    return empty_spaces

def valid_values(board, row, col):
    """Takes a board, row, and column and returns a list of valid values for the cell."""
    values = set(range(1, 10))
    for i in range(9):
        values.discard(board[ROW[i] + col])
        values.discard(board[row + COL[i]])
    box_row = (ROW.index(row) // 3) * 3
    box_col = (COL.index(col) // 3) * 3
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            values.discard(board[ROW[i] + COL[j]])
    return list(values)

def mrv(board):
    """Takes a board and returns the row and column of the cell with the minimum remaining values."""
    empty_spaces = findEmptySpaces(board)
    if len(empty_spaces) == 0:
        return None
    def count_valid_values(cell):
        return len(valid_values(board, cell[0], cell[1]))
    return min(empty_spaces, key=count_valid_values)

def isRowSafe(board, row, value):
    """Takes a board, row, and value and returns True if the value is safe to place in the row, False otherwise."""
    for i in range(9):
        if board[row + COL[i]] == value:
            return False
    return True

def isColSafe(board, col, value):
    """Takes a board, column, and value and returns True if the value is safe to place in the column, False otherwise."""
    for i in range(9):
        if board[ROW[i] + col] == value:
            return False
    return True

def isGridSafe(board, row, col, value):
    """Takes a board, row, column, and value and returns True if the value is safe to place in the 3x3 grid, False otherwise."""
    box_row = (ROW.index(row) // 3) * 3
    box_col = (COL.index(col) // 3) * 3
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if board[ROW[i] + COL[j]] == value:
                return False
    return True

def isSafe(board, row, col, value):
    """Takes a board, row, column, and value and returns True if the value is safe to place in the cell, False otherwise."""
    return isRowSafe(board, row, value) and isColSafe(board, col, value) and isGridSafe(board, row, col, value)

def helper(board):
    """Takes a board and returns solved board."""
    if not findEmptySpaces(board):
        return True
    
    row, col = mrv(board)

    for val in valid_values(board, row, col):
        if isSafe(board, row, col, val):
            board[row + col] = val
            if helper(board):
                return True
        board[row + col] = 0
    
    return False

def AC3(csp):
    """Takes a CSP object and returns True if all constraints are satisfied, False otherwise."""
    queue = csp.constraints.copy()
    while queue:
        (X, Y) = queue.pop(0)
        if recheck(csp, X, Y):
            if len(csp.domains[X]) == 0:
                return False
            for Xk in get_neighbors(csp, X):
                if X != Y:
                    queue.append((X, Y))
    return True

def recheck(csp, X, Y):
    """Takes a CSP object and two variables and returns True if the domain of X is revised, False otherwise."""
    revised = False
    for x in csp.domains[X]:
        is_x_safe = False
        for y in csp.domains[Y]:
            if y != x and isSafe(csp.board, X[0], X[1], y):
                is_x_safe = True
                break
        if not is_x_safe:
            csp.domains[X].remove(x)
            revised = True
    return revised

def get_neighbors(csp, cell):
    """Takes a CSP object and a cell and returns a list of neighbors of the cell."""
    neighbors = []
    for row in ROW:
        for col in COL:
            if row == cell[0] or col == cell[1] or (ROW.index(row) // 3 == ROW.index(cell[0]) // 3 and COL.index(col) // 3 == COL.index(cell[1]) // 3):
                neighbors.append(row + col)
    neighbors.remove(cell)
    return neighbors

def select_unassigned_variable(csp):
    """Takes a CSP object and returns the next unassigned variable to be assigned."""
    unassigned_vars = []
    for cell in csp.variables:
        if csp.board[cell] == 0:
            unassigned_vars.append(cell)
    return min(unassigned_vars, key=lambda cell: len(csp.domains[cell]))

def order_domain_values(csp, cell):
    """Takes a CSP object and a cell and returns the domain of the cell in a specific order."""
    neighbors = get_neighbors(csp, cell)
    def count_safe_values(val):
        return sum(isSafe(csp.board, neighbor[0], neighbor[1], val) for neighbor in neighbors)
    return sorted(csp.domains[cell], key=count_safe_values)

def is_complete(board):
    """Takes a board and returns True if the board is complete, False otherwise."""
    for cell in board:
        if board[cell] == 0:
            return False
    return True

def backtracking(board):
    """Takes a board and returns a solution to the Sudoku puzzle."""
    csp = CSP(board)
    AC3(csp)
    helper(board)
    
    return board

if __name__ == '__main__':
    if len(sys.argv) > 1:
        
        # Running sudoku solver with one board $python3 sudoku.py <input_string>.
        print(sys.argv[1])
        # Parse boards to dict representation, scanning board L to R, Up to Down
        board = { ROW[r] + COL[c]: int(sys.argv[1][9*r+c])
                  for r in range(9) for c in range(9)}       
        solved_board = backtracking(board)
        
        # Write board to file
        out_filename = 'output.txt'
        outfile = open(out_filename, "w")
        if solved_board is not None:
            outfile.write(board_to_string(solved_board))
            outfile.write('\n')
        else:
            print("No solution found for the Sudoku puzzle.")

    else:
        # Running sudoku solver for boards in sudokus_start.txt $python3 sudoku.py

        #  Read boards from source.
        src_filename = 'sudokus_start.txt'
        try:
            srcfile = open(src_filename, "r")
            sudoku_list = srcfile.read()
        except:
            print("Error reading the sudoku file %s" % src_filename)
            exit()

        # Setup output file
        out_filename = 'output.txt'
        outfile = open(out_filename, "w")

        elapsed_times = []
        solved_boards = 0

        # Solve each board using backtracking
        for line in sudoku_list.split("\n"):

            if len(line) < 9:
                continue

            # Parse boards to dict representation, scanning board L to R, Up to Down
            board = { ROW[r] + COL[c]: int(line[9*r+c])
                      for r in range(9) for c in range(9)}

            # Print starting board. TODO: Comment this out when timing runs.
            #print_board(board)

            # Solve with backtracking
            start_time = time.time()
            solved_board = backtracking(board)
            end_time = time.time()
            elapsed_time = end_time - start_time


            # Print solved board. TODO: Comment this out when timing runs.
            #print_board(solved_board)

            # Write board to file
            outfile.write(board_to_string(solved_board))
            outfile.write('\n')

            if is_complete(solved_board):
                elapsed_times.append(elapsed_time)
                solved_boards += 1
            
            num_boards = len(sudoku_list.split("\n")) - 1  # Exclude the last empty line
            if num_boards > 0 and solved_boards > 1:  # Check that at least two boards were solved
                min_time = min(elapsed_times)
                max_time = max(elapsed_times)
                mean_time = statistics.mean(elapsed_times)
                stdev_time = statistics.stdev(elapsed_times)
            else:
                min_time = max_time = mean_time = stdev_time = 0  # Set to 0 if no boards were solved

            with open('README.txt', 'w') as readme:
                readme.write(f'Number of boards solved: {solved_boards}/{num_boards}\n')
                readme.write(f'Minimum time: {min_time:.2f} seconds\n')
                readme.write(f'Maximum time: {max_time:.2f} seconds\n')
                readme.write(f'Mean time: {mean_time:.2f} seconds\n')
                readme.write(f'Standard deviation: {stdev_time:.2f} seconds\n')

            print("Running", line)

        print("Finishing all boards in file.")