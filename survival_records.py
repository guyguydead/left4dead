#==================================================
# survival_records.py - Script to keep track of left 4 dead survival records. The information is tracked inside of dictionaries, which can be imported and exported to text files.
#==================================================
import datetime
import sys
import re
import getopt

"""
def import_list(filename, list):
	f = open(filename, 'r')
	lists = [ dict(item.split('=') for item in line.strip().split(';')) for line in f.readlines()]
	list += lists
	f.close()
"""
#--------------------------------------------------
# import_list(filename, list)
#--------------------------------------------------
def import_list(filename, list):
	f = open(filename, 'r')
	for line in f.readlines():
		lists = dict([ (item[:item.index('=')], item[item.index('=')+1:]) for item in line.strip().split(';') ])
		list.append(lists)
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
	def get_aliases(m):
		if 'aliases' in m:
			return m['aliases']
		else:
			return []
	def get_type(m):
		if 'type' in m:
			return m['type']
		else:
			return ''

	file.write('\n'.join(['ID=%d;name=%s;campaign=%s;game=%d;aliases=%s;type=%s' % (map['ID'], map['name'], map['campaign'], map['game'], ','.join(get_aliases(map)), get_type(map)) for map in maps]))

#--------------------------------------------------
# export_groups_list(file, groups)
#--------------------------------------------------
def export_groups_list(file, groups):
	message_list = []
	for group in groups:
		#print group
		#print
		line = []

		for (k, v) in group.iteritems():
			if k == 'ID':
				line.append('ID=%d' % (group['ID']))
			elif k == 'players':
				line.append('players=%s' % ','.join(['%d' % p['ID'] for p in v]))
			elif k == 'records':
				line.append('records=%s' % ','.join(['%d' % p['ID'] for p in v]))
			elif k == 'countries':
				line.append('countries=%s' % ','.join(v))
			elif k == 'aliases':
				line.append('aliases=%s' % ','.join(v))
			elif k == 'map':
				line.append('map=%d' % v['ID'])
			else:
				line.append('%s=%s' % (k, v))
		message_list.append(';'.join(line))

	file.write('\n'.join(message_list))

#--------------------------------------------------
# export_records_list(file, records)
#--------------------------------------------------
def export_records_list(file, records):
	record_list = []
	for record in records:
		if record['map']['game'] == 1:
			record_list.append('ID=%d;date=%s;time=%02d:%02d:%02d.%02d;map=%d;players=%s;common=%d;hunters=%d;smokers=%d;boomers=%d;tanks=%d' \
				% (record['ID'], \
				record['date'], \
				record['time'].seconds / 3600, record['time'].seconds % 3600 / 60, record['time'].seconds % 3600 % 60, record['time'].microseconds / 10000, \
				record['map']['ID'], \
				','.join(['%d' % player['ID'] for player in record['players']]), \
				record['common'], \
				record['hunters'], \
				record['smokers'], \
				record['boomers'], \
				record['tanks']))

		elif record['map']['game'] == 2:
			record_list.append('ID=%d;date=%s;time=%02d:%02d:%02d.%02d;map=%d;players=%s;common=%d;hunters=%d;smokers=%d;boomers=%d;chargers=%d;spitters=%d;jockeys=%d;tanks=%d' \
				% (record['ID'], \
				record['date'], \
				record['time'].seconds / 3600, record['time'].seconds % 3600 / 60, record['time'].seconds % 3600 % 60, record['time'].microseconds / 10000, \
				record['map']['ID'], \
				','.join(['%d' % player['ID'] for player in record['players']]), \
				record['common'], \
				record['hunters'], \
				record['smokers'], \
				record['boomers'], \
				record['chargers'],
				record['spitters'],
				record['jockeys'],
				record['tanks']))
	file.write('\n'.join(record_list))

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
# import_groups_list(filename, groups)
#--------------------------------------------------
def import_groups_list(filename, groups, players, records, maps):
	import_list(filename, groups)
	for group in groups:
		#print group
		#print 'Convert ID %s' % group['ID']
		group['ID'] = int(group['ID'])

		if 'numplayers' in group:
			group['numplayers'] = int(group['numplayers'])

		if 'game' in group:
			group['game'] = int(group['game'])

		if 'map' in group:
			group['map'] = find_id(maps, int(group['map']))

		# importing list of players
		if 'players' in group:
			try:
				group['players'] = [find_id(players, p) for p in map(int, filter(lambda s: s.strip() != '', group['players'].split(',')))]
			except ValueError:
				return 'Error importing players'

		# importing list a records
		if 'records' in group:
			try:
				group['records'] = [find_id(records, p) for p in map(int, [i.strip() for i in group['records'].split(',') if i.strip() != ''])]
			except ValueError:
				return 'Error importing records'

		for k in ['countries', 'aliases']:
			if k in group:
				group[k] = filter(lambda s: s != '', map(lambda str: str.strip(), group[k].split(',')))


#--------------------------------------------------
# import_player_list(filename, players)
#--------------------------------------------------
def import_player_list(filename, players):
	import_list(filename, players)
	for player in players:
		player['ID'] = int(player['ID'])
		player['aliases'] = filter(lambda a: a != '', player['aliases'].strip().split(','))

#--------------------------------------------------
# import_map_list(filename, maps)
#--------------------------------------------------
def import_map_list(filename, maps):
	import_list(filename, maps)
	for m in maps:
		m['game'] = int(m['game'])
		m['ID'] = int(m['ID'])
		if 'aliases' in m:
			m['aliases'] = map(lambda s: s.strip(), m['aliases'].split(','))

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
	elif len(times) == 4:
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
	new_records = []
	for record in records:
		record['date'] = datetime.date(*(map(int, record['date'].split('-'))))
		record['time'] = create_timedelta(record['time'])
		record['common'] = int(record['common'])
		record['hunters'] = int(record['hunters'])
		record['smokers'] = int(record['smokers'])
		record['boomers'] = int(record['boomers'])
		record['tanks'] = int(record['tanks'])
		record['map'] = find_id(maps, int(record['map']))
		record['game'] = record['map']['game']
		record['ID'] = int(record['ID'])
		try:
			record['chargers'] == int(record['chargers'])
			record['spitters'] == int(record['spitters'])
			record['jockeys'] == int(record['jockeys'])
		except KeyError:
			pass

		record['players'] = [find_id(players, p) for p in map(int, record['players'].split(','))]
		try:
			new_records.append \
			({ \
				'date':record['date'], \
				'time':record['time'], \
				'players':record['players'], \
				'common':record['common'], \
				'hunters':record['hunters'], \
				'smokers':record['smokers'], \
				'boomers':record['boomers'], \
				'tanks':record['tanks'], \
				'map':record['map'], \
				'game':record['game'], \
				'ID':record['ID'], \
				'chargers':int(record['chargers']), \
				'spitters':int(record['spitters']), \
				'jockeys':int(record['jockeys']) \
			})
		except KeyError:
			new_records.append \
			({ \
				'date':record['date'], \
				'time':record['time'], \
				'players':record['players'], \
				'common':record['common'], \
				'hunters':record['hunters'], \
				'smokers':record['smokers'], \
				'boomers':record['boomers'], \
				'tanks':record['tanks'], \
				'map':record['map'], \
				'game':record['game'], \
				'ID':record['ID'], \
			})

	return new_records

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
	if len(matches) > 0: return 'Name %s already matches a player' % name

	# check if any of the aliases matches any existing players or aliases
	for alias in aliases:
		matches = filter(lambda p: equal_name(p['name'], alias) or is_alias(alias, p['aliases']), players)
		if len(matches) > 0: return 'Alias %s already matches a player' % alias

	# create a new ID by adding 1 to the maximum ID
	new_id = max([player['ID'] for player in players]) + 1
	players.append({'name':name, 'country':country, 'aliases':aliases, 'ID':new_id})
	return None

#--------------------------------------------------
# edit_player(players, name, country, aliases)
#--------------------------------------------------
def edit_player(players, name, country, aliases, change_country, change_aliases):
	# find the existing player with the matching name
	matches = filter(lambda p: equal_name(p['name'], name) or is_alias(name, p['aliases']), players)
	if len(matches) == 0: return 'Player %s not found' % name

	player = matches[0]

	if change_aliases:
		# check if any of the aliases matches any existing players or aliases
		for alias in aliases:
			matches = filter(lambda p: p is not player and (equal_name(p['name'], alias) or is_alias(alias, p['aliases'])), players)
			if len(matches) > 0: return 'Alias %s already matches a player' % alias

		# change the aliases
		player['aliases'] = aliases

	if change_country:
		# change the country
		player['country'] = country
	return None

#--------------------------------------------------
# edit_player_name(players, name, country, aliases)
#--------------------------------------------------
def edit_player_name(players, name, aliases):
	player = None
	for alias in aliases:
		matches = filter(lambda p: (equal_name(p['name'], alias) or is_alias(alias, p['aliases'])), players)
		if len(matches) > 0: player = matches[0]

	if player == None:
		return 'None of the aliases provided match a player'

	# check if name matches any other existing players or aliases
	matches = filter(lambda p: p is not player and (equal_name(p['name'], name) or is_alias(name, p['aliases'])), players)
	if len(matches) > 0: return 'Name %s already matches a player' % name

	player['name'] = name

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

def match_group(group, game, mp, name):
	match = [equal_name(name, group['name'])]
	if 'aliases' in group and match[0] == False:
		match[0] = is_alias(name, group['aliases'])
	if 'map' in group:
		match.append(group['map'] == mp)
	if 'game' in group:
		match.append(group['game'] == game)

	return not False in match

#--------------------------------------------------
# create_record_from_strings(players, maps, records, date, time, mapID, plyrsID, common, hunters, smokers, boomers, tanks)
#--------------------------------------------------
def create_record_from_strings(game, players, maps, records, groups, date, time, m, plyrs, grps, common, hunters, smokers, boomers, tanks, chargers = '', spitters = '', jockeys = ''):
	"""Creates a new record, checking for any inconsistencies. This function will return None if successful and return an error message if record creation failed. All arguments should be strings.
	
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


	map_name = m
	# find the matching map
	mp = [m for m in maps if (equal_name(m['name'], map_name) or ('aliases' in m and is_alias(map_name, m['aliases']))) and m['game'] == game]
	if mp == []: return 'Map %s not found' % map_name
	else: mp = mp[0]

	# get player names
	playerlist = []
	for name in filter(lambda p: p.strip() != '', plyrs.split(',')):
		player = [p for p in players if equal_name(p['name'], name) or is_alias(name, p['aliases'])]
		if player == []:
			return 'Player %s not found [%s]' % (name, plyrs)
		else:
			playerlist.append(player[0])

	# find the matching groups
	grouplist = []
	for name in filter(lambda p: p != '', map(lambda s: s.strip(), grps.split(','))):
		group = filter(lambda g: match_group(g, game, mp, name), groups)
		if group == []:
			return 'Group %s not found' % name
		else:
			grouplist.append(group[0])

	# get time, date, counts
	times = time.split(':')

	if len(times) == 3:
		try:
			time = datetime.timedelta(hours = int(times[0]), minutes = int(times[1]), seconds = int(times[2].split('.')[0]), milliseconds = 10 * int(times[2].split('.')[1]))
		except (TypeError, ValueError, IndexError):
			return 'time is in an invalid format'
	elif len(times) == 2:
		try:
			time = datetime.timedelta(minutes = int(times[0]), seconds = int(times[1].split('.')[0]), milliseconds = 10 * int(times[1].split('.')[1]))
		except (TypeError, ValueError, IndexError):
			return 'time is in an invalid format'
	else:
		return 'time is in an invalid format'

	date_arr = date.split('-')
	if len(date_arr) != 3:
		return 'date is in an invalid format'
	try:
		year = int(date_arr[0])
		month = int(date_arr[1])
		day = int(date_arr[2])
		date = datetime.date(year, month, day)
	except (TypeError, ValueError):
		return 'date is in an invalid format'


	# make sure there are no exact duplicates of time and date
	if (date, time) in [(r['date'], r['time']) for r in records]:
		# error, duplicate
		return 'A record with same date and time already exists'

	# also make sure there are no exact duplicate players time, and maps
	if (time, set([p['name'] for p in playerlist]), mp['name']) in [(r['time'], set([p['name'] for p in r['players']]), r['map']['name']) for r in records]:
		return 'There is already a duplicate time, playerlist, and map.'

	try:
		common  = int(common)
	except (TypeError, ValueError):
		return 'common is invalid number'
	try:
		hunters = int(hunters)
	except (TypeError, ValueError):
		return 'hunters is invalid number'
	try:
		smokers = int(smokers)
	except (TypeError, ValueError):
		return 'smokers is invalid number'
	try:
		boomers = int(boomers)
	except (TypeError, ValueError):
		return 'boomers is invalid number'
	try:
		tanks   = int(tanks)
	except (TypeError, ValueError):
		return 'tanks is invalid number'
	new_id = max([p['ID'] for p in records]) + 1

	if game == 2:
		try:
			chargers = int(chargers)
		except (TypeError, ValueError):
			return 'chargers is invalid number'
		try:
			jockeys = int(jockeys)
		except (TypeError, ValueError):
			return 'jockeys is invalid number'
		try:
			spitters = int(spitters)
		except (TypeError, ValueError):
			return 'spitters is invalid number'

	if game == 1:
		new_record = \
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
		}
	elif game == 2:
		new_record = \
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
		}

	records.append(new_record)

	# also add the records to the groups
	for group in grouplist:
		if 'records' in group:
			group['records'].append(new_record)
		else:
			group['records'] = [new_record]
	return None

def edit_record_time_from_strings(game, players, maps, records, date, time, m, plyrs):
	date_arr = date.split('-')
	if len(date_arr) != 3:
		return 'date is in an invalid format'
	try:
		year = int(date_arr[0])
		month = int(date_arr[1])
		day = int(date_arr[2])
		date = datetime.date(year, month, day)
	except (TypeError, ValueError):
		return 'date is in an invalid format'

	map_name = m
	# find the matching map
	mp = [m for m in maps if (equal_name(m['name'], map_name) or ('aliases' in m and is_alias(map_name, m['aliases']))) and m['game'] == game]
	if mp == []: return 'Map %s not found' % map_name
	else: mp = mp[0]

	# get player names
	playerlist = []
	for name in filter(lambda p: p.strip() != '', plyrs.split(',')):
		player = [p for p in players if equal_name(p['name'], name) or is_alias(name, p['aliases'])]
		if player == []:
			return 'Player %s not found [%s]' % (name, plyrs)
		else:
			playerlist.append(player[0])

	# find the record with matching date, map, and players
	matching_records = filter(lambda r: (date, mp, set([p['name'] for p in playerlist])) == (r['date'], r['map'], set([p['name'] for p in r['players']])), records)
	if matching_records == []:
		return 'No matching records found with matching players, date %s and map %s' % (date, mp['name'])

	record = matching_records[0]

	times = time.split(':')

	if len(times) == 3:
		try:
			time = datetime.timedelta(hours = int(times[0]), minutes = int(times[1]), seconds = int(times[2].split('.')[0]), milliseconds = 10 * int(times[2].split('.')[1]))
		except (TypeError, ValueError, IndexError):
			return 'time is in an invalid format'
	elif len(times) == 2:
		try:
			time = datetime.timedelta(minutes = int(times[0]), seconds = int(times[1].split('.')[0]), milliseconds = 10 * int(times[1].split('.')[1]))
		except (TypeError, ValueError, IndexError):
			return 'time is in an invalid format'
	else:
		return 'time is in an invalid format'

	record['time'] = time

	return None

def edit_record_date_from_strings(game, players, maps, records, date, time, m, plyrs):
	# get time, date, counts
	times = time.split(':')

	if len(times) == 3:
		try:
			time = datetime.timedelta(hours = int(times[0]), minutes = int(times[1]), seconds = int(times[2].split('.')[0]), milliseconds = 10 * int(times[2].split('.')[1]))
		except (TypeError, ValueError, IndexError):
			return 'time is in an invalid format'
	elif len(times) == 2:
		try:
			time = datetime.timedelta(minutes = int(times[0]), seconds = int(times[1].split('.')[0]), milliseconds = 10 * int(times[1].split('.')[1]))
		except (TypeError, ValueError, IndexError):
			return 'time is in an invalid format'
	else:
		return 'time is in an invalid format'
	map_name = m

	# find the matching map
	mp = [m for m in maps if (equal_name(m['name'], map_name) or ('aliases' in m and is_alias(map_name, m['aliases']))) and m['game'] == game]
	if mp == []: return 'Map %s not found' % map_name
	else: mp = mp[0]

	# get player names
	playerlist = []
	for name in filter(lambda p: p.strip() != '', plyrs.split(',')):
		player = [p for p in players if equal_name(p['name'], name) or is_alias(name, p['aliases'])]
		if player == []:
			return 'Player %s not found [%s]' % (name, plyrs)
		else:
			playerlist.append(player[0])

	# find the record with matching time, map, and players
	matching_records = filter(lambda r: (time, mp, set([p['name'] for p in playerlist])) == (r['date'], r['map'], set([p['name'] for p in r['players']])), records)
	if matching_records == []:
		return 'No matching records found with matching players, date %s and map %s' % (date, mp['name'])

	date_arr = date.split('-')
	if len(date_arr) != 3:
		return 'date is in an invalid format'
	try:
		year = int(date_arr[0])
		month = int(date_arr[1])
		day = int(date_arr[2])
		date = datetime.date(year, month, day)
	except (TypeError, ValueError):
		return 'date is in an invalid format'
	record['date'] = date

#--------------------------------------------------
# add_group_record_from_strings
#--------------------------------------------------
def add_group_record_from_strings(game, players, maps, records, groups, date, time, m, plyrs, grps):

	times = time.split(':')

	if len(times) == 3:
		try:
			time = datetime.timedelta(hours = int(times[0]), minutes = int(times[1]), seconds = int(times[2].split('.')[0]), milliseconds = 10 * int(times[2].split('.')[1]))
		except (TypeError, ValueError, IndexError):
			return 'time is in an invalid format'
	elif len(times) == 2:
		try:
			time = datetime.timedelta(minutes = int(times[0]), seconds = int(times[1].split('.')[0]), milliseconds = 10 * int(times[1].split('.')[1]))
		except (TypeError, ValueError, IndexError):
			return 'time is in an invalid format'
	else:
		return 'time is in an invalid format'

	date_arr = date.split('-')
	if len(date_arr) != 3:
		return 'date is in an invalid format'
	try:
		year = int(date_arr[0])
		month = int(date_arr[1])
		day = int(date_arr[2])
		date = datetime.date(year, month, day)
	except (TypeError, ValueError):
		return 'date is in an invalid format'


	# find the record with matching time and date
	matching_records = filter(lambda r: (date, time) == (r['date'], r['time']), records)
	if matching_records == []:
		return 'No matching records found with date %s and time %s' % (date, format_time(time))

	record = matching_records[0]

	# find the matching groups
	grouplist = []
	for name in filter(lambda p: p != '', map(lambda s: s.strip(), grps.split(','))):
		group = filter(lambda g: match_group(g, game, m, name), groups)
		if group == []:
			return 'Group %s not found' % name
		else:
			grouplist.append(group[0])

	# also add the records to the groups
	for group in grouplist:
		if 'records' in group:
			if record in group['records']:
				return 'Record is already in the group %s' % group['name']
			else:
				group['records'].append(record)
		else:
			group['records'] = [record]

	return None

#--------------------------------------------------
# edit_record_from_strings(players, maps, records, date, time, mapID, plyrsID, common, hunters, smokers, boomers, tanks)
#--------------------------------------------------
def edit_record_from_strings(game, players, maps, records, date, time, m, plyrs, common, hunters, smokers, boomers, tanks, chargers = '', spitters = '', jockeys = '', edit_players = True, edit_counts = True, edit_map = True):

	times = time.split(':')

	if len(times) == 3:
		try:
			time = datetime.timedelta(hours = int(times[0]), minutes = int(times[1]), seconds = int(times[2].split('.')[0]), milliseconds = 10 * int(times[2].split('.')[1]))
		except (TypeError, ValueError, IndexError):
			return 'time is in an invalid format'
	elif len(times) == 2:
		try:
			time = datetime.timedelta(minutes = int(times[0]), seconds = int(times[1].split('.')[0]), milliseconds = 10 * int(times[1].split('.')[1]))
		except (TypeError, ValueError, IndexError):
			return 'time is in an invalid format'
	else:
		return 'time is in an invalid format'

	date_arr = date.split('-')
	if len(date_arr) != 3:
		return 'date is in an invalid format'
	try:
		year = int(date_arr[0])
		month = int(date_arr[1])
		day = int(date_arr[2])
		date = datetime.date(year, month, day)
	except (TypeError, ValueError):
		return 'date is in an invalid format'


	# find the record with matching time and date
	matching_records = filter(lambda r: (date, time) == (r['date'], r['time']), records)
	if matching_records == []:
		return 'No matching records found with date %s and time %s' % (date, format_time(time))

	record = matching_records[0]

	if edit_map == True:
		map_name = m
		# find the matching map
		mp = [m for m in maps if (equal_name(m['name'], map_name) or ('aliases' in m and is_alias(map_name, m['aliases']))) and m['game'] == game]
		if mp == []: return 'Map %s not found' % map_name

		record['map'] = mp[0]

	if edit_players == True:
		# get player names
		playerlist = []
		for name in filter(lambda p: p.strip() != '', plyrs.split(',')):
			player = [p for p in players if equal_name(p['name'], name) or is_alias(name, p['aliases'])]
			if player == []:
				return 'Player %s not found [%s]' % (name, plyrs)
			else:
				playerlist.append(player[0])
		record['players'] = playerlist


	if edit_counts == True:
		try:
			record['common']  = int(common)
		except (TypeError, ValueError):
			return 'common is invalid number'
		try:
			record['hunters'] = int(hunters)
		except (TypeError, ValueError):
			return 'hunters is invalid number'
		try:
			record['smokers'] = int(smokers)
		except (TypeError, ValueError):
			return 'smokers is invalid number'
		try:
			record['boomers'] = int(boomers)
		except (TypeError, ValueError):
			return 'boomers is invalid number'
		try:
			record['tanks']   = int(tanks)
		except (TypeError, ValueError):
			return 'tanks is invalid number'
		new_id = max([p['ID'] for p in records]) + 1

		if game == 2:
			try:
				record['chargers'] = int(chargers)
			except (TypeError, ValueError):
				return 'chargers is invalid number'
			try:
				record['jockeys'] = int(jockeys)
			except (TypeError, ValueError):
				return 'jockeys is invalid number'
			try:
				record['spitters'] = int(spitters)
			except (TypeError, ValueError):
				return 'spitters is invalid number'
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

def campaign_name_order(m):
	cs1 = ['No Mercy', 'Crash Course', 'Death Toll', 'Dead Air', 'Blood Harvest', 'Last Stand', 'Sacrifice']
	cs2 = ['Dead Center', 'The Passing', 'Dark Carnival', 'Swamp Fever', 'Hard Rain', 'The Parish', 'No Mercy', 'The Sacrifice']
	names = [ 'Generator Room', 'Gas Station', 'Hospital', 'Rooftop', 'Bridge (CC)', 'Truck Depot', 'Drains', 'Church', 'Street', 'Boathouse', 'Crane', 'Construction Site', 'Terminal', 'Runway', 'Warehouse', 'Bridge (BH)', 'Farmhouse', 'Lighthouse', 'Traincar', 'Port', 'Mall Atrium', 'Riverbank', 'Underground', 'Port (P)', 'Motel', 'Stadium Gates', 'Concert', 'Gator Village', 'Plantation', 'Burger Tank', 'Sugar Mill', 'Bus Depot', 'Bridge', 'Generator Room', 'Traincar', 'Port (S)', 'Rooftop' ]

	if m['game'] == 1:
		try:
			m1 = cs1.index(m['campaign'])
		except ValueError:
			m1 = len(cs1) + len(cs2) + ('type' in m and m['type'] == 'custom')
	else: # l4d2
		try:
			m1 = len(cs1) + cs2.index(m['campaign'])
		except ValueError:
			m1 = len(cs1) + len(cs2) + ('type' in m and m['type'] == 'custom')

	try:
		m2 = names.index(m['name'])
	except ValueError:
		m2 = len(names)

	return (m1, m2)

def custom_maps(maps):
	return filter(lambda m: 'type' in m and m['type'] == 'custom', maps)
def official_maps(maps):
	return filter(lambda m: 'type' in m and m['type'] == 'official', maps)

#--------------------------------------------------
# combine_message_lists
#--------------------------------------------------
def combine_message_lists(list1, list2, column_spacing = 0):
	def count(line):
		return line.count(';') - line.count('\\;')

	# find the maximum number of semicolons
	max_list1 = max([count(line) for line in list1])

	for i, line in enumerate(list1):
		list1[i] += ((max_list1 - count(line)) * ';')

	# find the max number of lines
	max_lines = max([len(list1), len(list2)])
	list1 += [';' * (max_list1)] * (max_lines - len(list1))
	list2 += [''] * (max_lines - len(list2))

	combined_list = [x + (';' * (column_spacing + 1)) + y for (x,y) in zip(list1,list2)]
	return combined_list

#--------------------------------------------------
# combine_all_message_lists
#--------------------------------------------------
def combine_all_message_lists(lists, column_spacing = 0):
	combined = lists[0]
	for l in lists[1:]:
		combined = combine_message_lists(combined, l, column_spacing)
	return combined


#--------------------------------------------------
# export_maps_google_spreadsheet(user, pw, maps)
#--------------------------------------------------
def export_maps_google_spreadsheet(user, pw, maps, records, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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

	#message_list = []
	#message_list.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))
	update = lambda r,c,v: update_cell(gd_client, curr_key, curr_wksht_id, r, c, v)

	message_lists = []
	for i,typ in enumerate(['official', 'custom']):
		for game in [1, 2]:
			message_list = []
			message_list.append('Left 4 Dead %d %s Maps' % (game, typ))
			if typ == 'official':
				message_list.append('campaign;name;records')
				message_list += ['%s;%s;%d' % (m['campaign'], m['name'], len(filter(lambda r: r['map'] == m, records))) for m in \
					sorted \
					( \
						filter(lambda m: m['game'] == game, official_maps(maps) if typ == 'official' else custom_maps(maps)), \
						key = lambda m: (campaign_name_order(m), m['campaign'].lower(), m['name'].lower()) \
					)]
			else:
				#message_list.append('campaign;name;records;url')
				message_list.append('campaign;name;records;url')
				"""
				message_list += ['%s;%s;%d' % (m['campaign'], m['name'], len(filter(lambda r: r['map'] == m, records))) for m in \
					sorted \
					( \
						filter(lambda m: m['game'] == game, custom_maps(maps)), \
						key = lambda m: (campaign_name_order(m), m['campaign'].lower(), m['name'].lower()) \
					)]
				"""
				#"""
				message_list += ['%s;%s;%d;=HYPERLINK("%s"\\;"link")' % (m['campaign'], m['name'], len(filter(lambda r: r['map'] == m, records)), m['url']) for m in \
					sorted \
					( \
						filter(lambda m: m['game'] == game, custom_maps(maps)), \
						key = lambda m: (campaign_name_order(m), m['campaign'].lower(), m['name'].lower()) \
					)]
				#"""
			#if game == 1 or i == 0: message_list.append('')

			message_lists.append(message_list)
	#print message_lists
	combined = combine_all_message_lists(message_lists, 1)

	export_batch_text_google_spreadsheet(user, pw, combined, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = curr_wksht_id, verbose=verbose)

#--------------------------------------------------
# export_groups_google_spreadsheet(user, pw, groups)
#--------------------------------------------------
def export_groups_google_spreadsheet(user, pw, groups, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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


	# remove all dictionary entries where the type is missing
	gs = filter(lambda g: 'type' in g, groups)

	message_list1 = []
	message_list1.append('Game Modes')
	message_list1.append('name;description;records')
	for g in sorted \
		( \
			filter(lambda g: g['type'] == 'gamemode', gs), \
			key = lambda g: g['name'].lower() \
		):
		message_list1.append('%s;%s;%d' % (g['name'], g['description'], len(find_group_records(g, records))))

	message_list2 = []
	message_list2.append('Strategies')
	message_list2.append('map;name;description;records')
	for g in sorted \
	( \
		filter(lambda g: g['type'] == 'strategy', gs), \
		key = lambda g: (campaign_name_order(g['map']), g['name'].lower()) \
	):
		message_list2.append \
		( \
			'%s;%s;%s;%d' % \
			( \
				g['map']['name'], \
				g['name'], \
				g['description'], \
				len(find_group_records(g, records)) \
			) \
		)
	message_list3 = []
	message_list3.append('Player Groups')
	message_list3.append('name;total members;url')
	for g in sorted \
	( \
		filter(lambda g: g['type'] == 'playergroup' and 'countries' in g, gs), \
		key = lambda g: g['name'].lower() \
	):
		msg = '%s;%d' % (g['name'], len(find_group_members(g, players)))
		if 'url' in g:
			msg += ';=HYPERLINK("%s"\;"link")' % g['url']
		message_list3.append(msg);
	message_list3.append('')
	for g in sorted \
	( \
		filter(lambda g: g['type'] == 'playergroup' and not 'countries' in g, gs), \
		key = lambda g: g['name'].lower() \
	):
		msg = '%s;%d' % (g['name'], len(find_group_members(g, players)))
		if 'url' in g:
			msg += ';=HYPERLINK("%s"\;"link")' % g['url']
		message_list3.append(msg);

	message_list = combine_all_message_lists([message_list1, message_list2, message_list3], 1)

	message_list.append('')
	message_list.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))

	export_batch_text_google_spreadsheet(user, pw, message_list, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = curr_wksht_id, verbose = verbose)

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
	message_list.append('name;country;records;aliases')
	message_list += \
	[ \
		'%s;%s;%d;%s' % \
		( \
			m['name'], \
			m['country'], \
			len(filter(lambda r: m in r['players'], records)), \
			', '.join(m['aliases']) \
		) \
		for m in sorted \
		( \
			players, \
			key = lambda p: p['name'].lower() \
		) \
	]
	message_list.append('')
	message_list.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))

	export_batch_text_google_spreadsheet(user, pw, message_list, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = curr_wksht_id, verbose = verbose)

#--------------------------------------------------
# export_records_google_spreadsheet(records, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None)
#--------------------------------------------------
def export_records_google_spreadsheet(records, groups, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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

	message_list1 = []
	message_list1.append('Left 4 Dead 1;%d games recorded' % len(filter(lambda r: r['map']['game'] == 1, records)))
	message_list1.append('date;time;map;p1;p2;p3;p4;common;hunters;smokers;boomers;tanks;trash factor;kill factor;score factor;groups')

	message_list1 += \
	[ \
		'%s;%s;%s;%s;%d;%d;%d;%d;%d;%.03f;%.03f;%d;%s' % \
		( \
			r['date'], \
			format_time(r['time']), \
			r['map']['name'], \
			';'.join(['%s' % player['name'] for player in sorted(r['players'], key = lambda p: p['name'].lower())]) + ';' * (4 - len(r['players'])), \
			r['common'], \
			r['hunters'], \
			r['smokers'], \
			r['boomers'], \
			r['tanks'], \
			trash_factor(r), \
			kill_factor(r), \
			score_factor(r), \
			', '.join([group['name'] for group in sorted(find_records_group(r, groups), key = lambda g: g['name'].lower())]) \
		) \
		for r in sorted(filter(lambda r: r['map']['game'] == 1, records), key = lambda r: (campaign_name_order(r['map']), r['date'], r['time'])) \
	]

	#message_list.append('')
	message_list2 = []
	message_list2.append('Left 4 Dead 2;%d games recorded' % len(filter(lambda r: r['map']['game'] == 2, records)))
	message_list2.append('date;time;map;p1;p2;p3;p4;common;hunters;smokers;boomers;chargers;spitters;jockeys;tanks;trash factor;kill factor;score factor;groups')

	message_list2 += \
	[ \
		'%s;%s;%s;%s;%d;%d;%d;%d;%d;%d;%d;%d;%.03f;%.03f;%d;%s' % \
		( \
			r['date'], \
			format_time(r['time']), \
			r['map']['name'], \
			';'.join(['%s' % player['name'] for player in sorted(r['players'], key = lambda p: p['name'].lower())]) + ';' * (4 - len(r['players'])), \
			r['common'], \
			r['hunters'], \
			r['smokers'], \
			r['boomers'], \
			r['chargers'], \
			r['spitters'], \
			r['jockeys'], \
			r['tanks'], \
			trash_factor(r), \
			kill_factor(r), \
			score_factor(r), \
			', '.join([group['name'] for group in sorted(find_records_group(r, groups), key = lambda g: g['name'].lower())]) \
		) \
		for r in sorted(filter(lambda r: r['map']['game'] == 2, records), key = lambda r: (campaign_name_order(r['map']), r['date'], r['time'])) \
	]

	message_list = combine_message_lists(message_list1, message_list2, 1)
	message_list.append('')
	message_list.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))

	#print '\n'.join(message_list)
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

def splitting(text, delimiter):
	array = []
	status = 0 #0 NORMAL, 1 TOKEN
	current_word = ''
	for i, t in enumerate(text):
		if status == 0:
			if t == delimiter:
				array.append(current_word)
				current_word = ''
			elif t == '\\':
				status = 1
			else:
				current_word += t
				if i == len(text) - 1 and current_word != '':
					array.append(current_word)
					current_word = ''
		else:
			current_word += t
			status = 0
			if i == len(text) - 1 and current_word != '':
				array.append(current_word)
				current_word = ''
	return array

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

	"""
	def splitting(T):
		S = '\;'
		starts = [match.start() for match in re.finditer(re.escape(S), T)]
		T2 = T.replace('\;', '##')
		Tsplit = T2.split(';')

		for i, s in enumerate(starts):
			pos = s
			start_word = 0
			for j, word in enumerate(Tsplit):
				if pos > len(word):
					pos -= len(word) + 1
					start_word = j+1

			starts[i] = (pos, start_word)

		for t in starts:
			Tsplit[t[1]] = Tsplit[t[1]][:t[0]] + ';' + Tsplit[t[1]][t[0]+2:]
		return Tsplit
	"""


	batch_count = 0
	single_update_list = []
	for i,r in enumerate(text):
		for j,c in enumerate(splitting(r, ';')):
			entry = find(lambda entry: entry != None and int(entry.cell.row) == i+1 and int(entry.cell.col) == j+1, cells.entry)
			if entry != None:
				if entry.cell.text.strip() != c.strip():
					entry.cell.text = c
					entry.cell.inputValue = c
					batchRequest.AddUpdate(entry)
					batch_count += 1
			elif entry == None and c.strip() != '':
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

def score_factor(r):
	if r['map']['game'] == 1:
		return int(round(r['time'].seconds + r['time'].microseconds / 1e6) * 2 + r['common'] + (r['hunters'] + r['smokers'] + r['boomers']) * 10 + r['tanks'] * 30)
	elif r['map']['game'] == 2:
		si_score = (r['hunters'] + r['smokers'] + r['boomers'] + r['chargers'] + r['spitters'] + r['jockeys']) * 7
		si_per_min = round((r['hunters'] + r['smokers'] + r['boomers'] + r['chargers'] + r['spitters'] + r['jockeys']) / (r['time'].seconds + r['time'].microseconds / 1e6) * 60, 2)
		bonus = (si_per_min / 10 + 1) * si_score - si_score
		return int(round(r['time'].seconds + r['time'].microseconds / 1e6) + round(r['common'] * 0.5) + (r['hunters'] + r['smokers'] + r['boomers'] + r['chargers'] + r['spitters'] + r['jockeys']) * 7 + r['tanks'] * 25 + bonus)

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
	for m in filter(lambda m: m['game'] == 1, official_maps(maps)):
		message_list.append(m['name'])
		poss_records = filter(lambda r: r['map'] == m, records)
		for i, best in enumerate(sorted(poss_records, reverse = True, key = lambda r: r['time'])[0:10]):
			message_list.append('%d:;%02d:%02d:%02d.%02d;%s' % (i, best['time'].seconds / 3600, best['time'].seconds % 3600 / 60, best['time'].seconds % 3600 % 60, best['time'].microseconds / 10000, \
				';'.join([p['name'] for p in sorted(best['players'], key = lambda p: p['name'].lower())])))
		message_list.append('')
	message_list.append('top10 times L4D2')
	message_list.append('')
	for m in filter(lambda m: m['game'] == 2, official_maps(maps)):
		message_list.append(m['name'])
		poss_records = filter(lambda r: r['map'] == m, records)
		for i, best in enumerate(sorted(poss_records, reverse = True, key = lambda r: r['time'])[0:10]):
			message_list.append('%d:;%02d:%02d:%02d.%02d;%s' % (i, best['time'].seconds / 3600, best['time'].seconds % 3600 / 60, best['time'].seconds % 3600 % 60, best['time'].microseconds / 10000, \
				';'.join([p['name'] for p in best['players']])))
		message_list.append('')
	export_batch_text_google_spreadsheet(user, pw, message_list)

#--------------------------------------------------
# find_records_group
#--------------------------------------------------
def find_records_group(record, groups):
	"""Finds all the groups a record belongs to"""
	grouplist = []
	for group in groups:
		if 'records' in group and record in group['records']:
			grouplist.append(group)
		if 'numplayers' in group and len(record['players']) == group['numplayers']:
			grouplist.append(group)

	return grouplist

#--------------------------------------------------
# find_group_records
#--------------------------------------------------
def find_group_records(group, records):
	"""Finds all the records belonging to a group"""
	recordlist = []
	if 'records' in group:
		recordlist += filter(lambda r: r in group['records'], records)
	if 'numplayers' in group:
		recordlist += filter(lambda r: len(r['players']) == group['numplayers'], records)
	return recordlist

#--------------------------------------------------
# find_group_members
#--------------------------------------------------
def find_group_members(group, players):
	"""generates a list of all group members"""
	playerlist = []

	if 'players' in group:
		playerlist += group['players']

	if 'countries' in group:
		for country in group['countries']:
			playerlist += [p for p in players if equal_name(p['country'], country)]

	return playerlist

#--------------------------------------------------
# gen_statistics
#--------------------------------------------------
def gen_statistics_group_strategy(records, players, maps, groups, factor, n = 1):
	return \
	[ \
		( \
			g, \
			sorted \
			( \
				filter(lambda r: r in g['records'], records), \
				key = factor, \
				reverse = True \
			)[0:n] \
		) \
		for g in filter(lambda g: g['type'] == 'strategy' and 'records' in g, groups) \
	] \
	+ \
	[ (g, []) for g in filter(lambda g: g['type'] == 'strategy' and not 'records' in g, groups) ]

#--------------------------------------------------
# gen_statistics
#--------------------------------------------------
def gen_statistics(records, players, maps, factor, n = 1):
	return \
	[ \
		( \
			m, \
			sorted \
			( \
				filter(lambda r: r['map'] == m, records), \
				key = factor, \
				reverse = True \
			)[0:n] \
		) \
		for m in sorted(maps, key = lambda m: campaign_name_order(m)) \
	]

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
	#return '%02d:%02d:%02d.%02d' % (t.seconds / 3600, t.seconds % 3600 / 60, t.seconds % 3600 % 60, t.microseconds / 10000)
	return '%02d:%02d:%02d' % (t.seconds / 3600, t.seconds % 3600 / 60, t.seconds % 3600 % 60)

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
	def add_stat_message_list(label, fcn, display_fcn = lambda s: '%s' % s, more_info = '', add_stat = False):
		stats = gen_statistics(records, players, official_maps(maps), factor = fcn, n = 10)
		for game in [1, 2]:
			message_list.append('Best %s L4D%d;%s' % (label,game,more_info))
			for (m, rlist) in filter(lambda s: s[0]['game'] == game, stats):
				message_list.append(m['name'])
				for i,rec in enumerate(rlist):
					if add_stat == True:
						message_list.append \
						( \
							'%d:;%s;%s;%s' % \
							( \
								i+1, \
								display_fcn(fcn(rec)), \
								format_time(rec['time']), \
								';'.join([p['name'] for p in sorted(rec['players'], key = lambda p: p['name'].lower())]) \
							) \
						)
					else:
						message_list.append \
						( \
							'%d:;%s;%s' % \
							( \
								i+1, \
								format_time(rec['time']), \
								';'.join([p['name'] for p in sorted(rec['players'], key = lambda p: p['name'].lower())]) \
							) \
						)
				for index in range(len(rlist) + 1, 11):
					message_list.append('%d:' % (index))
				message_list.append('')

	add_stat_message_list('Time', lambda r: r['time'])
	add_stat_message_list('Trash Factor', trash_factor, display_fcn = lambda s: '%.03f' % s, add_stat = True, more_info='total SI kills/min')

	message_list.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))

	export_batch_text_google_spreadsheet(user, pw, message_list, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=curr_wksht_id, verbose=verbose)

def export_na_stats_top10_google_spreadsheet(records, players, maps, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
	na = ['US', 'Canada', 'Mexico']
	def na_players(plist):
		nap = filter(lambda p: p['country'] in na, plist)
		nao = filter(lambda p: not p['country'] in na, plist)
		return len(nap) > len(nao)
	na_records = filter(lambda r: na_players(r['players']), records)
	export_stats_top10_google_spreadsheet(records=na_records, players=players, maps=maps, user=user, pw=pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=curr_wksht_id, verbose=verbose)

#--------------------------------------------------
# export_group_stats_google_spreadsheet
#--------------------------------------------------
def export_group_stats_google_spreadsheet(records, players, maps, groups, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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
	message_list.append('Best Times (Strategy Specific)')
	message_list.append('map;strategy;time;p1;p2;p3;p4')
	def add_stat_message_list(label, fcn, display_fcn = lambda s: '%s' % s,more_info = '', add_stat = False, mlist = message_list):
		stats = gen_statistics_group_strategy(records, players, sorted(official_maps(maps), key = lambda m: (campaign_name_order(m), m['campaign'].lower(), m['name'].lower())), \
			filter(lambda g: g['type'] == 'strategy', groups), factor = fcn)

		for (g, rlist) in sorted(stats, key = lambda (g,r): (campaign_name_order(g['map']), g['map']['campaign'].lower(), g['map']['name'].lower(), g['name'].lower())):
			if rlist == []:
				mlist.append('%s;%s;' % (g['map']['name'], g['name']))
			else:
				rec = rlist[0]
				if add_stat == True:
					mlist.append \
					( \
						'%s;%s;%s;%s;%s' % \
						( \
							g['map']['name'], \
							g['name'], \
							display_fcn(fcn(rec)), \
							format_time(rec['time']), \
							';'.join([p['name'] for p in sorted(rec['players'], key = lambda p: p['name'].lower())]) \
						) \
					)
				else:
					mlist.append \
					( \
						'%s;%s;%s;%s' % \
						( \
							g['map']['name'], \
							g['name'], \
							format_time(rec['time']), \
							';'.join([p['name'] for p in sorted(rec['players'], key = lambda p: p['name'].lower())]) \
						) \
					)
		return mlist

	# get top times
	def add_stat_message_list_gamemode(label, fcn, gamemode, message_list, display_fcn = lambda s: '%s' % s,more_info = '', add_stat = False):
		stats = gen_statistics(find_group_records(gamemode, records), players, filter(lambda m: ('game' in gamemode and m['game'] == gamemode['game']) or (not 'game' in gamemode), sorted(official_maps(maps), key = lambda m: (campaign_name_order(m), m['campaign'].lower(), m['name'].lower()))), factor = fcn)
		for game in [1, 2]:
			#message_list.append('Best %s L4D%d;%s' % (label,game,more_info))
			for (m, rlist) in filter(lambda s: s[0]['game'] == game, \
				sorted(stats, key = lambda (m, rlist): (campaign_name_order(m), m['campaign'].lower(), m['name'].lower()))):
				if rlist == []:
					message_list.append('%s' % m['name'])
				else:
					rec = rlist[0]
					if add_stat == True:
						message_list.append \
						( \
							'%s;%s;%s;%s' % \
							( \
								m['name'], \
								display_fcn(fcn(rec)), \
								format_time(rec['time']), \
								';'.join([p['name'] for p in sorted(rec['players'], key = lambda p: p['name'].lower())]) \
							) \
						)
					else:
						message_list.append \
						( \
							'%s;%s;%s' % \
							( \
								m['name'], \
								format_time(rec['time']), \
								';'.join([p['name'] for p in sorted(rec['players'], key = lambda p: p['name'].lower())]) \
							) \
						)
			if game == 1:
				message_list.append('')
		return message_list

	lists = []
	add_stat_message_list('Time', lambda r: r['time'])
	lists.append(message_list)

	gamemodes = ['smashtv', 'solo', 'nomv']
	list1 = []
	for gamemode in filter(lambda g: g['type'] == 'gamemode' and g['name'] in gamemodes, groups):
		list1.append('Best Timess mode %s' % gamemode['name'])
		list1.append('map;time;player 1;player 2;player 3;player 4')
		add_stat_message_list_gamemode('Time', lambda r: r['time'], gamemode, list1)
		list1.append('')
	lists.append(list1)

	combined = combine_all_message_lists(lists, 1)
	combined.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))
	export_batch_text_google_spreadsheet(user, pw, combined, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=curr_wksht_id, verbose = verbose)

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
	def add_stat_message_list(label, fcn, display_fcn = lambda s: '%s' % s,more_info = '', add_stat = False, map_type = 'official', mlist = message_list):
		stats = gen_statistics(records, players, official_maps(maps) if map_type == 'official' else custom_maps(maps), factor = fcn)
		for game in [1, 2]:
			if more_info == '':
				mlist.append('Best %s L4D%d' % (label,game))
			else:
				mlist.append('Best %s L4D%d (%s)' % (label,game,more_info))

			for (m, rlist) in filter(lambda s: s[0]['game'] == game, stats):
				if rlist == []:
					mlist.append('%s' % m['name'])
				else:
					rec = rlist[0]
					if add_stat == True:
						mlist.append \
						( \
							'%s;%s;%s;%s;%s' % \
							( \
								m['name'], \
								display_fcn(fcn(rec)), \
								format_time(rec['time']), \
								';'.join([p['name'] for p in sorted(rec['players'], key = lambda p: p['name'].lower())]), \
								'%s%s' % (';' * (4 - len(rec['players'])), rec['date']) \
							) \
						)
					else:
						mlist.append \
						( \
							'%s;%s;%s;%s' % \
							( \
								m['name'], \
								format_time(rec['time']), \
								';'.join([p['name'] for p in sorted(rec['players'], key = lambda p: p['name'].lower())]), \
								'%s%s' % (';' * (4 - len(rec['players'])), rec['date']) \
							) \
						)
			mlist.append('')

	message_list1 = []
	add_stat_message_list('Time', lambda r: r['time'], mlist = message_list1)
	add_stat_message_list('Gore Factor', gore_factor, display_fcn = lambda s: '%.03f' % s, add_stat = True, more_info='total SI kills', mlist = message_list1)
	add_stat_message_list('Tank Kills', lambda r: r['tanks'], add_stat = True, mlist = message_list1)
	add_stat_message_list('Common Kills', lambda r: r['common'], add_stat = True, more_info='', mlist = message_list1)

	message_list2 = []
	add_stat_message_list('Trash Factor', trash_factor, display_fcn = lambda s: '%.03f' % s, add_stat = True, more_info='total SI kills/min', mlist = message_list2)
	add_stat_message_list('Kill Factor', kill_factor, display_fcn = lambda s: '%.03f' % s, add_stat = True, more_info='avg SI kills/min', mlist = message_list2)
	add_stat_message_list('Score Factor', score_factor, display_fcn = lambda s: '%.03f' % s, add_stat = True, more_info='', mlist = message_list2)

	message_list3 = []
	add_stat_message_list('Time', lambda r: r['time'], map_type = 'custom', mlist=message_list3)


	combined = combine_all_message_lists([message_list1, message_list2, message_list3], 1)

	combined.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))
	export_batch_text_google_spreadsheet(user, pw, combined, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=curr_wksht_id, verbose = verbose, remove_extra_text = True)

def export_na_stats_google_spreadsheet(records, players, maps, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
	na = ['US', 'Canada', 'Mexico']
	def na_players(plist):
		nap = filter(lambda p: p['country'] in na, plist)
		nao = filter(lambda p: not p['country'] in na, plist)
		return len(nap) > len(nao)
	na_records = filter(lambda r: na_players(r['players']), records)
	export_stats_google_spreadsheet(records=na_records, players=players, maps=maps, user=user, pw=pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=curr_wksht_id, verbose=verbose)

def import_text_google_spreadsheet(user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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

	row_list = [(int(entry.cell.row), int(entry.cell.col), entry.cell.text) for entry in cells.entry]

	max_row = max([row for (row, col, text) in row_list])
	max_col = [0] * max_row

	for row in [row for (row, col, text) in row_list]:
		r = row - 1
		max_col[r] = max([col1 for (row1, col1, text1) in row_list if row1 == row])

	rowlist = []
	for r in range(max_row):
		row = r + 1
		collist = []
		for c in range(max_col[r]):
			col = c + 1
			t = [text1 for (row1, col1, text1) in row_list if row1 == row and col1 == col]
			if t == []:
				collist.append('')
			else:
				collist.append(t[0])
		rowlist.append(collist)
	return rowlist

def add_players_google_spreadsheet(players, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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

	message_list = import_text_google_spreadsheet(user, pw, gd_client, curr_key, curr_wksht_id, verbose)

	if len(message_list) == 0 or not set(message_list[0]) <= set(['name', 'country', 'aliases', 'status', 'errors']):
		new_message_list = ['status;name;country;aliases;errors']
		new_message_list.append([';'.join(col_list) for col_list in message for message in message[1:]])
		export_batch_text_google_spreadsheet(user, pw, new_message_list, gd_client, curr_key, curr_wksht_id, verbose)
		return

	new_message_list = [';'.join(message_list[0])]
	count = 0

	for line in message_list[1:]:
		try:
			status = line[message_list[0].index('status')].strip().lower()
		except IndexError:
			status = ''

		try:
			name = line[message_list[0].index('name')].strip()
		except IndexError:
			name = ''

		try:
			country = line[message_list[0].index('country')].strip()
		except IndexError:
			country = ''

		try:
			aliases = line[message_list[0].index('aliases')].strip().split(',')
		except IndexError:
			aliases = []

		if status == 'add':
			err_msg = create_player(players, name, country, aliases)
			if err_msg == None:
				new_message_list.append('added;%s;%s;%s' % (name, country, ','.join(aliases)))
				count += 1
			else:
				new_message_list.append('error;%s;%s;%s;%s' % (name, country, ','.join(aliases), err_msg))
		elif status == 'edit-name':
			err_msg = edit_player_name(players, name, aliases)
			if err_msg == None:
				new_message_list.append('edited;%s;%s;%s' % (name, country, ','.join(aliases)))
			else:
				new_message_list.append('error;%s;%s;%s;%s' % (name, country, ','.join(aliases), err_msg))
		elif status == 'edit':
			err_msg = edit_player(players, name, country, aliases, change_country = True, change_aliases = True)
			if err_msg == None:
				new_message_list.append('edited;%s;%s;%s' % (name, country, ','.join(aliases)))
			else:
				new_message_list.append('error;%s;%s;%s;%s' % (name, country, ','.join(aliases), err_msg))
		elif status == 'edit-aliases':
			err_msg = edit_player(players, name, country, aliases, change_country = False, change_aliases = True)
			if err_msg == None:
				new_message_list.append('edited;%s;%s;%s' % (name, country, ','.join(aliases)))
			else:
				new_message_list.append('error;%s;%s;%s;%s' % (name, country, ','.join(aliases), err_msg))
		elif status == 'edit-country':
			err_msg = edit_player(players, name, country, aliases, change_country = True, change_aliases = False)
			if err_msg == None:
				new_message_list.append('edited;%s;%s;%s' % (name, country, ','.join(aliases)))
			else:
				new_message_list.append('error;%s;%s;%s;%s' % (name, country, ','.join(aliases), err_msg))
		else:
			new_message_list.append(';'.join(line))

	export_batch_text_google_spreadsheet(user, pw, new_message_list, gd_client, curr_key, curr_wksht_id, verbose)
	print "  Added %d players" % (count)

def add_records_google_spreadsheet(game, records, players, maps, groups, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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

	message_list = import_text_google_spreadsheet(user, pw, gd_client, curr_key, curr_wksht_id, verbose)

	if game == 1:
		labels_required = 'status;date;time;map;players;common;hunters;smokers;boomers;tanks;groups;errors'
	else:
		labels_required = 'status;date;time;map;players;common;hunters;smokers;boomers;chargers;spitters;jockeys;tanks;groups;errors'

	if len(message_list) == 0 or not set(labels_required.split(';')) <= set(message_list[0]):
		new_message_list = [labels_required]
		for message in message_list[1:]:
			new_message_list.append(';'.join([col_list for col_list in message]))
		export_batch_text_google_spreadsheet(user, pw, new_message_list, gd_client, curr_key, curr_wksht_id, verbose)
		return

	new_message_list = [';'.join(message_list[0])]
	count = 0

	for i, line in enumerate(message_list[1:]):
		v = {}
		for j, l in enumerate(labels_required.split(';')):
			try:
				v[l] = line[message_list[0].index(l)].strip()
			except IndexError:
				v[l] = ''

		if v['status'] == 'add':
			if game == 1:
				err_msg = create_record_from_strings(1, players, maps, records, groups, v['date'], v['time'], v['map'], v['players'], v['groups'], v['common'], v['hunters'], v['smokers'], v['boomers'], v['tanks'])
			else:
				err_msg = create_record_from_strings(2, players, maps, records, groups, v['date'], v['time'], v['map'], v['players'], v['groups'], v['common'], v['hunters'], v['smokers'], v['boomers'], v['tanks'], v['chargers'], v['spitters'], v['jockeys'])
			if err_msg == None:
				count += 1
				new_message_list.append('added;%s' % (';'.join(line[1:])))
			else:
				if verbose:
					print 'Error line %d for [%s], %s' % (i, ', '.join(line), err_msg)
				new_message_list.append('error;%s;%s' % (';'.join(line[1:]), 'Error: %s' %err_msg))

		elif v['status'] == 'add-group':
			# if the column containing groups is empty, try taking the group information from the next available spot, which should be the players spot
			if v['groups'].strip() == '':
				v['groups'] = v['players']
				
			err_msg = add_group_record_from_strings \
			( \
				game, \
				players, \
				maps, \
				records, \
				groups, \
				v['date'], \
				v['time'], \
				v['map'], \
				v['players'], \
				v['groups'] \
			)
			if err_msg == None:
				new_message_list.append('groups added;%s' % (';'.join(line[1:])))
			else:
				if verbose:
					print 'Error line %d for [%s], %s' % (i, ', '.join(line), err_msg)
				new_message_list.append('error;%s;%s' % (';'.join(line[1:]), 'Group Add Error: %s' %err_msg))


		elif v['status'] == 'edit-date':
			err_msg = edit_record_date_from_strings \
			( \
				players, \
				maps, \
				records, \
				v['date'], \
				v['time'], \
				v['map'], \
				v['players'] \
			)
			if err_msg == None:
				new_message_list.append('edited;%s' % (';'.join(line[1:])))
			else:
				if verbose:
					print 'Error line %d for [%s], %s' % (i, ', '.join(line), err_msg)
				new_message_list.append('error;%s;%s' % (';'.join(line[1:]), 'Error: %s' %err_msg))
		elif v['status'] == 'edit-time':
			err_msg = edit_record_time_from_strings \
			( \
				game, \
				players, \
				maps, \
				records, \
				v['date'], \
				v['time'], \
				v['map'], \
				v['players'] \
			)
			if err_msg == None:
				new_message_list.append('edited;%s' % (';'.join(line[1:])))
			else:
				if verbose:
					print 'Error line %d for [%s], %s' % (i, ', '.join(line), err_msg)
				new_message_list.append('error;%s;%s' % (';'.join(line[1:]), 'Error: %s' %err_msg))

		elif v['status'] == 'edit-players':
			if game == 1:
				err_msg = edit_record_from_strings \
				( \
					1, \
					players, \
					maps, \
					records, \
					v['date'], \
					v['time'], \
					v['map'], \
					v['players'], \
					v['common'], \
					v['hunters'], \
					v['smokers'], \
					v['boomers'], \
					v['tanks'], \
					edit_players = True, \
					edit_counts = False, \
					edit_map = False \
				)
			else:
				err_msg = edit_record_from_strings \
				( \
					2, \
					players, \
					maps, \
					records, \
					v['date'], \
					v['time'], \
					v['map'], \
					v['players'], \
					v['common'], \
					v['hunters'], \
					v['smokers'], \
					v['boomers'], \
					v['tanks'], \
					v['chargers'], \
					v['spitters'], \
					v['jockeys'], \
					edit_players = True, \
					edit_counts = False, \
					edit_map = False \
				)

			if err_msg == None:
				new_message_list.append('edited;%s' % (';'.join(line[1:])))
			else:
				if verbose:
					print 'Error line %d for [%s], %s' % (i, ', '.join(line), err_msg)
				new_message_list.append('error;%s;%s' % (';'.join(line[1:]), 'Error: %s' %err_msg))

		elif v['status'] == 'edit-counts':
			if game == 1:
				err_msg = edit_record_from_strings \
				( \
					1, \
					players, \
					maps, \
					records, \
					v['date'], \
					v['time'], \
					v['map'], \
					v['players'], \
					v['common'], \
					v['hunters'], \
					v['smokers'], \
					v['boomers'], \
					v['tanks'], \
					edit_players = False, \
					edit_counts = True, \
					edit_map = False \
				)
			else:
				err_msg = edit_record_from_strings \
				( \
					2, \
					players, \
					maps, \
					records, \
					v['date'], \
					v['time'], \
					v['map'], \
					v['players'], \
					v['common'], \
					v['hunters'], \
					v['smokers'], \
					v['boomers'], \
					v['tanks'], \
					v['chargers'], \
					v['spitters'], \
					v['jockeys'], \
					edit_players = False, \
					edit_counts = True, \
					edit_map = False \
				)

			if err_msg == None:
				new_message_list.append('edited;%s' % (';'.join(line[1:])))
			else:
				if verbose:
					print 'Error line %d for [%s], %s' % (i, ', '.join(line), err_msg)
				new_message_list.append('error;%s;%s' % (';'.join(line[1:]), 'Error: %s' %err_msg))

		elif v['status'] == 'edit-map':
			if game == 1:
				err_msg = edit_record_from_strings \
				( \
					1, \
					players, \
					maps, \
					records, \
					v['date'], \
					v['time'], \
					v['map'], \
					v['players'], \
					v['common'], \
					v['hunters'], \
					v['smokers'], \
					v['boomers'], \
					v['tanks'], \
					edit_players = True, \
					edit_counts = True, \
					edit_map = True \
				)
			else:
				err_msg = edit_record_from_strings \
				( \
					2, \
					players, \
					maps, \
					records, \
					v['date'], \
					v['time'], \
					v['map'], \
					v['players'], \
					v['common'], \
					v['hunters'], \
					v['smokers'], \
					v['boomers'], \
					v['tanks'], \
					v['chargers'], \
					v['spitters'], \
					v['jockeys'], \
					edit_players = True, \
					edit_counts = True, \
					edit_map = True \
				)

			if err_msg == None:
				new_message_list.append('edited;%s' % (';'.join(line[1:])))
			else:
				if verbose:
					print 'Error line %d for [%s], %s' % (i, ', '.join(line), err_msg)
				new_message_list.append('error;%s;%s' % (';'.join(line[1:]), 'Error: %s' %err_msg))

		elif v['status'] == 'edit':
			if game == 1:
				err_msg = edit_record_from_strings \
				( \
					1, \
					players, \
					maps, \
					records, \
					v['date'], \
					v['time'], \
					v['map'], \
					v['players'], \
					v['common'], \
					v['hunters'], \
					v['smokers'], \
					v['boomers'], \
					v['tanks'], \
					edit_players = True, \
					edit_counts = True, \
					edit_map = True \
				)
			else:
				err_msg = edit_record_from_strings \
				( \
					2, \
					players, \
					maps, \
					records, \
					v['date'], \
					v['time'], \
					v['map'], \
					v['players'], \
					v['common'], \
					v['hunters'], \
					v['smokers'], \
					v['boomers'], \
					v['tanks'], \
					v['chargers'], \
					v['spitters'], \
					v['jockeys'], \
					edit_players = True, \
					edit_counts = True, \
					edit_map = True \
				)

			if err_msg == None:
				new_message_list.append('edited;%s' % (';'.join(line[1:])))
			else:
				if verbose:
					print 'Error line %d for [%s], %s' % (i, ', '.join(line), err_msg)
				new_message_list.append('error;%s;%s' % (';'.join(line[1:]), 'Error: %s' %err_msg))
		else:
			new_message_list.append(';'.join(line))

	if verbose:
		print '  Added %d records' % (count)
	export_batch_text_google_spreadsheet(user, pw, new_message_list, gd_client, curr_key, curr_wksht_id, False)

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

def main():
	pass

players = []
maps = []
records = []
groups = []
import_player_list('players.txt', players)
import_map_list('maps.txt', maps)
records = import_record_list('records.txt', records, players, maps)
err = import_groups_list('groups.txt', groups, players, records, maps)
if err != None:
	print 'Error: %s' % err
print 'done import'

#export_groups_list(sys.stdout, groups)
#raw_input()

#f1 = open('new_records.csv', 'r')
#msg = import_record_list_csv(f1, records, players, maps)
#if msg != None: print msg
#f1.close()

use_defaults = True
user = None
pw = None
# parse command line options
try:
	opts, args = getopt.getopt(sys.argv[1:], "", ["user=", "pw="])
	# Process options
	for o, a in opts:
		if o == "--user":
			user = a
		elif o == "--pw":
			pw = a
except getopt.error, msg:
	user = raw_input('user: ')
	pw = raw_input('pw: ')

if user == None:
	user = raw_input('user: ')
if pw == None:
	pw = raw_input('pw: ')

gd_client = gdata.spreadsheet.service.SpreadsheetsService()
gd_client.email = user
gd_client.password = pw
gd_client.ProgrammaticLogin()

if use_defaults == True or raw_input('default spreadsheet and worksheet values? y/n: ') == 'y':
	curr_key = get_key(gd_client, prompt=False, input='0')
	maps_wksht = get_wksht(gd_client, curr_key, prompt=False, input='0')
	player_wksht = get_wksht(gd_client, curr_key, prompt=False, input='1')
	records_wksht = get_wksht(gd_client, curr_key, prompt=False, input='2')
	stats_wksht = get_wksht(gd_client, curr_key, prompt=False, input='3')
	top10_wksht = get_wksht(gd_client, curr_key, prompt=False, input='4')
	na_wksht = get_wksht(gd_client, curr_key, prompt=False, input='5')
	na_top10_wksht = get_wksht(gd_client, curr_key, prompt=False, input='6')
	group_stats_wksht = get_wksht(gd_client, curr_key, prompt=False, input='7')
	add_player_wksht = get_wksht(gd_client, curr_key, prompt=False, input='8')
	add_record1_wksht = get_wksht(gd_client, curr_key, prompt=False, input='9')
	add_record2_wksht = get_wksht(gd_client, curr_key, prompt=False, input='10')
	group_wksht = get_wksht(gd_client, curr_key, prompt=False, input='11')
else:
	curr_key = get_key(gd_client)
	feed = gd_client.GetWorksheetsFeed(curr_key)
	_PrintFeed(feed)

	maps_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('maps wksht: '))
	player_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('player wksht: '))
	records_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('records wksht: '))
	stats_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('stats wksht: '))
	top10_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('top10 wksht: '))
	na_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('na wksht: '))
	na_top10_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('na top10 wksht: '))
	group_stats_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('group wksht: '))
	add_player_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('add player wksht: '))
	add_record1_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('add record1 wksht: '))
	add_record2_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('add record2 wksht: '))
	group_wksht = get_wksht(gd_client, curr_key, prompt=False, input=raw_input('group wksht: '))

verbose = True

print 'adding new players'
add_players_google_spreadsheet(players, user, pw, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = add_player_wksht, verbose = False)

players_file = open('players.txt', 'w')
export_players_list(players_file, players)
players_file.close()

print 'adding l4d1 records'
add_records_google_spreadsheet(1, records, players, maps, groups, user, pw, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = add_record1_wksht, verbose = True)
print 'adding l4d2 records'
add_records_google_spreadsheet(2, records, players, maps, groups, user, pw, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = add_record2_wksht, verbose = True)


records_file = open('records.txt', 'w')
export_records_list(records_file, records)
records_file.close()
groups_file = open('groups.txt', 'w')
export_groups_list(groups_file, groups)
groups_file.close()

print 'updating maps'
export_maps_google_spreadsheet(user, pw, maps, records, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=maps_wksht, verbose = verbose)
print 'updating players'
export_players_google_spreadsheet(user, pw, players, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=player_wksht, verbose = verbose)
print 'updating records'
export_records_google_spreadsheet(user=user, pw=pw, records=records, groups=groups, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=records_wksht, verbose = verbose)
print 'updating stats'
export_stats_google_spreadsheet(user=user, pw=pw, records=records, players=players, maps=maps, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=stats_wksht, verbose = verbose)
print 'updating top10'
export_stats_top10_google_spreadsheet(records, players, maps, user = user, pw = pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=top10_wksht, verbose = verbose)
print 'updating na stats'
export_na_stats_google_spreadsheet(user=user, pw=pw, records=records, players=players, maps=maps, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=na_wksht, verbose = verbose)
print 'updating na top10'
export_na_stats_top10_google_spreadsheet(records, players, maps, user = user, pw = pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=na_top10_wksht, verbose = verbose)
print 'updating group stats'
export_group_stats_google_spreadsheet(records, players, maps, groups, user=user, pw=pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=group_stats_wksht, verbose=verbose)
print 'updating groups'
export_groups_google_spreadsheet(user, pw, groups, gd_client, curr_key, group_wksht, verbose = verbose)


if __name__ == '__main__':
  main()
