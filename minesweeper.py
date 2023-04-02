import random

class Globals: #To avoid dealing with global variables
	rows = None
	columns = None
	mines = None
	board = []
	marker = [None, None]

class Tile:
	def __init__(self):
		self.revealed = False
		self.mine = False
		self.flag = False
		self.adjacentTiles = []
	
	#Using board and position (as the object does not normally know its own position on the board), adds all "adjacent" tiles to a list
	def initalizeAdjacentTiles(self, board, r, c):
		self.adjacentTiles = []
		for i in range(r-1, r+2):
			for j in range(c-1, c+2):
				if (0 <= i < Globals.rows) and (0 <= j < Globals.columns) and ((i, j) != (r, c)): #Checking that position is in range, and not self
					self.adjacentTiles.append(Globals.board[i][j])
	
	#Determines the number of adjacent tiles that are mines
	def getAdjacentMinesCount(self):
		return len(list(filter(lambda t : t.mine, self.adjacentTiles)))
	
	#Reveals tile, as well as all adjacent tiles if none of them are mines
	#Returns number of tiles revealed
	def revealTile(self):
		self.revealed = True
		self.flag = False
		if self.getAdjacentMinesCount() == 0:
			r = 1
			for t in self.adjacentTiles:
				if not t.revealed:
					r += t.revealTile()
			return r
		else:
			return 1

#Returns a string representation of the board, with the following format:
#	X for marker position (if markerPos != None)
#	F for flagged tile
#	+ for unrevealed and unflagged tile
#	B for revealed bomb tile (used for game over screen)
#	1-9 for revealed tile with adjacent mines
#	. for revealed tile with no adjacent mines
def boardString(board, markerPos=None):
	outStr = ""
	
	for i in range(len(board)):
		for j in range(len(board[i])):
			tile = board[i][j]
			if [i, j] == markerPos:
				outStr += "X"
			elif tile.revealed and tile.mine:
				outStr += "B"
			elif tile.revealed and tile.getAdjacentMinesCount() == 0:
				outStr += "."
			elif tile.revealed:
				outStr += str(tile.getAdjacentMinesCount())
			elif tile.flag:
				outStr += "F"
			else:
				outStr += "+"
		outStr += "\n"
	
	return outStr

#Generates a function that prompts the user with a custom string, and outputs either yesFunc or noFunc, depending on user input
#The output function generated takes no arguments and outputs a callable object, allowing it to be used in the menu-state system 
def generateConfirmationMenu(prompt, yesFunc, noFunc):
	def confirm():
		if input(prompt+" (Enter y to confirm, other to cancel): ") in ['y', 'Y']:
			return yesFunc
		else:
			return noFunc
	return confirm

#Prompts the user to enter the number of rows. If the user enters a non-integer or a non-positive number, they will be prompted to re-enter, otherwise the program progresses to selectColumnMenu
def selectRowMenu():
	try:
		Globals.rows = int(input("Enter the number of rows: "))
	except ValueError:
		print("Input must be number, please re-enter")
		return selectRowMenu
	if Globals.rows < 1:
		print("Input must greater than zero, please re-enter")
		return selectRowMenu
	return selectColumnMenu

#Prompts the user to enter the number of columns. If the user enters a non-integer or a non-positive number, they will be prompted to re-enter, otherwise the program progresses to either confirm and progress to selectMines or re-enter the board size
def selectColumnMenu():
	try:
		Globals.columns = int(input("Enter the number of columns: "))
	except ValueError:
		print("Input must be number, please re-enter")
		return selectColumnMenu
	if Globals.columns < 1:
		print("Input must greater than zero, please re-enter")
		return selectColumnMenu
	return generateConfirmationMenu("Board Preview: \n\n"+(('+'*Globals.columns)+'\n')*Globals.rows+'\nConfirm board size '+str(Globals.columns)+'x'+str(Globals.rows)+'?', selectMines, selectRowMenu)

#Prompts the user to enter the number of columns. If the user enters a non-integer or a number out of range, they will be prompted to re-enter, otherwise the program progresses to either confirm and progress to initalizeBoard or re-enter the number of mines
def selectMines():
	try:
		Globals.mines = int(input("Enter the number of mines: "))
	except ValueError:
		print("Input must be number, please re-enter")
		return selectMines
	if not 0 <= Globals.mines < Globals.rows*Globals.columns:
		print("Input must be between 0 and "+str(Globals.rows*Globals.columns-1)+" (inclusive), please re-enter")
		return selectMines
	return generateConfirmationMenu("Is this the correct number of mines ("+str(Globals.mines)+")?", initalizeBoard, selectMines) 

#Creates a row*column list of Tile objects, runs the function initalizeAdjacentTiles on each object, and converts a fixed number of random tiles into mines
def initalizeBoard():
	Globals.board = list(map(lambda r : list(map(lambda t : Tile(), range(Globals.columns))), range(Globals.rows)))
	for i in range(len(Globals.board)):
		for j in range(len(Globals.board[i])):
			Globals.board[i][j].initalizeAdjacentTiles(Globals.board, i, j)
	while Globals.mines > 0:
		Globals.marker[0] = random.randint(1, Globals.rows-1)
		Globals.marker[1] = random.randint(1, Globals.columns-1)
		if not Globals.board[Globals.marker[0]][Globals.marker[1]].mine:
			Globals.board[Globals.marker[0]][Globals.marker[1]].mine = True
			Globals.mines -= 1
	return gameActionMenu

#Generates a pair of functions that prompt the user to enter a series of coordinates, before progressing to endFunction
def fillMarker(endFunction):
	def getYPos():
		try:
			Globals.marker[0] = int(input("Enter the row: "))
		except ValueError:
			print("Input must be number, please re-enter")
			return getYPos
		if not 0 <= Globals.marker[0] < Globals.rows:
			print("Input must be between 0 and "+str(Globals.rows)+" (inclusive), please re-enter")
			return getYPos
		return endFunction
	def getXPos():
		try:
			Globals.marker[1] = int(input("Enter the column: "))
		except ValueError:
			print("Input must be number, please re-enter")
			return getXPos
		if not 0 <= Globals.marker[1] < Globals.columns:
			print("Input must be between 0 and "+str(Globals.columns)+" (inclusive), please re-enter")
			return getXPos
		return getYPos
	return getXPos

#The main action menu, allowing the user to either guess a tile, toggle a flag, or exit the game
def gameActionMenu():
	print("GAME BOARD:\n"+boardString(Globals.board))
	print("Options")
	print("1. Guess Tile")
	print("2. Flag/Unflag Tile")
	print("3. Exit Game")
	inVal = input("Select Option: ")
	if inVal == '1':
		return fillMarker(guessTile)
	elif inVal == '2': 
		return fillMarker(placeFlag)
	elif inVal == '3':
		return generateConfirmationMenu("Exit Game?", None, gameActionMenu)
	else:
		print("Invalid input, please re-enter: ")
		return gameActionMenu

#Asks user for confirmation before either triggering a game over (if the selected tile is a mine), or revealing the tile and checking for a win condition
def guessTile():
	prompt = "\nGAME BOARD:\n"+boardString(Globals.board, markerPos=Globals.marker)+'\n'
	prompt += "Guess tile ("+str(Globals.marker[1])+", "+str(Globals.marker[0])+")?"
	if Globals.board[Globals.marker[0]][Globals.marker[1]].flag:
		prompt += " (WARNING: TILE HAS BEEN FLAGGED)"
	if generateConfirmationMenu(prompt, True, False)():
		if Globals.board[Globals.marker[0]][Globals.marker[1]].mine:
			return gameOver
		else:
			print("Successful guess, "+str(Globals.board[Globals.marker[0]][Globals.marker[1]].revealTile())+" tiles revealed\n")
			return checkForWin
	else:
		return gameActionMenu

#Prompts the user for confirmation before toggling the flag variable on the selected tile
def placeFlag():
	prompt = "\nGAME BOARD:\n"+boardString(Globals.board, markerPos=Globals.marker)+'\n'
	if Globals.board[Globals.marker[0]][Globals.marker[1]].flag:
		prompt += "Unflag "
	else:
		prompt += "Flag "
	prompt += "tile ("+str(Globals.marker[1])+", "+str(Globals.marker[0])+")?"
	if generateConfirmationMenu(prompt, True, False)():
		Globals.board[Globals.marker[0]][Globals.marker[1]].flag = not Globals.board[Globals.marker[0]][Globals.marker[1]].flag
	return gameActionMenu

#Reveals all mine tiles, before displaying the board and prompting the player to either play again or exit
def gameOver():
	for i in range(len(Globals.board)):
		for j in range(len(Globals.board[i])):
			if Globals.board[i][j].mine:
				Globals.board[i][j].revealed = True
			Globals.board[i][j].flag = False
	print("GAME BOARD:\n"+boardString(Globals.board))
	return generateConfirmationMenu("GAME OVER\nPlay another round?", selectRowMenu, None)

#Checks for a victory (all tiles are either mined or revealed). If the player has won, the board is displayed and the player is prompted to either play again or exit. If the player has not won, then the program returns to gameActionMenu
def checkForWin():
	winCond = True
	for i in range(len(Globals.board)):
		for j in range(len(Globals.board[i])):
			if not (Globals.board[i][j].mine or Globals.board[i][j].revealed):
				winCond = False
				break
		if not winCond:
			break
	
	if winCond:
		print("GAME BOARD:\n"+boardString(Globals.board))
		return generateConfirmationMenu("YOU WIN\nPlay another round?", selectRowMenu, None)
	else:
		return gameActionMenu

state = selectRowMenu #Starting Function
while state != None:
	state = state()
