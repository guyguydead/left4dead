#==================================================
# record_data.py - data structures to keep track of records
#
# NOTE: these data structures ended up not being used; Using dictionaries instead to save time
#==================================================

#--------------------------------------------------
# Map Structure
#--------------------------------------------------
class Map:
	"""Structure to hold map information.
	Maps contain the following data:
	Name:      (example: Mall Atrium)
	Campaign:  (example: Dead Center)
	Game:      (example: Left 4 Dead 2)"""

	# Initialization Operation-------------------------
	def __init__(self, name, campaign, game):
		self.name = name
		self.campaign = campaign
		self.game = game

	def __eq__(self, other):
		name1 = self.name.lower()
		name2 = other.name.lower()
		campaign1 = filter(str.isalnum, self.campaign.lower())
		campaign2 = filter(str.isalnum, other.campaign.lower())
		game1 = self.game.lower()
		game2 = other.game.lower()
		return name1 == name2 and campaign1 == campaign2 and game1 == game2

#--------------------------------------------------
# Player Structure
#--------------------------------------------------
class Player:
	"""Structure to hold player information.
	Players contain the following data:
	Name:      (example: guyguy)
	Country:   (example: Canada)
	Aliases:   (example: ['guyguydead', 'xiaoxiao']"""

	# Initialization Operation-------------------------
	def __init__(self, name, country):
		self.name = name
		self.country = country
		self.aliases = []

#--------------------------------------------------
# SurvivalRecord Structure
#--------------------------------------------------
class SurvivalRecord1:
	"""Structure to hold survival record information (L4D1).
	Survival records contain the following information:
	Map, Time,
	PlayerList,
	Common, Hunters, Smokers, Boomers, Tanks"""

	# Initialization Operation-------------------------
	def __init__(self, map, time, players, c, h, s, b, t):
		self.map = map
		self.time = time
		self.players = players
		self.common = c
		self.hunters = h
		self.smokers = s
		self.boomers = b
		self.tanks = t
