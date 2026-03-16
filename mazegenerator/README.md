MazeGenerator
Description

MazeGenerator is a reusable class for generating and solving mazes.
The generator creates a grid-based maze using a Depth-First Search (DFS) algorithm and stores the maze internally as a bit-masked integer matrix.

If the maze size is large enough, the generator embeds a "42" logo pattern in the center of the maze. The pattern is carved directly into the maze and connected to the generated paths.

The class can also:

Generate perfect mazes (single unique solution)

Generate imperfect mazes (extra paths added)

Solve the maze using Breadth-First Search (BFS)

Export the maze, entry/exit and solution to a file.

Installation

If the class is distributed as a package:

pip install poneraqui.tar

Or place maze_generator.py inside your project and import it directly.

Usage
Import the class
from maze_generator import MazeGenerator
Create an instance
maze = MazeGenerator(
    width=20,
    height=20,
    entry=(0, 0),
    exit_pt=(19, 19),
    output_file="maze.txt",
    perfect=True,
    seed=42
)
Generate the maze
maze.generate()

This creates the maze grid using Depth-First Search with backtracking.

If the maze is larger than 15×15, a "42" logo pattern will automatically be placed in the center.

Solve the maze
solution = maze.solve()
print(solution)

The solver uses Breadth-First Search (BFS) to find the shortest path from the entry to the exit.

The returned solution is a string containing movement directions:

N = North
E = East
S = South
W = West

Example:

EESSSWNN
Save maze to file
maze.save()

The output file will contain:

The maze grid encoded in hexadecimal

The entry coordinates

The exit coordinates

The solution path

Example file structure:

F7BD...
8A3C...
...

0,0
19,19
EESSWN...
Regenerate the maze

To reset the generator and create a new maze with a new random seed:

maze.regenerate()
maze.generate()

This clears the grid and initializes the generator again.

Maze Generation Algorithm

The maze is generated using Depth-First Search (DFS) with a stack:

Start from the entry cell

Randomly choose an unvisited neighbor

Remove the wall between the two cells

Push the new cell to the stack

Backtrack when no neighbors are available

This produces a perfect maze where every cell is reachable and there is exactly one path between two points.

If perfect=False, additional random walls are removed using add_paths() to create multiple solutions.

Data Structure

The maze is stored in:

self.grid

A 2D matrix of integers where each integer is a bit mask representing the walls of a cell.

Bit	Direction	Binary
1	North	0001
2	East	0010
4	South	0100
8	West	1000

Example:

15 (1111) → all walls present
14 (1110) → north wall removed

Walls are removed using bitwise operations.

Parameters
Parameter	Type	Default	Description
width	int	—	Width of the maze grid
height	int	—	Height of the maze grid
entry	tuple[int,int]	—	Starting coordinate (x,y)
exit_pt	tuple[int,int]	—	Exit coordinate (x,y)
output_file	str	—	File where the maze and solution will be saved
perfect	bool	True	If True, maze has a single solution
seed	Optional[int]	None	Random seed to reproduce the same maze
Special Feature: "42" Pattern

If the maze size is larger than 15×15, the generator automatically embeds a "42" logo pattern in the center of the maze.

The pattern:

Is carved as predefined cells

Maintains wall consistency with neighbors

Is connected to the rest of the maze by at least one path

This allows the maze to contain a recognizable structure without breaking solvability.