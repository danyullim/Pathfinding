import pygame
import math
from queue import PriorityQueue

# Setup of the display
WIDTH = 800
# setting the dimension - this is square
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")
# colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

# keep track of: color, location, width, neighbors, etc.
class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows
	
	# getting the position
	def get_pos(self):
		return self.row, self.col

	# node that is has been visited
	def is_closed(self):
		return self.color == RED

	# node that has not been visited - in the open set?
	def is_open(self):
		return self.color == GREEN

	# avoid black barriers
	def is_barrier(self):
		return self.color == BLACK

	# color of starting node - Point B 
	def is_start(self):
		return self.color == ORANGE

	# color of ending node - Point B
	def is_end(self):
		return self.color == TURQUOISE

	# change color back to white
	def reset(self):
		self.color = WHITE

	# color it red
	def make_closed(self):
		self.color = RED

	# color it green
	def make_open(self):
		self.color = GREEN

	# color it black
	def make_barrier(self):
		self.color = BLACK

	# color it orange
	def make_start(self):
		self.color = ORANGE

	# color it turquoise
	def make_end(self):
		self.color = TURQUOISE

	# color it purple
	def make_path(self):
		self.color = PURPLE

	# drawing on the screen - top left -> bottom right
	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	# updating the barriers 
	def update_neighbors(self, grid):
		# blank list
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		# not at row zero and not a barrier
		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])


		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		# not at column zero and not a barrier
		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	# lt = less than
	def __lt__(self, other):
		return False

# Heuristic function - using manhattan distance
# p1 - point 1, p2 - point 2
def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	# while in the list of came from
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()

# A* algorithm
def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	# add start node with F(h)
	# count - to break ties if 2 nodes in the set has same F(h) value
	open_set.put((0, count, start))
	# from the last visited node
	came_from = {}
	# initialize at infinity
	g_score = {spot: float("inf") for row in grid for spot in row}
	# for the start node - G(h) = 0
	g_score[start] = 0
	# start at infinity 
	f_score = {spot: float("inf") for row in grid for spot in row}
	# for the start node - heuristic b/c to estimate how far we are from the end node
	f_score[start] = h(start.get_pos(), end.get_pos())

	# create set for the priortity queue, so we can check if node is inside of itf
	open_set_hash = {start}

	# if open set is empty
	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		# index at 2 - to access the node
		current = open_set.get()[2]
		# take whatever node that we popped off, then remove out of set
		open_set_hash.remove(current)

		# found the shortest path
		if current == end:
			# found the path
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		# if neighbor is in current.neighbors
		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			# if we found a better way to reach this neighbor, then update/store this path
			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					# if not in, then increment the count
					count += 1
					# put in the new neighbor - with the better path
					open_set.put((f_score[neighbor], count, neighbor))
					# storing the spot
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		# if node we just considered is not the start node, then make it red and close it off
		if current != start:
			current.make_closed()

	# if we did not find the path
	return False


def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			# new spot
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid

# drawing gridlines
def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		# draw horizontal line for each of the rows
		# give start and end of line
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			# draw vertical line for each of the columns
			# give start and end of line
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

# drawing everything
def draw(win, grid, rows, width):
	win.fill(WHITE)
	# draw all the colors
	for row in grid:
		for spot in row:
			spot.draw(win)
	# draw gridlines
	draw_grid(win, rows, width)
	# take whatever that was drawn and update it
	pygame.display.update()

# given mouse position - by pos 
def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos
	
	# dividing the x and y position by width of cube
	# gives location
	row = y // gap
	col = x // gap

	return row, col


def main(win, width):
	ROWS = 50
	# call make_grid function
	grid = make_grid(ROWS, width)

	start = None
	end = None

	run = True
	while run:
		# make sure to draw everything
		draw(win, grid, ROWS, width)
		# loop through all the events that happened
		for event in pygame.event.get():
			# 1st thing to check
			# stop running if they quit
			if event.type == pygame.QUIT:
				run = False

			# left clicking - draw
			if pygame.mouse.get_pressed()[0]: # if left is clicked:
				# give x,y pos of mouse
				pos = pygame.mouse.get_pos()
				# get row and col of 2-D list
				row, col = get_clicked_pos(pos, ROWS, width)
				# index/access it
				spot = grid[row][col]
				# 1st click has to be start point
				if not start and spot != end:
					start = spot
					start.make_start()
				# 2nd click has to be end point 
				elif not end and spot != start:
					end = spot
					end.make_end()
				# if not start or end, then make barrier
				elif spot != end and spot != start:
					spot.make_barrier()

			# right clicking - deleting
			elif pygame.mouse.get_pressed()[2]: # elif right is clicked:
				# give x,y pos of mouse
				pos = pygame.mouse.get_pos()
				# get row and col of 2-D list
				row, col = get_clicked_pos(pos, ROWS, width)
				# index/access it
				spot = grid[row][col]
				# right click - clears and resets nodes
				spot.reset()
				if spot == start:
					start = None
				elif spot == end:
					end = None

			# check if spacebar was pressed
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					# calling for each spot
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)
					# lamda = anonymous function
					algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

				# clear with "C"
				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, width)
	# exit pygame window
	pygame.quit()

main(WIN, WIDTH)

