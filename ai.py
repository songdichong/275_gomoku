'''
game class
init:
game.board: 15x15 arrary that records stone information

function:
game.reset: clear the board

game.get_value: 1 if the target position is black stone. 2 if it is white.

game.check_winner: check wether there are 5 stones connected. return winner
'''
class game:
	def __init__(self):
		#board is a 15*15 array: each posision is initially set to be 0
		self.board = [[0 for i in range(15)] for j in range(15)]

	def board (self):
		return self.board

	#clear the board
	def reset(self):
		self.board = [[0 for i in range(15)] for j in range(15)]
		return self.board

	#get the value at a coord
	def get_value(self,row,col):
		if row<0 or row>=15 or col<0 or col>=15:
			return 0
		else:
			return self.board[row][col]

	def check_winner(self):
		board=self.board
		#check 4 directions
		direction = ((1,-1),(1,0),(1,1),(0,1))
		#i=row,j=col
		for i in range(15):
			for j in range(15):
				# no need to consider the position without any stone
				if board[i][j]==0:
					continue

				value = board[i][j]
				#check winner
				for d in direction:
					(x,y) = (i,j)
					count = 0
					for k in range(5):
						if self.get_value(x,y)!= value:
							break
						x+= d[0]
						y+= d[1]
						count+= 1

					if count==5:
						return value
		#no winner yet, return 0
		return 0

	def terminal(self):
		print('  A B C D E F G H I J K L M N O')
		for column in range(15):
			print(chr(ord('A')+column),end=' ')
			for row in range(15):
				current = self.board[row][column]
				if current==0:
					print('.',end=' ')
				elif current==1:
					print('X',end=' ')
				elif current==2:
					print('O',end=' ')
			print ('')
'''
evaluation class
init:
evaluation.position: record the weight of each point. The midmost point weights the most
evaluation.record: 15x15x4 list that records the result of analysis 
evaluation.count: counts the number of live/dead 2,3,4 5 of black and white after the move

function:
evaluation.reset: clear the record

evaluation.analysis_line: analyze a line, find out different situations (i.e., five, four, three, etc)

evluation.anlyze_horizon/vertical/leftdiagonal/rightdiagonal: anlyze how may situations there will be in these directions

evaluation.return score: return score

evaluation.evluate: detailed evluation
'''
class evaluation:
	def __init__(self):
		# self.position is for adding weight to each intersetion
		# add weight of 7 to the center, 6 to the outer square, then
		# 5, 4, 3, 2, 1, at last 0 to the outermost square.
		self.position = []
		for i in range(15):
			row=[]
			for j in range(15):
				row.append( 7 - max(abs(i - 7), abs(j - 7)) )
			self.position.append(row)

		# different types of situations below
		self.d_two = 1			# dead 2		2 stones in a row, 1 move(1 possible position) to make a d3
		self.d_three = 2		# dead 3		3 stones in a row, 1 move(1 possible position) to make a d4
		self.d_four = 3			# dead 4		4 stones in a row, 1 move(1 possible position) to make a 5
		self.l_two = 4			# live 2		2 stones in a row, 1 move(2 possible positions) to make a l3
		self.l_three = 5		# live 3		3 stones in a row, 1 move(2 possible positions) to make a l4
		self.l_four = 6			# live 4		4 stones in a row, 1 move(2 possible positions) to make a 5
		self.five = 7			# live 5		5 stones in a row
		self.analyzed = 8		# has benn analyzed
		self.unanalyzed = 0			# has not been analyzed
		self.result = [ 0 for i in range(30) ]		# save current reslut of analyzation in a line
		self.line = [ 0 for i in range(30) ]		# current data in a line
		self.record = []			# result of analysis of whole board
									# format of each item in list is record[row][col][dir]
		for i in range(15):
			self.record.append([])
			self.record[i] = []
			for j in range(15):
				self.record[i].append([ 0, 0, 0, 0])
		
		self.count = []				# count of each situation: count[black/white][situation]
		for i in range(3):
			data = [ 0 for i in range(10) ]
			self.count.append(data)
		
		self.reset()

	def reset(self):
		count = self.count
		for i in range(15):
			line = self.record[i]
			for j in range(15):
				line[j][0] = self.unanalyzed
				line[j][1] = self.unanalyzed
				line[j][2] = self.unanalyzed
				line[j][3] = self.unanalyzed
		for i in range(10):
			count[0][i] = 0
			count[1][i] = 0
			count[2][i] = 0


	# analyze & evaluate board
	# return score based on analysis result
	def return_score (self, board, turn):
		score = self.evaluate(board, turn)
		count = self.count
		if score < -9000:
			if turn == 1:
				stone = 2
			elif turn == 2:
				stone = 1
			for i in range(10):
				if count[stone][i] > 0:
					score -= i

		elif score > 9000:
			if turn == 1:
				stone = 2
			elif turn == 2:
				stone = 1
			for i in range(10):
				if count[turn][i] > 0:
					score += i
		return score

	# analyze & evaluate board
	# in 4 directinos: horizontally, vertically, left-hand diagonally and right-hand diagonally
	# return score difference between players based on analysis result
	def evaluate (self, board, turn):
		record = self.record
		count = self.count
		unanalyzed = self.unanalyzed
		analyzed = self.analyzed
		self.reset()
		# analysis in 4 directions
		for i in range(15):
			for j in range(15):
				if board[i][j] != 0:
					# has not analyzed horizontally
					if record[i][j][0] == unanalyzed:
						self.analyze_horizontal(board, i, j)
					# has not analyzed vertically
					if record[i][j][1] == unanalyzed:
						self.analyze_vertical(board, i, j)
					# has not analyzed left-hand diagonally
					if record[i][j][2] == unanalyzed:
						self.analyze_left(board, i, j)
					# has not analyzed right-hand diagonally
					if record[i][j][3] == unanalyzed:
						self.analyze_right(board, i, j)

		five = self.five
		l_four = self.l_four
		l_three =  self.l_three
		l_two = self.l_two
		d_four = self.d_four
		d_three = self.d_three
		d_two = self.d_two

		check = {}

		# for either white or black, calculated the number of occurences of different
		# situations (i.e., five, l_four, d_four, l_three, d_three, l_two, d_two)
		for c in (five, l_four, d_four, l_three, d_three, l_two, d_two):
			check[c] = 1
		# for each stone on the board
		for i in range(15):
			for j in range(15):
				stone = board[i][j]
				if stone != 0:
					# for 4 directions
					for k in range(4):
						ch = record[i][j][k]
						if ch in check:
							count[stone][ch] += 1

		# return score if there is a five
		black = 1
		white = 2
		# current turn is white
		if turn == white:
			if count[black][five]:
				return -10000
			elif count[white][five]:
				return 10000
		# current turn is black
		else:
			if count[white][five]:
				return -10000
			elif count[black][five]:
				return 10000

		# if there exist 2 dead 4, it's equivalent to 1 live 4
		if count[white][d_four] >= 2:
			count[white][l_four] += 1
		if count[black][d_four] >= 2:
			count[black][l_four] += 1

		# return score for specific situations
		white_value = 0
		black_value = 0
		win = 0
		# current turn is white
		if turn == white:
			#specific situations that may cause direct win or lose in 2 turn
			# white live 4 (win in 1 turn)
			if count[white][l_four] > 0:
				return 9990
			#white dead 4(need to kill it immediately)
			if count[white][d_four] > 0:
				return 9980
			#black live 4(lose in 1 turn)
			if count[black][l_four] > 0:
				return -9970
			#black dead 4 and live 3 (lose in 2 turn)
			if count[black][d_four] > 0 and count[black][l_three] > 0:
				return -9960
			#white live 3 & no black dead 4 (attack situation)
			if count[white][l_three] >0 and count[black][d_four] == 0:
				return 9950
			#(defend situation)
			if	(count[black][l_three] > 1 and	# black >1 live 3 &
				count[white][d_four] == 0 and	# no white dead 4 &
				count[white][l_three] == 0 and	# no white live 3 &
				count[white][d_three] == 0):	# no white dead 3
					return -9940

			#general cases
			#white >1 live 3
			if count[white][l_three] > 1:
				white_value += 2000
			#white 1 live 3
			elif count[white][l_three]==1:
				white_value += 200
			#black>1 live 3
			if count[black][l_three] > 1:
				black_value += 500
			#black 1 live 3
			elif count[black][l_three]==1:
				black_value += 100

			#white dead 3
			if count[white][d_three]>0:
				white_value += count[white][d_three] * 10
			#black dead 3
			if count[black][d_three]>0:
				black_value += count[black][d_three] * 10
			#white live 2
			if count[white][l_two]>0:
				white_value += count[white][l_two] * 4
			#black live 2
			if count[black][l_two]>0:
				black_value += count[black][l_two] * 4
			#white dead 2
			if count[white][d_two]>0:
				white_value += count[white][d_two]
			#black dead 2
			if count[black][d_two]>0:
				black_value += count[black][d_two]

		# current turn is black
		else:
			#black live 4
			if count[black][l_four] > 0:
				return 9990
			#black dead 4
			if count[black][d_four] > 0:
				return 9980
			#white live 4
			if count[white][l_four] > 0:
				return -9970
			#white dead 4 & live 3
			if count[white][d_four]>0 and count[white][l_three]>0:
				return -9960
			#black live 3 & no white dead 4
			if count[black][l_three] and count[white][d_four] == 0:
				return 9950
			if	(count[white][l_three] > 1 and	# white >1 live 3 &
				count[black][d_four] == 0 and	# no black dead 4 &
				count[black][l_three] == 0 and	# no black live 3 &
				count[black][d_three] == 0):	# no black dead 3
				return -9940
			#black >1 live 3
			if count[black][l_three] > 1:
				black_value += 2000
			#black 1 live 3
			elif count[black][l_three]==1:
				black_value += 200
			#white >1 live 3
			if count[white][l_three] > 1:
				white_value += 500
			#white 1 live 3
			elif count[white][l_three]==1:
				white_value += 100

			#black dead 3
			if count[black][d_three]:
				black_value += count[black][d_three] * 10
			#white dead 3
			if count[white][d_three]:
				white_value += count[white][d_three] * 10
			#black live 2
			if count[black][l_two]:
				black_value += count[black][l_two] * 4
			#white live 2
			if count[white][l_two]:
				white_value += count[white][l_two] * 4
			#black dead 2
			if count[black][d_two]:
				black_value += count[black][d_two]
			#white dead 2
			if count[white][d_two]:
				white_value += count[white][d_two]


		# include weight for each intersection
		white_pos = 0
		black_pos = 0
		# for each intersection with a stone, add weight
		for i in range(15):
			for j in range(15):
				stone = board[i][j]
				if stone != 0:
					if stone == white:
						white_pos += self.position[i][j]
					else:
						black_pos += self.position[i][j]
		# add total weight to total score
		white_value += white_pos
		black_value += black_pos

		# return score differnece between players
		if turn == white:
			return (white_value - black_value)
		else:
			return (black_value - white_value)


	# anaylze horizontally
	def analyze_horizontal (self, board, i, j):
		# add each intersection in a row to line
		for x in range(15):
			self.line[x] = board[i][x]
		self.analysis_line(self.line, self.result, 15, j)
		for x in range(15):
			if self.result[x] != 0:
				self.record[i][x][0] = self.result[x]
		return self.record[i][j][0]


	# analyze vertically
	def analyze_vertical (self, board, i, j):
		for x in range(15):
			self.line[x] = board[x][j]
		self.analysis_line(self.line, self.result, 15, i)
		for x in range(15):
			if self.result[x] != 0:
				self.record[x][j][1] = self.result[x]
		return self.record[i][j][1]


	# analyze left-hand diagonally
	def analyze_left (self, board, i, j):
		if i < j:
			(x, y) = (j - i, 0)
		else:
			(x, y) = (0, i - j)
		k = 0
		while k < 15:
			if x + k > 14 or y + k > 14:
				break
			self.line[k] = board[y + k][x + k]
			k += 1
		self.analysis_line(self.line, self.result, k, j - x)
		for s in range(k):
			if self.result[s] != 0:
				self.record[y + s][x + s][2] = self.result[s]
		return self.record[i][j][2]


	# analyzed right-hand diagonally
	def analyze_right (self, board, i, j):
		if (14 - i)< j:
			x, y, realnum = j - 14 + i, 14, 14 - i
		else:
			x, y, realnum = 0, i + j, j
		k = 0
		while k < 15:
			if x + k > 14 or y - k < 0:
				break
			self.line[k] = board[y - k][x + k]
			k += 1
		self.analysis_line(self.line, self.result, k, j - x)
		for s in range(k):
			if self.result[s] != 0:
				self.record[y - s][x + s][3] = self.result[s]
		return self.record[i][j][3]
	
	#Function that finds dead 2,3,4; live 2,3,4 and 5
	def analysis_line (self, line, record, num, pos):
		#initializations
		unanalyzed = self.unanalyzed
		analyzed = self.analyzed
		l_three = self.l_three
		d_three = self.d_three
		l_four = self.l_four
		d_four = self.d_four
		while len(line) < 30:
			line.append(15)
		while len(record) < 30:
			record.append(unanalyzed)
		for i in range(num, 30):
			line[i] = 15
		for i in range(num):
			record[i] = unanalyzed
		if num < 5:
			for i in range(num):
				record[i] = analyzed
			return 0
		
		stone = line[pos]
		inverse = (0, 2, 1)[stone]
		num -= 1
		xl = pos
		xr = pos
		# left border
		while xl > 0:
			if line[xl - 1] != stone:
				break
			xl -= 1
		# right border
		while xr < num:
			if line[xr + 1] != stone:
				break
			xr += 1
		left_range = xl
		right_range = xr
		# left border check (no opponent's stone)
		while left_range > 0:
			if line[left_range - 1] == inverse:
				break
			left_range -= 1
		# right border check (no opponent's stone)
		while right_range < num:
			if line[right_range + 1] == inverse:
				break
			right_range += 1

		# if the linear range is less than 5, return directly
		if (right_range - left_range) < 4:
			for k in range(left_range, right_range + 1):
				record[k] = analyzed
			return 0

		# set analyzed
		for k in range(xl, xr + 1):
			record[k] = analyzed

		srange = xr - xl

		# if 5 in a row
		if srange >= 4:
			record[pos] = self.five
			return self.five

		# if 4 in a row
		if srange == 3:
			leftfour = False
			# if space on the left
			if xl > 0:
				if line[xl - 1] == 0:
					# live 4
					leftfour = True
			if xr < num:
				if line[xr + 1] == 0:
					if leftfour:
						# live 4
						record[pos] = self.l_four
					else:
						# dead 4
						record[pos] = self.d_four
				else:
					if leftfour:
						# dead 4
						record[pos] = self.d_four
			else:
				if leftfour:
					# dead 4
					record[pos] = self.d_four
			return record[pos]

		# if 3 in a row
		if srange == 2:
			left3 = False
			# if space on the left
			if xl > 0:
				# if space on the left
				if line[xl - 1] == 0:
					if xl > 1 and line[xl - 2] == stone:
						record[xl] = d_four
						record[xl - 2] = analyzed
					else:
						left3 = True
				elif xr == num or line[xr + 1] != 0:
					return 0
			if xr < num:
				# if space on the right
				if line[xr + 1] == 0:
					if xr < num - 1 and line[xr + 2] == stone:
						# 11101 or 22202 is equivalent to dead 4
						record[xr] = d_four
						record[xr + 2] = analyzed
					elif left3:
						record[xr] = l_three
					else:
						record[xr] = d_three
				elif record[xl] == d_four:
					return record[xl]
				elif left3:
					record[pos] = d_three
			else:
				if record[xl] == d_four:
					return record[xl]
				if left3:
					record[pos] = d_three
			return record[pos]

		# if 2 in a row
		if srange == 1:
			left2 = False
			if xl > 2:
				# if space on the left
				if line[xl - 1] == 0:
					if line[xl - 2] == stone:
						if line[xl - 3] == stone:
							record[xl - 3] = analyzed
							record[xl - 2] = analyzed
							record[xl] = d_four
						elif line[xl - 3] == 0:
							record[xl - 2] = analyzed
							record[xl] = d_three
					else:
						left2 = True
			if xr < num:
				# if space on the right
				if line[xr + 1] == 0:
					if xr < num - 2 and line[xr + 2] == stone:
						if line[xr + 3] == stone:
							record[xr + 3] = analyzed
							record[xr + 2] = analyzed
							record[xr] = d_four
						elif line[xr + 3] == 0:
							record[xr + 2] = analyzed
							record[xr] = left2 and l_three or d_three
					else:
						if record[xl] == d_four:
							return record[xl]
						if record[xl] == d_three:
							record[xl] = l_three
							return record[xl]
						if left2:
							record[pos] = self.l_two
						else:
							record[pos] = self.d_two
				else:
					if record[xl] == d_four:
						return record[xl]
					if left2:
						record[pos] = self.d_two

			return record[pos]
		return 0

'''
searcher class
init:
searcher.board: gameboard
searcher.gameover: already win/lose situation
searcher.depth: level of trees that considered

function:
searcher.generate_moves:generate possible moves and return the socre

searcher.alpbeta_search:alpha-beta search, call generate_move function and return
						alpha score(white,ai) and beta score(black,player), and 
						eliminate the useless branches
searcher.search:final decision
'''
class searcher:
	# initialization
	def __init__ (self):
		self.evaluator = evaluation()
		self.board = game().board
		self.gameover = 0
		# set the max depth to 3 so that the running time for each move is not too long
		# depth: 1 - <1 sec, 2 - a few sec, 3 - up to 4 min
		self.maxdepth = 3

	# generate possible moves for the current board
	# store the score and position of each move in a list in format of (score, i, j)
	def generate_moves (self, turn):
		moves = []
		board = self.board
		POSES = self.evaluator.position
		for i in range(15):
			for j in range(15):
				if board[i][j] == 0:
					score = POSES[i][j]
					moves.append((score, i, j))
		# moves are sorted with decreasing scores
		moves.sort()
		moves.reverse()
		return moves

	# recursive search, returns the best score
	# minimax algorithm with alpha-beta pruning
	# 0x7fffffff == (2^31)-1, indicating a large value
	def alpbeta_search (self, turn, depth, alpha = -0x7fffffff, beta = 0x7fffffff):

		# base case: depth is 0
		# evaluate the board and return
		if depth <= 0:
			score = self.evaluator.return_score(self.board, turn)
			return score

		# if game over, return immediately
		score = self.evaluator.return_score(self.board, turn)
		if abs(score) >= 9999 and depth < self.maxdepth:
			return score

		# generate new moves
		moves = self.generate_moves(turn)
		bestmove = None

		# for all current moves
		# len(moves) == num of empty intersections on current board
		# worst case O(m^n) or O( m!/(m-n)! ), m = num of empty spots,
		# 			n = depth(num of further steps this program predicts)
		for score, row, col in moves:

			# label current move to board
			self.board[row][col] = turn

			# calculate next turn
			if turn == 1:
				nturn = 2
			elif turn == 2:
				nturn = 1


			# DFS, return score and position of move
			score = - self.alpbeta_search(nturn, depth - 1, -beta, -alpha)

			# clear current move on board
			self.board[row][col] = 0

			# calculate the move with best score
			# alpha beta pruning: removes nodes that are evaluated by the minimax algorithm
			# 				in the search tree, eliminates branches that cannot posibbly
			#				influence the final decision.
			if score > alpha:
				alpha = score
				bestmove = (row, col)
				if alpha >= beta:
					break

		# if depth is max depth, record the best move
		if depth == self.maxdepth and bestmove:
			self.bestmove = bestmove

		# return current best score and its correponding move
		return alpha


	# specific search
	# args: turn: 1(black)/2(white), depth
	def search (self, turn, depth = 3):
		self.maxdepth = depth
		self.bestmove = None
		score = self.alpbeta_search(turn, depth)
		if abs(score) > 8000:
			self.maxdepth = depth
			score = self.alpbeta_search(turn, 1)
		row, col = self.bestmove
		return score, row, col
