#==================================================
# survival_records.py - Script to keep track of left 4 dead survival records. The information is tracked inside of dictionaries, which can be imported and exported to text files.
#==================================================
import datetime
import sys

def import_list(filename, list):
	f = open(filename, 'r')
	lists = [ dict(item.split('=') for item in line.strip().split(';')) for line in f.readlines()]
	list += lists
	f.close()

def export_players_list(file, players):
	file.write('\n'.join(['name=%s;country=%s;ID=%d;aliases=%s' % (player['name'], player['country'], player['ID'], ','.join(player['aliases'])) for player in players]))

def export_maps_list(file, maps):
	file.write('\n'.join(['name=%s;campaign=%s;game=%d;ID=%d' % (map['name'], map['campaign'], map['game'], map['ID']) for map in maps]))

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

def print_players(players):
	for player in players:
		print "%8s: %s" % ('name', player['name'])
		print "%8s: %s" % ('country', player['country'])
		print "%8s: %s" % ('aliases', player['aliases'])
		print

def print_records(records):
	for record in records:
		print "%s time: %s" % (record['date'], record['time'])
		print "%10s: %s" % ("map", record['map']['name'])
		print "%10s: %s" % ("players", ", ".join([p['name'] for p in record['players']]))

def import_player_list(filename, players):
	import_list(filename, players)
	for player in players:
		player['ID'] = int(player['ID'])
		player['aliases'] = filter(lambda a: a != '', player['aliases'].split(','))

def import_map_list(filename, maps):
	import_list(filename, maps)
	for map in maps:
		map['game'] = int(map['game'])
		map['ID'] = int(map['ID'])

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

def find_id(maps, ID):
	matches = filter(lambda x: x['ID'] == ID, maps)
	assert(len(matches) < 2)

	if len(matches) == 1:
		return matches[0]
	else: return None

def import_record_list(filename, records, players, maps):
	import_list(filename, records)
	for record in records:
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

def import_player_list_csv(file, players):
	label = file.readline().strip().split(',')
	for line in map(strip, file.readlines()):
		name, country = line[0:1]
		aliases = filter(lambda x: x != '', line[2:])
		msg = create_player(players, name, country, aliases)
		if msg != None: print msg

def import_record_list_csv(file, records, players, maps):
	# first line in the csv file is a label
	label = file.readline().strip().split(',')

	for line in file.readlines():
		game_str, date_str, time_str, map_name, p1_str, p2_str, p3_str, p4_str, common_str, hunters_str, boomers_str, smokers_str, tanks_str = line.strip().split(',')

		# find the matching mp
		mp = [m for m in maps if m['name'] == map_name and m['game'] == int(game_str)]
		if mp == []: return 'Map %s not found' % map_name
		else: mp = mp[0]

		# get player names
		playerlist = []
		for name in [p1_str, p2_str, p3_str, p4_str]:
			player = [p for p in players if p['name'].lower() == name.lower()]
			if player == []: return 'Player %s not found [%s]' % (name, ', '.join([p['name'] for p in players]))
			else: playerlist.append(player[0])

		# get time, date, counts
		times = time_str.split(':')
		time = datetime.timedelta(hours = int(times[0]), minutes = int(times[1]), seconds = int(times[2].split('.')[0]), milliseconds = 10 * int(times[2].split('.')[1]))

		date = datetime.date(*map(int, date_str.split('-')))
		common  = int(common_str)
		hunters = int(hunters_str)
		smokers = int(smokers_str)
		boomers = int(boomers_str)
		tanks   = int(tanks_str)
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

def create_player(players, name, country, aliases):
	# check if name matches any other existing players or aliases
	matches = filter(lambda p: p['name'] == name or name in p['aliases'], players)
	if len(matches > 0): return 'Name %s already matches a player' % name

	# check if any of the aliases matches any existing players or aliases
	for alias in aliases:
		matches = filter(lambda p: p['name'] == alias or alias in p['aliases'], players)
		if len(matches > 0): return 'Alias %s already matches a player' % alias

	# create a new ID by adding 1 to the maximum ID
	new_id = max([player['ID'] for player in players]) + 1
	players.append({'name':name, 'country':country, 'aliases':aliases})
	return None

def create_map(maps, name, campaign, game):
	# check if name matches any other existing maps
	if name in [m['name'] for m in maps]: return 'Name %s already matches an existing map' % name

	# create a new ID by adding 1 to the maximum ID
	new_id = max([m['ID'] for m in maps]) + 1
	maps.append({'name':name, 'campaign':campaign, 'game':game})
	return None

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

def update_cell(gd_client, curr_key, curr_wksht_id, row, col, inputValue):
    entry = gd_client.UpdateCell(row=row, col=col, inputValue=inputValue, 
        key=curr_key, wksht_id=curr_wksht_id)
    if isinstance(entry, gdata.spreadsheet.SpreadsheetsCell):
      return 'Updated!'

def export_maps_google_spreadsheet(user, pw, maps):
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
	update(row, 1, 'Left 4 Dead 1 Maps'); row += 1
	for m in [m for m in maps if m['game'] == 1]:
		update_cell(gd_client, curr_key, curr_wksht_id, row, 1, m['name'])
		update_cell(gd_client, curr_key, curr_wksht_id, row, 2, m['campaign'])
		row += 1

	update(row, 1, 'Left 4 Dead 2 Maps'); row += 1
	for m in [m for m in maps if m['game'] == 2]:
		update_cell(gd_client, curr_key, curr_wksht_id, row, 1, m['name'])
		update_cell(gd_client, curr_key, curr_wksht_id, row, 2, m['campaign'])
		row += 1

def export_players_google_spreadsheet(user, pw, players):
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

	col = 1
	for label in ['name', 'country', 'aliases']:
		update(row, col, label)
		col += 1
	row += 1

	for player in players:
		update(row, 1, player['name'])
		update(row, 2, player['country'])
		update(row, 3, ','.join(player['aliases']))
		row += 1

def export_records_google_spreadsheet(user, pw, records):
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

	col = 1
	for label in 'date,time,map,players,common,hunters,smokers,boomers,tanks'.split(','):
		update(row, col, label)
		col += 1
	row += 1

	for record in records:
		update(row, 1, '%s' % record['date'])
		update(row, 2, '%02d:%02d:%02d.%02d' % (record['time'].seconds / 3600, record['time'].seconds % 3600 / 60, record['time'].seconds % 3600 % 60, record['time'].microseconds / 10000))
		update(row, 3, '%s' % record['map']['name'])
		update(row, 4, ','.join(['%s' % player['name'] for player in record['players']]))
		update(row, 5, '%d' % record['common'])
		update(row, 6, '%d' % record['hunters'])
		update(row, 7, '%d' % record['smokers'])
		update(row, 8, '%d' % record['boomers'])
		update(row, 9, '%d' % record['tanks'])
		row += 1

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

def export_statistics_google_spreadsheet(user, pw, records, players, maps):
	message_list = []

	message_list.append('Best known times L4D1')
	# find the top times for each map
	for m in filter(lambda m: m['game'] == 1, maps):
		poss_records = filter(lambda r: r['map'] == m, records)
		if (poss_records == []):
			message_list.append('%s;None' % (m['name']))
		else:
			best = max(poss_records, key = lambda r: r['time'])
			message_list.append('%s;%02d:%02d:%02d.%02d;%s;%s;%s;%s' % (m['name'], best['time'].seconds / 3600, best['time'].seconds % 3600 / 60, best['time'].seconds % 3600 % 60, best['time'].microseconds / 10000, \
				best['players'][0]['name'], best['players'][1]['name'], best['players'][2]['name'], best['players'][3]['name']))

	message_list.append('')
	message_list.append('Best known times L4D2')

	for m in filter(lambda m: m['game'] == 2, maps):
		poss_records = filter(lambda r: r['map'] == m, records)
		if (poss_records == []):
			message_list.append('%s;None' % (m['name']))
		else:
			best = max(poss_records, key = lambda r: r['time'])
			message_list.append('%s;%02d:%02d:%02d.%02d' % (m['name'], best['time'] / 3600, best['time'] % 3600 / 60, best['time'] % 3600 % 60, best['time'].microseconds / 10000))

	message_list.append('')
	message_list.append('Most Tank Kills L4D1')
	# find the top times for each map
	for m in filter(lambda m: m['game'] == 1, maps):
		poss_records = filter(lambda r: r['map'] == m, records)
		if (poss_records == []):
			message_list.append('%s;None' % (m['name']))
		else:
			best = max(poss_records, key = lambda r: r['tanks'])
			message_list.append('%s;%s;%02d:%02d:%02d.%02d;%s;%s;%s;%s' % (m['name'], best['tanks'], best['time'].seconds / 3600, best['time'].seconds % 3600 / 60, best['time'].seconds % 3600 % 60, best['time'].microseconds / 10000, \
				best['players'][0]['name'], best['players'][1]['name'], best['players'][2]['name'], best['players'][3]['name']))

	message_list.append('')
	message_list.append('Most Tank Kills L4D2')
	# find the top times for each map
	for m in filter(lambda m: m['game'] == 2, maps):
		poss_records = filter(lambda r: r['map'] == m, records)
		if (poss_records == []):
			message_list.append('%s;None' % (m['name']))
		else:
			best = max(poss_records, key = lambda r: r['tanks'])
			message_list.append('%s;%s;%02d:%02d:%02d.%02d;%s;%s;%s;%s' % (m['name'], best['tanks'], best['time'].seconds / 3600, best['time'].seconds % 3600 / 60, best['time'].seconds % 3600 % 60, best['time'].microseconds / 10000, \
				best['players'][0]['name'], best['players'][1]['name'], best['players'][2]['name'], best['players'][3]['name']))

	export_text_google_spreadsheet(user, pw, message_list)

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
#export_records_google_spreadsheet(user, pw, records)
export_statistics_google_spreadsheet(user, pw, records, players, maps)
