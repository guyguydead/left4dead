#==================================================
# survival_records.py - Script to keep track of left 4 dead survival records. The information is tracked inside of dictionaries, which can be imported and exported to text files.
#==================================================
import datetime
import sys
import re

#--------------------------------------------------
# import_list(filename, list)
#--------------------------------------------------
def import_list(filename, list):
	f = open(filename, 'r')
	lists = [ dict(item.split('=') for item in line.strip().split(';')) for line in f.readlines()]
	list += lists
	f.close()

#--------------------------------------------------
# export_players_list(file, players)
#--------------------------------------------------
def export_players_list(file, players):
	file.write('\n'.join(['name=%s;country=%s;ID=%d;aliases=%s' % (player['name'], player['country'], player['ID'], ','.join(player['aliases'])) for player in players]))

#--------------------------------------------------
# export_maps_list(file, maps)
#--------------------------------------------------
def export_maps_list(file, maps):
	file.write('\n'.join(['name=%s;campaign=%s;game=%d;ID=%d' % (map['name'], map['campaign'], map['game'], map['ID']) for map in maps]))

#--------------------------------------------------
# export_records_list(file, records)
#--------------------------------------------------
def export_records_list(file, records):
	file.write('\n'.join(['ID=%d;date=%s;time=%02d:%02d:%02d.%02d;map=%d;players=%s;common=%d;hunters=%d;smokers=%d;boomers=%d;tanks=%d' \
		% (record['ID'], \
		record['date'], \
		record['time'].seconds / 3600, record['time'].seconds % 3600 / 60, record['time'].seconds % 3600 % 60, record['time'].microseconds / 10000, \
		record['map']['ID'], \
		','.join(['%d' % player['ID'] for player in record['players']]), \
		record['common'], \
		record['hunters'], \
		record['smokers'], \
		record['boomers'], \
		record['tanks']) for record in records]))

#--------------------------------------------------
# print_players(players)
#--------------------------------------------------
def print_players(players):
	for player in players:
		print "%8s: %s" % ('name', player['name'])
		print "%8s: %s" % ('country', player['country'])
		print "%8s: %s" % ('aliases', player['aliases'])
		print

#--------------------------------------------------
# print_records(records)
#--------------------------------------------------
def print_records(records):
	for record in records:
		print "%s time: %s" % (record['date'], record['time'])
		print "%10s: %s" % ("map", record['map']['name'])
		print "%10s: %s" % ("players", ", ".join([p['name'] for p in record['players']]))

#--------------------------------------------------
# import_player_list(filename, players)
#--------------------------------------------------
def import_player_list(filename, players):
	import_list(filename, players)
	for player in players:
		player['ID'] = int(player['ID'])
		player['aliases'] = filter(lambda a: a != '', player['aliases'].split(','))

#--------------------------------------------------
# import_map_list(filename, maps)
#--------------------------------------------------
def import_map_list(filename, maps):
	import_list(filename, maps)
	for map in maps:
		map['game'] = int(map['game'])
		map['ID'] = int(map['ID'])

#--------------------------------------------------
# create_timedelta(time_str)
#--------------------------------------------------
def create_timedelta(time_str):
	times = time_str.split(':')
	ln = []
	ln += (times[:-1])
	ln += (times[-1].split('.'))

	times = map(int, ln)
	if len(times) == 3:
		return datetime.timedelta(minutes=times[0], seconds=times[1], milliseconds=10*times[2])
	elif len(time) == 4:
		return datetime.timedelta(hours=times[0], minutes=times[1], seconds=times[2], milliseconds=10*times[3])

#--------------------------------------------------
# find_id(maps, ID)
#--------------------------------------------------
def find_id(maps, ID):
	matches = filter(lambda x: x['ID'] == ID, maps)
	assert(len(matches) < 2)

	if len(matches) == 1:
		return matches[0]
	else: return None

#--------------------------------------------------
# import_record_list(filename, records, players, maps)
#--------------------------------------------------
def import_record_list(filename, records, players, maps):
	import_list(filename, records)
	for record in records:
		record['game'] = int(record['game'])
		record['date'] = datetime.date(*(map(int, record['date'].split('-'))))
		record['time'] = create_timedelta(record['time'])
		record['common'] = int(record['common'])
		record['hunters'] = int(record['hunters'])
		record['smokers'] = int(record['smokers'])
		record['boomers'] = int(record['boomers'])
		record['tanks'] = int(record['tanks'])
		record['ID'] = int(record['ID'])

		record['map'] = find_id(maps, int(record['map']))
		record['players'] = [find_id(players, p) for p in map(int, record['players'].split(','))]

#--------------------------------------------------
# import_player_list_csv(file, players)
#--------------------------------------------------
def import_player_list_csv(file, players):
	label = file.readline().strip().split(',')
	for line in map(strip, file.readlines()):
		name, country = line[0:1]
		aliases = filter(lambda x: x != '', line[2:])
		msg = create_player(players, name, country, aliases)
		if msg != None: print msg

#--------------------------------------------------
# import_record_list_csv(file, records, players, maps)
# TODO: make sure there are no duplicates
#--------------------------------------------------
def import_record_list_csv(file, records, players, maps):
	# first line in the csv file is a label
	label = (file.readline().strip().split(','))

	for line in file.readlines():
		line_arr = line.strip().split(',')
		str_dict = {label[k] : v for k,v in enumerate(line.strip().split(','))}
		#game_str, date_str, time_str, map_name, p1_str, p2_str, p3_str, p4_str, common_str, hunters_str, boomers_str, smokers_str, tanks_str = line.strip().split(',')
		game = int(str_dict['game'])
		map_name = str_dict['map']
		p1_str, p2_str, p3_str, p4_str = str_dict['player1'], str_dict['player2'], str_dict['player3'], str_dict['player4']
		time_str = str_dict['time']
		date_str = str_dict['date']

		# find the matching map
		mp = [m for m in maps if m['name'] == map_name and m['game'] == game]
		if mp == []: return 'Map %s not found' % map_name
		else: mp = mp[0]

		# get player names
		playerlist = []
		for name in filter(lambda p: p != '', [p1_str, p2_str, p3_str, p4_str]):
			player = [p for p in players if equal_name(p['name'], name) or is_alias(name, p['aliases'])]
			if player == []:
				return 'Player %s not found [%s]' % (name, ', '.join([p['name'] for p in players]))
			else:
				playerlist.append(player[0])

		# get time, date, counts
		times = time_str.split(':')
		time = datetime.timedelta(hours = int(times[0]), minutes = int(times[1]), seconds = int(times[2].split('.')[0]), milliseconds = 10 * int(times[2].split('.')[1]))

		date = datetime.date(*map(int, date_str.split('-')))

		# make sure there are no exact duplicates of time and date
		if (date, time) in [(r['date'], r['time']) for r in records]:
			# error, duplicate
			continue

		common  = int(str_dict['common'])
		hunters = int(str_dict['hunters'])
		smokers = int(str_dict['smokers'])
		boomers = int(str_dict['boomers'])
		tanks   = int(str_dict['tanks'])
		new_id = max([p['ID'] for p in records]) + 1


		if game == 1:
			records.append(\
			{\
				'ID':new_id, \
				'date':date, \
				'time':time, \
				'map':mp, \
				'players':playerlist, \
				'common':common, \
				'hunters':hunters, \
				'smokers':smokers, \
				'boomers':boomers, \
				'tanks':tanks \
			})

		elif game == 2:
			spitters = int(str_dict['spitters'])
			chargers = int(str_dict['chargers'])
			jockeys = int(str_dict['jockeys'])

			records.append(\
			{\
				'ID':new_id, \
				'date':date, \
				'time':time, \
				'map':mp, \
				'players':playerlist, \
				'common':common, \
				'hunters':hunters, \
				'smokers':smokers, \
				'boomers':boomers, \
				'jockeys':jockeys, \
				'chargers':chargers, \
				'spitters':spitters, \
				'tanks':tanks \
			})

def equal_name(name1, name2):
	return re.sub(r'\s', '', name1).lower() == re.sub(r'\s', '', name2).lower()
def is_alias(name1, aliases_list):
	return filter(lambda n: equal_name(n, name1), aliases_list) != []

#--------------------------------------------------
# create_player(players, name, country, aliases)
#--------------------------------------------------
def create_player(players, name, country, aliases):
	# check if name matches any other existing players or aliases
	matches = filter(lambda p: equal_name(p['name'], name) or is_alias(name, p['aliases']), players)
	if len(matches > 0): return 'Name %s already matches a player' % name

	# check if any of the aliases matches any existing players or aliases
	for alias in aliases:
		matches = filter(lambda p: equal_name(p['name'], alias) or is_alias(alias, p['aliases']), players)
		if len(matches > 0): return 'Alias %s already matches a player' % alias

	# create a new ID by adding 1 to the maximum ID
	new_id = max([player['ID'] for player in players]) + 1
	players.append({'name':name, 'country':country, 'aliases':aliases})
	return None

#--------------------------------------------------
# create_map(maps, name, campaign, game)
#--------------------------------------------------
def create_map(maps, name, campaign, game):
	# check if name matches any other existing maps
	if name in [m['name'] for m in maps]: return 'Name %s already matches an existing map' % name

	# create a new ID by adding 1 to the maximum ID
	new_id = max([m['ID'] for m in maps]) + 1
	maps.append({'name':name, 'campaign':campaign, 'game':game})
	return None

#--------------------------------------------------
# create_record(players, maps, records, date, time, mapID, plyrsID, common, hunters, smokers, boomers, tanks)
#--------------------------------------------------
def create_record(players, maps, records, date, time, mapID, plyrsID, common, hunters, smokers, boomers, tanks):
	"""Creates a new record, checking for any inconsistencies. This function will return None if successful and return an error message if record creation failed.
	
	Keyword arguments:
	players    -- The master list of players
	maps       -- The master list of maps
	records    -- The master list of existing records
	date       -- the date in datetime format
	time       -- the time in timedelta format
	mapID      -- the map ID
	plyrsID    -- list of IDs of the players involved
	common     -- common count
	hunters    -- hunter count
	smokers    -- smoker count
	boomers    -- boomer count
	tanks      -- tank count"""
	# first check to see that there aren't already existing matches with the exact same date and time 
	if (time, date) in zip([r['time'] for r in records], [r['date'] for r in records]):
		return 'There is already a matching record with date and time %s, %s' % (date, time)

	# Next find the specified map ID
	map = find_id(maps, mapID)
	if map == None: return 'Invalid map %d' % mapID

	# find all players
	plyrs = [find_id(players, id) for id in plysID]
	if None in plyrs: return 'One of the player IDs is invalid %s' % plyrsID

	# create a new ID by adding 1 to the maximum ID
	new_id = max([m['ID'] for m in records]) + 1

	records.append(\
	{\
		'ID':new_id, \
		'date':date, \
		'time':time, \
		'map':map, \
		'players':plyrs, \
		'common':common, \
		'hunters':hunters, \
		'smokers':smokers, \
		'boomers':boomers, \
		'tanks':tanks \
	})

	return None

#--------------------------------------------------
# input_new_record(records, maps, players, in_fcn, out_stream=None)
#--------------------------------------------------
def input_new_record(records, maps, players, in_fcn, out_stream=None):
	"""Gets input for a new record using the in_fcn (e.g. raw_input). Prompts for the input using the out_stream. Returns an error message for invalid input or None if sucessful."""

	# get map name
	if out_stream != None:
		out_stream.write('Map: ')
	map_name = in_fcn()

	# find the matching mp
	mp = [m for m in maps if m['name'] == map_name]
	if mp == []: return 'Map %s not found' % map_name
	else: mp = mp[0]

	# get player names
	if out_stream != None:
		out_stream.write('Players, separated by semicolon: ')
	players_names = in_fcn()
	playerlist = []
	for name in players_names.split(';'):
		player = [p for p in players if p['name'] == name]
		if player == []: return 'Player %s not found [%s]' % (name, ', '.join([p['name'] for p in players]))
		else: playerlist.append(player[0])

	# get time, date, counts
	if out_stream != None:
		out_stream.write('Time e.g. 00:17:23.21: ')
	times = in_fcn().split(':')
	time = datetime.timedelta(hours = int(times[0]), minutes = int(times[1]), seconds = int(times[2].split('.')[0]), milliseconds = 10 * int(times[2].split('.')[1]))

	if out_stream != None:
		out_stream.write('Date e.g. 2001-01-30: ')
	date = datetime.date(*map(int, in_fcn().split('-')))

	if out_stream != None:
		out_stream.write('common: ')
	common = int(in_fcn())
	if out_stream != None:
		out_stream.write('hunters: ')
	hunters = int(in_fcn())
	if out_stream != None:
		out_stream.write('smokers: ')
	smokers = int(in_fcn())
	if out_stream != None:
		out_stream.write('boomers: ')
	boomers = int(in_fcn())
	if out_stream != None:
		out_stream.write('tanks: ')
	tanks = int(in_fcn())

	# create a new ID by adding 1 to the maximum ID
	new_id = max([p['ID'] for p in records]) + 1

	records.append(\
	{\
		'ID':new_id, \
		'date':date, \
		'time':time, \
		'map':mp, \
		'players':playerlist, \
		'common':common, \
		'hunters':hunters, \
		'smokers':smokers, \
		'boomers':boomers, \
		'tanks':tanks \
	})

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.spreadsheet
import atom
import getopt
import sys
import string
#--------------------------------------------------
# _PrintFeed(feed)
#--------------------------------------------------
def _PrintFeed(feed):
    for i, entry in enumerate(feed.entry):
      if isinstance(feed, gdata.spreadsheet.SpreadsheetsCellsFeed):
        print '%s %s\n' % (entry.title.text, entry.content.text)
      elif isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
        print '%s %s %s' % (i, entry.title.text, entry.content.text)
        # Print this row's value for each column (the custom dictionary is
        # built using the gsx: elements in the entry.)
        print 'Contents:'
        for key in entry.custom:  
          print '  %s: %s' % (key, entry.custom[key].text) 
        print '\n',
      else:
        print '%s %s\n' % (i, entry.title.text)

#--------------------------------------------------
# update_cell(gd_client, curr_key, curr_wksht_id, row, col, inputValue)
#--------------------------------------------------
def update_cell(gd_client, curr_key, curr_wksht_id, row, col, inputValue):
    entry = gd_client.UpdateCell(row=row, col=col, inputValue=inputValue, 
        key=curr_key, wksht_id=curr_wksht_id)
    if isinstance(entry, gdata.spreadsheet.SpreadsheetsCell):
      return 'Updated!'

#--------------------------------------------------
# export_maps_google_spreadsheet(user, pw, maps)
#--------------------------------------------------
def export_maps_google_spreadsheet(user, pw, maps, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
	if gd_client == None:
		gd_client = gdata.spreadsheet.service.SpreadsheetsService()
		gd_client.email = user
		gd_client.password = pw
		gd_client.ProgrammaticLogin()
	list_feed = None

	# Get the list of spreadsheets
	if curr_key == None:
		curr_key = get_key(gd_client)

	# Get the list of worksheets
	if curr_wksht_id == None:
		curr_wksht_id = get_wksht(gd_client, curr_key)

	message_list = []
	update = lambda r,c,v: update_cell(gd_client, curr_key, curr_wksht_id, r, c, v)

	for game in [1, 2]:
		message_list.append('Left 4 Dead %d Maps' % game)
		message_list += ['%s;%s' % (m['campaign'], m['name']) for m in filter(lambda m: m['game'] == game, maps)]
		if game == 1: message_list.append('')

	export_batch_text_google_spreadsheet(user, pw, message_list, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = curr_wksht_id, verbose=verbose)

#--------------------------------------------------
# export_players_google_spreadsheet(user, pw, players)
#--------------------------------------------------
def export_players_google_spreadsheet(user, pw, players, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
	if gd_client == None:
		gd_client = gdata.spreadsheet.service.SpreadsheetsService()
		gd_client.email = user
		gd_client.password = pw
		gd_client.ProgrammaticLogin()
	list_feed = None

	# Get the list of spreadsheets
	if curr_key == None:
		curr_key = get_key(gd_client)

	# Get the list of worksheets
	if curr_wksht_id == None:
		curr_wksht_id = get_wksht(gd_client, curr_key)

	message_list = []
	message_list.append('name;country;aliases')
	message_list += ['%s;%s;%s' % (m['name'], m['country'], ', '.join(m['aliases'])) for m in players]

	export_batch_text_google_spreadsheet(user, pw, message_list, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = curr_wksht_id, verbose = verbose)

#--------------------------------------------------
# export_records_google_spreadsheet(records, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None)
#--------------------------------------------------
def export_records_google_spreadsheet(records, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
	if gd_client == None:
		gd_client = gdata.spreadsheet.service.SpreadsheetsService()
		gd_client.email = user
		gd_client.password = pw
		gd_client.ProgrammaticLogin()
	list_feed = None

	# Get the list of spreadsheets
	if curr_key == None:
		curr_key = get_key(gd_client)

	# Get the list of worksheets
	if curr_wksht_id == None:
		curr_wksht_id = get_wksht(gd_client, curr_key)

	message_list = []
	message_list.append('Left 4 Dead 1')
	message_list.append('date;time;map;players;common;hunters;smokers;boomers;tanks')

	message_list += [ \
		'%s;%s;%s;%s;%d;%d;%d;%d;%d' % \
		(r['date'], format_time(r['time']), r['map']['name'], ','.join(['%s' % player['name'] for player in r['players']]), r['common'], r['hunters'], r['smokers'], r['boomers'], r['tanks']) \
		for r in filter(lambda r: r['map']['game'] == 1, records)]

	message_list.append('')
	message_list.append('Left 4 Dead 2')
	message_list.append('date;time;map;players;common;hunters;smokers;boomers;chargers;spitters;jockeys;tanks')

	message_list += [ \
		'%s;%s;%s;%s;%d;%d;%d;%d;%d;%d;%d;%d' % \
		(r['date'], format_time(r['time']), r['map']['name'], ','.join(['%s' % player['name'] for player in r['players']]), r['common'], r['hunters'], r['smokers'], r['boomers'], r['chargers'], r['spitters'], r['jockeys'], r['tanks']) \
		for r in filter(lambda r: r['map']['game'] == 2, records)]

	export_batch_text_google_spreadsheet(user, pw, message_list, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = curr_wksht_id, verbose = verbose)

#--------------------------------------------------
# test1()
#--------------------------------------------------
def test1():
	players = []
	maps = []
	records = []

	import_player_list('players.txt', players)
	import_map_list('maps.txt', maps)
	import_record_list('records.txt', records, players, maps)
	f1 = open('new_records.csv', 'r')
	import_record_list_csv(f1, records, players, maps)
	f1.close()

	#print_players(players)
	#print_records(records)
	#print input_new_record(records, maps, players, raw_input, sys.stdout)
	print
	export_players_list(sys.stdout, players)
	print '\n'
	export_maps_list(sys.stdout, maps)
	print '\n'
	export_records_list(sys.stdout, records)
	print

#--------------------------------------------------
# export_text_google_spreadsheet(user, pw, text)
#--------------------------------------------------
def export_text_google_spreadsheet(user, pw, text):
	"""Send this function a list of lines, each line uses semicolon to separate columns"""
	gd_client = gdata.spreadsheet.service.SpreadsheetsService()
	gd_client.email = user
	gd_client.password = pw
	gd_client.ProgrammaticLogin()
	curr_key = ''
	curr_wksht_id = ''
	list_feed = None

	# Get the list of spreadsheets
	feed = gd_client.GetSpreadsheetsFeed()
	_PrintFeed(feed)
	input = raw_input('\nSelection: ')
	id_parts = feed.entry[string.atoi(input)].id.text.split('/')
	curr_key = id_parts[len(id_parts) - 1]

	# Get the list of worksheets
	feed = gd_client.GetWorksheetsFeed(curr_key)
	_PrintFeed(feed)
	input = raw_input('\nSelection: ')
	id_parts = feed.entry[string.atoi(input)].id.text.split('/')
	curr_wksht_id = id_parts[len(id_parts) - 1]

	update = lambda r,c,v: update_cell(gd_client, curr_key, curr_wksht_id, r, c, v)

	row = 1
	for line in text:
		col = 1
		for phrase in line.split(';'):
			update(row, col, phrase)
			col += 1
		row += 1

def find(f, seq):
	"""Return first item in sequence where f(item) == True."""
	for item in seq:
		if f(item): 
			return item
#--------------------------------------------------
# export_batch_text_google_spreadsheet(user, pw, text)
#--------------------------------------------------
def export_batch_text_google_spreadsheet(user, pw, text, gd_client = None, curr_key = None, curr_wksht_id = None, remove_extra_text = True, verbose = False):
	"""Send this function a list of lines, each line uses semicolon to separate columns"""
	if gd_client == None:
		gd_client = gdata.spreadsheet.service.SpreadsheetsService()
		gd_client.email = user
		gd_client.password = pw
		gd_client.ProgrammaticLogin()
	list_feed = None

	# Get the list of spreadsheets
	if curr_key == None:
		curr_key = get_key(gd_client)

	# Get the list of worksheets
	if curr_wksht_id == None:
		curr_wksht_id = get_wksht(gd_client, curr_key)

	cells = gd_client.GetCellsFeed(curr_key, wksht_id = curr_wksht_id)
	batchRequest = gdata.spreadsheet.SpreadsheetsCellsFeed()
	update = lambda r,c,v: update_cell(gd_client, curr_key, curr_wksht_id, r, c, v)

	batch_count = 0
	single_update_list = []
	for i,r in enumerate(text):
		for j,c in enumerate(r.split(';')):
			entry = find(lambda entry: entry != None and int(entry.cell.row) == i+1 and int(entry.cell.col) == j+1, cells.entry)
			if entry != None:
				if entry.cell.text.strip() != c:
					entry.cell.text = c
					entry.cell.inputValue = c
					batchRequest.AddUpdate(entry)
					batch_count += 1
			else:
				single_update_list.append((i+1, j+1, c))

	if remove_extra_text == True:
		row_list = []
		for i,r in enumerate(text):
			for j,c in enumerate(r.split(';')):
				row_list.append((i+1, j+1))

		for entry in cells.entry:
			if not (int(entry.cell.row), int(entry.cell.col)) in row_list and entry.cell.text.strip() != '':
				entry.cell.inputValue = ''
				batch_count += 1
				batchRequest.AddUpdate(entry)

	if verbose == True:
		print '   batch update %d cells...' % (batch_count)
	updated = gd_client.ExecuteBatch(batchRequest, cells.GetBatchLink().href)

	if verbose == True:
		print '   single update %d cells...' % (len(single_update_list))
	for (r, c, v) in single_update_list:
		update(r,c,v)

def kill_factor(record):
	"""average SI kills per minute"""
	average = lambda x: sum(x) / len(x)
	if record['map']['game'] == 1:
		minutes = record['time'].seconds / 60.0
		kills = average([float(record[si]) for si in ['hunters', 'smokers', 'boomers', 'tanks']])
		return kills / minutes

	elif record['map']['game'] == 2:
		minutes = record['time'].seconds / 60.0
		kills = average([float(record[si]) for si in ['hunters', 'smokers', 'boomers', 'spitters', 'chargers', 'jockeys', 'tanks']])
		return kills / minutes

def gore_factor(record):
	"""total si kills"""
	if record['map']['game'] == 1:
		return sum([record[si] for si in ['hunters', 'smokers', 'boomers', 'tanks']])

	elif record['map']['game'] == 2:
		return sum([record[si] for si in ['hunters', 'smokers', 'boomers', 'spitters', 'chargers', 'jockeys', 'tanks']])

def trash_factor(record):
	"""Ideas for kill factor:
	trash: Highest time is cool but what you want is the hightest kill factor which is way better.What you do is add all si killed without the tanks and divide by the minutes and you get a number. In l4d the number should be over 7 and l4d2 the number should be over 6. The best or most fun games are over 9
	"""
	if record['map']['game'] == 1:
		minutes = record['time'].seconds / 60.0
		kills = sum([record[si] for si in ['hunters', 'smokers', 'boomers']])
		return kills / minutes

	elif record['map']['game'] == 2:
		minutes = record['time'].seconds / 60.0
		kills = sum([record[si] for si in ['hunters', 'smokers', 'boomers', 'spitters', 'chargers', 'jockeys']])
		return kills / minutes

#--------------------------------------------------
# export_statistics_google_spreadsheet(user, pw, records, players, maps)
#--------------------------------------------------
def export_statistics_top10_google_spreadsheet(user, pw, records, players, maps):
	message_list = []
	message_list.append('top10 times L4D1')
	message_list.append('')
	# find the top times for each map
	for m in filter(lambda m: m['game'] == 1, maps):
		message_list.append(m['name'])
		poss_records = filter(lambda r: r['map'] == m, records)
		for i, best in enumerate(sorted(poss_records, reverse = True, key = lambda r: r['time'])[0:10]):
			message_list.append('%d:;%02d:%02d:%02d.%02d;%s' % (i, best['time'].seconds / 3600, best['time'].seconds % 3600 / 60, best['time'].seconds % 3600 % 60, best['time'].microseconds / 10000, \
				';'.join([p['name'] for p in best['players']])))
		message_list.append('')
	message_list.append('top10 times L4D2')
	message_list.append('')
	for m in filter(lambda m: m['game'] == 2, maps):
		message_list.append(m['name'])
		poss_records = filter(lambda r: r['map'] == m, records)
		for i, best in enumerate(sorted(poss_records, reverse = True, key = lambda r: r['time'])[0:10]):
			message_list.append('%d:;%02d:%02d:%02d.%02d;%s' % (i, best['time'].seconds / 3600, best['time'].seconds % 3600 / 60, best['time'].seconds % 3600 % 60, best['time'].microseconds / 10000, \
				';'.join([p['name'] for p in best['players']])))
		message_list.append('')
	export_batch_text_google_spreadsheet(user, pw, message_list)

#--------------------------------------------------
# gen_statistics
#--------------------------------------------------
def gen_statistics(records, players, maps, factor, n = 1):
	return [(m, sorted(filter(lambda r: r['map'] == m, records), key = factor, reverse = True)[0:n]) for m in maps]

def get_key(gd_client, prompt = True, input = None):
	feed = gd_client.GetSpreadsheetsFeed()
	if prompt == True:
		_PrintFeed(feed)
		input = raw_input('\nSelection: ')
	id_parts = feed.entry[string.atoi(input)].id.text.split('/')
	curr_key = id_parts[len(id_parts) - 1]
	return curr_key

def get_wksht(gd_client, curr_key, prompt = True, input = None):
	feed = gd_client.GetWorksheetsFeed(curr_key)
	if prompt == True:
		_PrintFeed(feed)
		input = raw_input('\nSelection: ')
	id_parts = feed.entry[string.atoi(input)].id.text.split('/')
	curr_wksht_id = id_parts[len(id_parts) - 1]
	return curr_wksht_id

def format_time(t):
	return '%02d:%02d:%02d.%02d' % (t.seconds / 3600, t.seconds % 3600 / 60, t.seconds % 3600 % 60, t.microseconds / 10000)

#--------------------------------------------------
# export_stats_top10_google_spreadsheet
#--------------------------------------------------
def export_stats_top10_google_spreadsheet(records, players, maps, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
	if gd_client == None:
		gd_client = gdata.spreadsheet.service.SpreadsheetsService()
		gd_client.email = user
		gd_client.password = pw
		gd_client.ProgrammaticLogin()
	list_feed = None

	# Get the list of spreadsheets
	if curr_key == None:
		curr_key = get_key(gd_client)

	# Get the list of worksheets
	if curr_wksht_id == None:
		curr_wksht_id = get_wksht(gd_client, curr_key)

	message_list = []

	# get top times
	def add_stat_message_list(label, fcn, more_info = '', add_stat = False):
		stats = gen_statistics(records, players, maps, factor = fcn, n = 10)
		for game in [1, 2]:
			message_list.append('Best %s L4D%d;%s' % (label,game,more_info))
			for (m, rlist) in filter(lambda s: s[0]['game'] == game, stats):
				message_list.append(m['name'])
				for i,rec in enumerate(rlist):
					if add_stat == True:
						message_list.append('%d:;%s;%s;%s' % (i+1, fcn(rec), format_time(rec['time']), ';'.join([p['name'] for p in rec['players']])))
					else:
						message_list.append('%d:;%s;%s' % (i+1, format_time(rec['time']), ';'.join([p['name'] for p in rec['players']])))
				for index in range(len(rlist) + 1, 11):
					message_list.append('%d:;None' % (index))
				message_list.append('')

	add_stat_message_list('Time', lambda r: r['time'])
	add_stat_message_list('Kill Factor', kill_factor, add_stat = True, more_info='avg SI kills/min')
	#print '\n'.join(message_list)
	export_batch_text_google_spreadsheet(user, pw, message_list, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=curr_wksht_id, verbose=verbose)

#--------------------------------------------------
# export_stats_google_spreadsheet
#--------------------------------------------------
def export_stats_google_spreadsheet(records, players, maps, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
	if gd_client == None:
		gd_client = gdata.spreadsheet.service.SpreadsheetsService()
		gd_client.email = user
		gd_client.password = pw
		gd_client.ProgrammaticLogin()
	list_feed = None

	# Get the list of spreadsheets
	if curr_key == None:
		curr_key = get_key(gd_client)

	# Get the list of worksheets
	if curr_wksht_id == None:
		curr_wksht_id = get_wksht(gd_client, curr_key)

	message_list = []

	# get top times
	def add_stat_message_list(label, fcn, more_info = '', add_stat = False):
		stats = gen_statistics(records, players, maps, factor = fcn)
		for game in [1, 2]:
			message_list.append('Best %s L4D%d;%s' % (label,game,more_info))
			for (m, rlist) in filter(lambda s: s[0]['game'] == game, stats):
				if rlist == []:
					message_list.append('%s;None' % m['name'])
				else:
					rec = rlist[0]
					if add_stat == True:
						message_list.append('%s;%s;%s;%s' % (m['name'], fcn(rec), format_time(rec['time']), ';'.join([p['name'] for p in rec['players']])))
					else:
						message_list.append('%s;%s;%s' % (m['name'], format_time(rec['time']), ';'.join([p['name'] for p in rec['players']])))
			message_list.append('')

	add_stat_message_list('Time', lambda r: r['time'])
	add_stat_message_list('Tank Kills', lambda r: r['tanks'], add_stat = True)
	add_stat_message_list('Kill Factor', kill_factor, add_stat = True, more_info='avg SI kills/min')
	add_stat_message_list('Gore Factor', gore_factor, add_stat = True, more_info='total SI kills')
	add_stat_message_list('Trash Factor', trash_factor, add_stat = True, more_info='total SI kills/min')
	add_stat_message_list('Common Kills', lambda r: r['common'], add_stat = True, more_info='')
	#print '\n'.join(message_list)
	export_batch_text_google_spreadsheet(user, pw, message_list, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=curr_wksht_id, verbose = verbose)

def test2():
	players = []
	maps = []
	records = []
	import_player_list('players.txt', players)
	import_map_list('maps.txt', maps)
	import_record_list('records.txt', records, players, maps)
	f1 = open('new_records.csv', 'r')
	msg = import_record_list_csv(f1, records, players, maps)
	if msg != None: print msg
	f1.close()

	print_records(records)
	user = raw_input('user: ')
	pw = raw_input('pw: ')

	#export_maps_google_spreadsheet(user, pw, maps)
	#export_players_google_spreadsheet(user, pw, players)
	#export_records_google_spreadsheet(user=user, pw=pw, records=records)
	#export_stats_google_spreadsheet(user=user, pw=pw, records=records, players=players, maps=maps)
	export_stats_top10_google_spreadsheet(records, players, maps, user = user, pw = pw, gd_client = None, curr_key = None, curr_wksht_id = None)
	#export_statistics_top10_google_spreadsheet(user, pw, records, players, maps)

players = []
maps = []
records = []
import_player_list('players.txt', players)
import_map_list('maps.txt', maps)
import_record_list('records.txt', records, players, maps)
f1 = open('new_records.csv', 'r')
msg = import_record_list_csv(f1, records, players, maps)
if msg != None: print msg
f1.close()

user = raw_input('user: ')
pw = raw_input('pw: ')

gd_client = gdata.spreadsheet.service.SpreadsheetsService()
gd_client.email = user
gd_client.password = pw
gd_client.ProgrammaticLogin()


if raw_input('default spreadsheet and worksheet values? y/n: ') == 'y':
	curr_key = get_key(gd_client, prompt=False, input='0')
	maps_wksht = get_wksht(gd_client, curr_key, prompt=False, input='0')
	player_wksht = get_wksht(gd_client, curr_key, prompt=False, input='1')
	records_wksht = get_wksht(gd_client, curr_key, prompt=False, input='2')
	stats_wksht = get_wksht(gd_client, curr_key, prompt=False, input='3')
	top10_wksht = get_wksht(gd_client, curr_key, prompt=False, input='4')
else:
	curr_key = get_key(gd_client)
	feed = gd_client.GetWorksheetsFeed(curr_key)
	_PrintFeed(feed)

	maps_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('maps wksht: '))
	player_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('player wksht: '))
	records_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('records wksht: '))
	stats_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('stats wksht: '))
	top10_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('top10 wksht: '))

verbose = True
print 'updating maps'
export_maps_google_spreadsheet(user, pw, maps, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=maps_wksht, verbose = verbose)
print 'updating players'
export_players_google_spreadsheet(user, pw, players, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=player_wksht, verbose = verbose)
print 'updating records'
export_records_google_spreadsheet(user=user, pw=pw, records=records, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=records_wksht, verbose = verbose)
print 'updating stats'
export_stats_google_spreadsheet(user=user, pw=pw, records=records, players=players, maps=maps, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=stats_wksht, verbose = verbose)
print 'updating top10'
export_stats_top10_google_spreadsheet(records, players, maps, user = user, pw = pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=top10_wksht, verbose = verbose)
