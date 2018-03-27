from tkinter import *
import math
import ai
'''
Board class
init:
self.frame: call tkinter frame
self.canvas:structured graphics facilities. Almost all the function used in tkinter is from this 

'''
class Board:
	def __init__(self,master,height=0,width=0):
		self.frame = Frame(master)
		self.frame.pack()
		self.printButton = Button(self.frame,text='game message',command=self.printMessage)
		self.printButton.pack(side=LEFT)
		self.quitButton = Button(self.frame,text='quit',command=self.frame.quit)
		self.quitButton.pack(side=RIGHT)
		self.orderButton = Button(self.frame,text='let computer go first',command=self.setturn)
		self.orderButton.pack(side=LEFT)
		self.canvas = Canvas(master,height=500,width=500)#range of our gameboard
		
		self.draw_board()
		self.canvas.bind('<Button-1>',self.gameloop)
		self.canvas.pack()# packs widgets in rows or columns
		self.turn=1
		self.g = ai.game()
		self.s = ai.searcher()
		self.s.board = self.g.board
		self.depth = 2

	def printMessage(self):
		print("The game of gomoku. Written by Dichong Song and Jeanna Somoza")
		print("Winning Condition: place 5 stones continiously in any direction(horizontally,vertically or diagonally)")

	def setturn(self):
		for i in range(15):
			for j in range(15):
				if self.s.board[i][j] != 0:
					 self.orderButton.config(state="disabled")
					 return 0
		self.turn=2
		self.orderButton.config(state="disabled")
		

	def draw_board(self):
		for i in range(15):
			start_x = (i+1)*30
			start_y = 30
			end_x = (i+1)*30
			end_y = 15*30
			self.canvas.create_line(start_x,start_y,end_x,end_y)
		for i in range(15):
			start_x = 30
			start_y = (i+1)*30
			end_x = 15*30
			end_y = (i+1)*30
			self.canvas.create_line(start_x,start_y,end_x,end_y)

	def draw_stone(self,row,column):
		start_x = (row+1)*30-10
		start_y = (column+1)*30-10
		end_x = (row+1)*30+10
		end_y = (column+1)*30+10
		if self.turn ==1:
			self.canvas.create_oval(start_x,start_y,end_x,end_y,fill='black')
		elif self.turn ==2:
			self.canvas.create_oval(start_x,start_y,end_x,end_y,fill='white')

	def gameloop(self,event):
		#user's turn
		if self.turn==1:
			while True:
				print ('Your turn now...\n')
				invalid_pos = True
				for i in range(15):
					for j in range(15):
						pixel_x = (i + 1) * 30
						pixel_y = (j + 1) * 30
						square_x = (event.x - pixel_x)** 2
						square_y = (event.y - pixel_y)** 2
						distance =  math.sqrt(square_x + square_y)
						#print(distance)
						if (distance < 15)and(self.g.board[i][j] == 0):
							invalid_pos = False
							(row, col) = (i, j)
							self.draw_stone(i,j)
							self.canvas.unbind('<Button-1>')
							break
						else:
							continue	# executed if the inner for loop ended normally(no break)
						break	
				if invalid_pos:
					print ('Invalid position. Please choose another one\n')
					break
				else:
					break#exit the entire while loop
			
			# Place a black stone after determining the position
			self.g.board[row][col] = 1
			#print(self.g.board,'\n')
			# If the user wins the game, end the game and unbind.
			if self.g.check_winner() == 1:
				print ('BLACK WINS !!')
				self.canvas.create_text(240, 480, text = 'BLACK WINS !!')
				self.canvas.unbind('<Button-1>')
				return 0

		# Change the turn to the program now
		self.turn = 2
		print ('Program is thinking now...')
		# Determine the position the program will place a white stone on.
		# Place a white stone after determining the position.
		score, row, col = self.s.search(self.turn, self.depth)
		coord = '%s%s'%(chr(ord('A') + row), chr(ord('A') + col))
		print ('Program has moved to %s \n' % coord)
		self.g.board[row][col] = 2
		self.draw_stone(row,col)
		self.g.terminal()
		self.turn =1
		# bind after the program makes its move so that the user can continue to play
		self.canvas.bind('<Button-1>', self.gameloop)

		# If the program wins the game, end the game and unbind.
		if self.g.check_winner() == 2:
			print ('WHITE WINS.')
			self.canvas.create_text(240, 480, text = 'WHITE WINS')
			self.canvas.unbind('<Button-1>')
			return 0


root= Tk(className=" GOMOKU")
board=Board(root)
root.mainloop()
