#==================================================
# survival_records.py - Script to keep track of left 4 dead survival records. The information is tracked inside of dictionaries, which can be imported and exported to text files.
#
# TODO list:
# player steamid hashes
#==================================================
import datetime
import sys
import re
import getopt
import survival as sv

DAYS = ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN')

def equal_name(name1, name2):
	return re.sub(r'\s', '', name1).lower() == re.sub(r'\s', '', name2).lower()
def is_alias(name1, aliases_list):
	return filter(lambda n: equal_name(n, name1), aliases_list) != []

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

def official_maps_rt(maps):
	return filter(lambda m: m.type == sv.Map.OFFICIAL, maps)
def custom_maps_rt(maps):
	return filter(lambda m: m.type == sv.Map.CUSTOM, maps)

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
# export_groups_google_spreadsheet_rt
#--------------------------------------------------
def export_groups_google_spreadsheet_rt(rt, user, pw, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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
	message_list1.append('Game Modes')
	message_list1.append('name;description;records')
	for g in sorted \
		( \
			rt.gamemodes, \
			key = lambda g: g.name.lower() \
		):
		message_list1.append('%s;%s;%d' % (g.name, g.description, len(find_group_records_rt(rt, g))))

	message_list2 = []
	message_list2.append('Strategies')
	message_list2.append('map;name;description;records')
	for g in sorted \
	( \
		rt.strategies, \
		key = lambda g: (g.map.order(), g.map.campaign.lower(), g.map.name.lower(), g.name.lower()) \
	):
		message_list2.append \
		( \
			'%s;%s;%s;%d' % \
			( \
				g.map.name, \
				g.name, \
				g.description, \
				len(find_group_records_rt(rt, g)) \
			) \
		)
	message_list3 = []
	message_list3.append('Player Groups')
	message_list3.append('name;total members;url')
	for g in sorted \
	( \
		filter(lambda g: len(g.countries) > 0, rt.playergroups), \
		key = lambda g: g.name.lower() \
	):
		msg = '%s;%d' % (g.name, len(find_country_members_rt(rt, g)))
		#if 'url' in g:
			#msg += ';=HYPERLINK("%s"\;"link")' % g['url']
		message_list3.append(msg);
	message_list3.append('')
	for g in filter(lambda g: len(g.players) > 0, rt.playergroups):
		msg = '%s;%d' % (g.name, len(g.players))
		if g.url != '':
			msg += ';=HYPERLINK("%s"\;"link")' % g.url
		message_list3.append(msg);

	message_list = combine_all_message_lists([message_list1, message_list2, message_list3], 1)

	message_list.append('')
	message_list.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))

	export_batch_text_google_spreadsheet(user, pw, message_list, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = curr_wksht_id, verbose = verbose)

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
	input = raw_input('Selection: ')
	id_parts = feed.entry[string.atoi(input)].id.text.split('/')
	curr_key = id_parts[len(id_parts) - 1]

	# Get the list of worksheets
	feed = gd_client.GetWorksheetsFeed(curr_key)
	_PrintFeed(feed)
	input = raw_input('Selection: ')
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

	if verbose:
		print '   Getting cells feed...'

	query = gdata.spreadsheet.service.CellQuery()
	query.return_empty = "true"
	cells = gd_client.GetCellsFeed(curr_key, wksht_id = curr_wksht_id, query=query)

	batchRequest = gdata.spreadsheet.SpreadsheetsCellsFeed()

	if verbose == True:
		print '   reading current cells...'

	max_row_spreadsheet = max(map(int, [entry.cell.row for entry in cells.entry]))
	max_col_spreadsheet = max(map(int, [entry.cell.col for entry in cells.entry]))
	max_row_text = len(text)
	max_col_text = 1

	batch_count = 0

	for i,r in enumerate(text):
		for j,c in enumerate(splitting(r, ';')):

			if j + 1 > max_col_text:
				max_col_text = j + 1

			if i < max_row_spreadsheet and j < max_col_spreadsheet:
				entry = cells.entry[i * max_col_spreadsheet + j]
				if (entry.cell.text != None and entry.cell.text.strip() != c.strip()) or (entry.cell.text == None and c.strip() != ''):
					entry.cell.text = c
					entry.cell.inputValue = c
					batchRequest.AddUpdate(entry)
					batch_count += 1

	if remove_extra_text == True:
		# remove extra rows
		if max_row_spreadsheet > max_row_text:
			for entry in cells.entry[max_row_text * max_col_spreadsheet:]:
				if entry.cell.text != None:
					entry.cell.text = ''
					entry.cell.inputValue = ''
					batchRequest.AddUpdate(entry)
					batch_count += 1
		# remove extra columns
		if max_col_spreadsheet > max_col_text:
			for r in range(max_row_spreadsheet):
				for entry in cells.entry[r * max_col_spreadsheet + max_col_text : (r+1) * max_col_spreadsheet]:
					if entry.cell.text != None:
						entry.cell.text = ''
						entry.cell.inputValue = ''
						batchRequest.AddUpdate(entry)
						batch_count += 1

	if verbose == True:
		print '   batch update %d cells...' % (batch_count)
	updated = gd_client.ExecuteBatch(batchRequest, cells.GetBatchLink().href)

#--------------------------------------------------
# Checks that the record does not use a gamemode that is a mutation
#--------------------------------------------------
def mutation_record_rt(rt, rec):
	return filter(lambda g: isinstance(g, sv.Gamemode) and g.mutation == True, find_records_group_rt(rt, rec)) != []

#--------------------------------------------------
# find_records_group_rt
#--------------------------------------------------
def find_records_group_rt(rt, record):
	"""Finds all the groups a record belongs to"""
	grouplist = []
	for group in rt.strategies:
		if record in group.records:
			grouplist.append(group)
	for group in rt.gamemodes:
		if record in group.records:
			grouplist.append(group)
		if len(record.players) == group.numplayers:
			grouplist.append(group)

	return grouplist

#--------------------------------------------------
# find_group_records_rt
#--------------------------------------------------
def find_group_records_rt(rt, group):
	"""Finds all the records belonging to a group"""
	recordlist = []
	if isinstance(group, sv.Strategy):
		recordlist += [r for r in group.records]
	elif isinstance(group, sv.Gamemode):
		recordlist += [r for r in group.records]
		recordlist += filter(lambda r: len(r.players) == group.numplayers, rt.records)
	else:
		assert False
	return recordlist

#--------------------------------------------------
# find_group_members_rt
#--------------------------------------------------
def find_group_members_rt(rt, group):
	"""generates a list of all group members"""
	playerlist = []

	playerlist += group.players

	for country in group.countries:
		playerlist += [p for p in rt.players if equal_name(p.country, country)]
	return playerlist

#--------------------------------------------------
# find_groups_player_rt
#--------------------------------------------------
def find_groups_player_rt(rt, player, include_countries = False):
	"""Finds all groups that the player belongs to"""
	if include_countries == False:
		return filter(lambda g: player in g.players, rt.playergroups)
	else:
		return filter(lambda g: (player.country in g.countries) or (player in g.players), rt.playergroups)

#--------------------------------------------------
# find_country_members_rt
#--------------------------------------------------
def find_country_members_rt(rt, group):
	"""generates a list of all group members"""
	playerlist = []

	for country in group.countries:
		playerlist += [p for p in rt.players if equal_name(p.country, country)]
	return playerlist

#--------------------------------------------------
# gen_statistics_group_strategy_rt
#--------------------------------------------------
def gen_statistics_group_strategy_rt(rt, maps, factor, n = 1):
	return \
	[ \
		( \
			g, \
			sorted \
			( \
				g.records, \
				key = factor, \
				reverse = True \
			)[0:n] \
		) \
		for g in filter(lambda s: s.map in maps, rt.strategies) \
	]

#--------------------------------------------------
# gen_statistics_rt
#--------------------------------------------------
def gen_statistics_rt(rt, records, maps, factor, n = 1):
	return \
	[ \
		( \
			m, \
			rt.find_map_records_filtered(m, n, factor, records) \
		) \
		for m in sorted(maps, key = lambda m: m.order()) \
	]

#--------------------------------------------------
# get_key_match
#--------------------------------------------------
def get_key_match(gd_client, prompt = True, input = None):
	feed = gd_client.GetSpreadsheetsFeed()
	if prompt == True:
		_PrintFeed(feed)
		input = raw_input('Selection: ')
	match  = filter(lambda e: e.title.text.strip().lower() == input.strip().lower(), feed.entry)
	if match == []:
		return None
	else:
		return match[0].id.text.split('/')[-1]

#--------------------------------------------------
# get_key
#--------------------------------------------------
def get_key(gd_client, prompt = True, input = None):
	feed = gd_client.GetSpreadsheetsFeed()
	if prompt == True:
		_PrintFeed(feed)
		input = raw_input('Selection: ')
	id_parts = feed.entry[string.atoi(input)].id.text.split('/')
	curr_key = id_parts[len(id_parts) - 1]
	return curr_key

def get_wksht(gd_client, curr_key, prompt = True, input = None):
	feed = gd_client.GetWorksheetsFeed(curr_key)
	if prompt == True:
		_PrintFeed(feed)
		input = raw_input('Selection: ')
	id_parts = feed.entry[string.atoi(input)].id.text.split('/')
	curr_wksht_id = id_parts[len(id_parts) - 1]
	return curr_wksht_id

def format_time(t):
	#return '%02d:%02d:%02d.%02d' % (t.seconds / 3600, t.seconds % 3600 / 60, t.seconds % 3600 % 60, t.microseconds / 10000)
	return '%02d:%02d:%02d' % (t.seconds / 3600, t.seconds % 3600 / 60, t.seconds % 3600 % 60)

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

#--------------------------------------------------
# create_player_rt(players, name, country, aliases)
#--------------------------------------------------
def create_player_rt(rt, name, country, aliases, playergroups_string = ''):
	# check if name matches any other existing players or aliases
	matches = filter(lambda p: equal_name(p.name, name) or is_alias(name, p.aliases), rt.players)
	if len(matches) > 0: return 'Name %s already matches a player' % name

	# check if any of the aliases matches any existing players or aliases
	for alias in aliases:
		matches = filter(lambda p: equal_name(p.name, alias) or is_alias(alias, p.aliases), rt.players)
		if len(matches) > 0: return 'Alias %s already matches a player' % alias

	p = rt.add_player(name, country, ','.join(aliases))

	# add this new player to all of the playergroups
	for g in map(lambda s: s.strip(), playergroups_string.split(',')):
		try:
			group = filter(lambda grp: equal_name(g, grp.name) or is_alias(g, grp.aliases), rt.playergroups)[0]
			group.add_player(p)
		except IndexError:
			pass

	return None

#--------------------------------------------------
# edit_player_name_rt
#--------------------------------------------------
def edit_player_name_rt(rt, name, aliases):
	player = None
	for alias in aliases:
		matches = filter(lambda p: (equal_name(p.name, alias) or is_alias(alias, p.aliases)), rt.players)
		if len(matches) > 0: player = matches[0]

	if player == None:
		return 'None of the aliases provided match a player'

	# check if name matches any other existing players or aliases
	matches = filter(lambda p: p is not player and (equal_name(p.name, name) or is_alias(name, p.aliases)), rt.players)
	if len(matches) > 0: return 'Name %s already matches a player' % name

	player.name = name

	return None

#--------------------------------------------------
# edit_player(players, name, country, aliases)
#--------------------------------------------------
def edit_player_rt(rt, name, country, aliases, change_country, change_aliases):
	# find the existing player with the matching name
	matches = filter(lambda p: equal_name(p.name, name) or is_alias(name, p.aliases), rt.players)
	if len(matches) == 0: return 'Player %s not found' % name

	player = matches[0]

	if change_aliases:
		# check if any of the aliases matches any existing players or aliases
		for alias in aliases:
			matches = filter(lambda p: p is not player and (equal_name(p.name, alias) or is_alias(alias, p.aliases)), rt.players)
			if len(matches) > 0: return 'Alias %s already matches a player' % alias

		# change the aliases
		player.aliases = aliases

	if change_country:
		# change the country
		player.country = country
	return None


#--------------------------------------------------
# add_players_google_spreadsheet_rt
#--------------------------------------------------
def add_players_google_spreadsheet_rt(rt, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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

	if len(message_list) == 0 or set(message_list[0]) != set(['name', 'country', 'aliases', 'status', 'playergroups', 'errors']):
		print 'Fixing Headers'
		new_message_list = ['status;name;country;aliases;playergroups;errors']
		for msg in message_list[1:]:
			new_message_list.append(';'.join(msg))
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
			aliases = filter(lambda s: s != '', map(lambda s: s.strip(), line[message_list[0].index('aliases')].split(',')))
		except IndexError:
			aliases = []

		try:
			playergroups_string = line[message_list[0].index('playergroups')]
		except IndexError:
			playergroups_string = ''

		if status == 'add':
			err_msg = create_player_rt(rt, name, country, aliases, playergroups_string)
			if err_msg == None:
				new_message_list.append('added;%s;%s;%s;%s' % (name, country, ','.join(aliases), playergroups_string))
				count += 1
			else:
				new_message_list.append('error;%s;%s;%s;%s;%s' % (name, country, ','.join(aliases), playergroups_string, err_msg))
		elif status == 'edit-name':
			err_msg = edit_player_name_rt(rt, name, aliases)
			if err_msg == None:
				new_message_list.append('edited;%s;%s;%s' % (name, country, ','.join(aliases)))
			else:
				new_message_list.append('error;%s;%s;%s;%s' % (name, country, ','.join(aliases), err_msg))
		elif status == 'edit':
			err_msg = edit_player_rt(rt, name, country, aliases, change_country = True, change_aliases = True)
			if err_msg == None:
				new_message_list.append('edited;%s;%s;%s' % (name, country, ','.join(aliases)))
			else:
				new_message_list.append('error;%s;%s;%s;%s' % (name, country, ','.join(aliases), err_msg))
		elif status == 'edit-aliases':
			err_msg = edit_player_rt(rt, name, country, aliases, change_country = False, change_aliases = True)
			if err_msg == None:
				new_message_list.append('edited;%s;%s;%s' % (name, country, ','.join(aliases)))
			else:
				new_message_list.append('error;%s;%s;%s;%s' % (name, country, ','.join(aliases), err_msg))
		elif status == 'edit-country':
			err_msg = edit_player_rt(players, name, country, aliases, change_country = True, change_aliases = False)
			if err_msg == None:
				new_message_list.append('edited;%s;%s;%s' % (name, country, ','.join(aliases)))
			else:
				new_message_list.append('error;%s;%s;%s;%s' % (name, country, ','.join(aliases), err_msg))
		else:
			new_message_list.append(';'.join(line))

	export_batch_text_google_spreadsheet(user, pw, new_message_list, gd_client, curr_key, curr_wksht_id, verbose)
	print "  Added %d players" % (count)

def match_strategies(rt, name, game, map_name):
	return filter(lambda g: (equal_name(name, g.name) or is_alias(name, g.aliases)) and (game == g.map.game) and (equal_name(map_name, g.map.name) or is_alias(map_name, g.map.aliases)), rt.strategies)

def match_gamemodes(rt, name, game, numplayers):
	return filter(lambda g: (equal_name(name, g.name) or is_alias(name, g.aliases)) and (g.game == Gamemode.ANY_GAME or game == g.game) and (g.numplayers == Gamemode.ANY_NUM_PLAYERS or g.numplayers == numplayers), rt.gamemodes)

def match_playergroups(rt, name):
	return filter(lambda g: (equal_name(name, g.name) or is_alias(name, g.aliases)), rt.playergroups)

def add_record1_rt(rt, time, mp, date, cmn, hnt, smk, bmr, tnk, playerlist):
	try:
		P1 = playerlist[0]
	except IndexError:
		P1 = None
	try:
		P2 = playerlist[1]
	except IndexError:
		P2 = None
	try:
		P3 = playerlist[2]
	except IndexError:
		P3 = None
	try:
		P4 = playerlist[3]
	except IndexError:
		P4 = None

	return rt.add_record(time, mp, date, cmn, hnt, smk, bmr, tnk, P1, P2, P3, P4)

def add_record2_rt(rt, time, mp, date, cmn, hnt, smk, bmr, chg, jck, spt, tnk, playerlist):
	try:
		P1 = playerlist[0]
	except IndexError:
		P1 = None
	try:
		P2 = playerlist[1]
	except IndexError:
		P2 = None
	try:
		P3 = playerlist[2]
	except IndexError:
		P3 = None
	try:
		P4 = playerlist[3]
	except IndexError:
		P4 = None

	return rt.add_record_2(time, mp, date, cmn, hnt, smk, bmr, chg, jck, spt, tnk, P1, P2, P3, P4)

#--------------------------------------------------
# create_record_from_strings_rt(players, maps, records, date, time, mapID, plyrsID, common, hunters, smokers, boomers, tanks)
#--------------------------------------------------
def create_record_from_strings_rt(rt, game, date, time, m, plyrs, grps, common, hunters, smokers, boomers, tanks, chargers = '', jockeys = '', spitters = ''):
	"""Creates a new record, checking for any inconsistencies. This function will return None if successful and return an error message if record creation failed. All arguments (except rt) should be strings.
	
	Keyword arguments:
	rt         -- the record tracking object
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
	mp = [m for m in rt.maps if (equal_name(m.name, map_name) or is_alias(map_name, m.aliases)) and m.game == game]
	if mp == []: return 'Map %s not found' % map_name
	else: mp = mp[0]

	# get player names
	playerlist = []
	for name in filter(lambda p: p.strip() != '', plyrs.split(',')):
		player = [p for p in rt.players if equal_name(p.name, name) or is_alias(name, p.aliases)]
		if player == []:
			return 'Player %s not found [%s]' % (name, plyrs)
		else:
			playerlist.append(player[0])

	# find the matching groups
	strategylist = []
	gamemodelist = []
	for name in filter(lambda p: p != '', map(lambda s: s.strip(), grps.split(','))):
		slist1 = match_strategies(rt, name, game, map_name)
		gmlist1 = match_gamemodes(rt, name, game, len(playerlist))
		if slist1 == [] and gmlist1 == []:
			return 'Group %s not found' % name
		else:
			strategylist += slist1
			gamemodelist += gmlist1

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
	if (date, time) in [(r.date, r.time) for r in rt.records]:
		# error, duplicate
		return 'A record with same date and time already exists'

	# also make sure there are no exact duplicate players time, and maps
	if (time, set([p.name for p in playerlist]), mp.name) in [(r.time, set([p.name for p in r.players]), r.map.name) for r in rt.records]:
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
		new_record = add_record1_rt(rt, time, mp, date, common, hunters, smokers, boomers, tanks, playerlist)

	elif game == 2:
		new_record = add_record2_rt(rt, time, mp, date, common, hunters, smokers, boomers, chargers, jockeys, spitters, tanks, playerlist)

	# also add the records to the groups
	for group in strategylist:
		group.add_record(new_record)
	for group in gamemodelist:
		group.add_record(new_record)
	return None

#--------------------------------------------------
# edit_record_time_from_strings(game, players, maps, records, date, time, m, plyrs)
#--------------------------------------------------
def edit_record_time_from_strings_rt(rt, game, date, time, m, plyrs):
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
	mp = [m for m in rt.maps if (equal_name(m.name, map_name) or is_alias(map_name, m.aliases)) and m.game == game]
	if mp == []: return 'Map %s not found' % map_name
	else: mp = mp[0]

	# get player names
	playerlist = []
	for name in filter(lambda p: p.strip() != '', plyrs.split(',')):
		player = [p for p in rt.players if equal_name(p.name, name) or is_alias(name, p.aliases)]
		if player == []:
			return 'Player %s not found [%s]' % (name, plyrs)
		else:
			playerlist.append(player[0])

	# find the record with matching date, map, and players
	matching_records = filter(lambda r: (date, mp, set([p.name for p in playerlist])) == (r.date, r.map, set([p.name for p in r.players])), rt.records)
	if matching_records == []:
		return 'No matching records found with matching players, date %s and map %s' % (date, mp.name)

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

	record.time = time

	return None

#--------------------------------------------------
# edit_record_date_from_strings(game, players, maps, records, date, time, m, plyrs)
#--------------------------------------------------
def edit_record_date_from_strings_rt(rt, game, date, time, m, plyrs):
	game = int(game)
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
	mp = [m for m in rt.maps if (equal_name(m.name, map_name) or is_alias(map_name, m.aliases)) and m.game == game]
	if mp == []: return 'Map %s not found' % map_name
	else: mp = mp[0]

	# get player names
	playerlist = []
	for name in filter(lambda p: p.strip() != '', plyrs.split(',')):
		player = [p for p in rt.players if equal_name(p.name, name) or is_alias(name, p.aliases)]
		if player == []:
			return 'Player %s not found [%s]' % (name, plyrs)
		else:
			playerlist.append(player[0])

	# find the record with matching time, map, and players
	matching_records = filter(lambda r: (time, mp, set([p.name for p in playerlist])) == (r.time, r.map, set([p.name for p in r.players])), rt.records)
	if matching_records == []:
		return 'No matching records found with matching players, time %s and map %s' % (time, mp.name)
	else:
		record = matching_records[0]

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
	record.date = date

#--------------------------------------------------
# add_group_record_from_strings
#--------------------------------------------------
def add_group_record_from_strings_rt(rt, game, date, time, map_name, plyrs, grps):
	"""Adds the record to all of the matching strategies and gamemodes"""

	game = int(game)
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
	matching_records = filter(lambda r: (date, time) == (r.date, r.time), rt.records)
	if matching_records == []:
		return 'No matching records found with date %s and time %s' % (date, format_time(time))

	record = matching_records[0]

	# find the matching map
	mp = [m for m in rt.maps if (equal_name(m.name, map_name) or is_alias(map_name, m.aliases)) and m.game == game]
	if mp == []: return 'Map %s not found' % map_name
	else: mp = mp[0]

	# find the matching groups
	strategylist = []
	gamemodelist = []
	for name in filter(lambda p: p != '', map(lambda s: s.strip(), grps.split(','))):
		slist1 = match_strategies(rt, name, game, map_name)
		gmlist1 = match_gamemodes(rt, name, game, len(record.players))
		if slist1 == [] and gmlist1 == []:
			return 'Group %s not found' % name
		else:
			strategylist += slist1
			gamemodelist += gmlist1

	# also add the records to the groups
	for group in strategylist:
		if record in group.records:
			return 'Record is already in the group %s' % group.name
		else:
			group.add_record(record)
	for group in gamemodelist:
		if record in group.records:
			return 'Record is already in the group %s' % group.name
		else:
			group.add_record(record)

	return None

#--------------------------------------------------
# edit_record_from_strings_rt(players, maps, records, date, time, mapID, plyrsID, common, hunters, smokers, boomers, tanks)
#--------------------------------------------------
def edit_record_from_strings_rt(rt, game, date, time, m, plyrs, common, hunters, smokers, boomers, tanks, chargers = '', jockeys = '', spitters = '', edit_players = True, edit_counts = True, edit_map = True):

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
	matching_records = filter(lambda r: (date, time) == (r.date, r.time), rt.records)
	if matching_records == []:
		return 'No matching records found with date %s and time %s' % (date, format_time(time))

	record = matching_records[0]

	if edit_map == True:
		map_name = m
		# find the matching map
		mp = [m for m in maps if (equal_name(m.name, map_name) or is_alias(map_name, m.aliases)) and m.game == game]
		if mp == []: return 'Map %s not found' % map_name

		record.map = mp[0]

	if edit_players == True:
		# get player names
		playerlist = []
		for name in filter(lambda p: p.strip() != '', plyrs.split(',')):
			player = [p for p in players if equal_name(p.name, name) or is_alias(name, p.aliases)]
			if player == []:
				return 'Player %s not found [%s]' % (name, plyrs)
			else:
				playerlist.append(player[0])
		record.players = playerlist


	if edit_counts == True:
		try:
			record.common  = int(common)
		except (TypeError, ValueError):
			return 'common is invalid number'
		try:
			record.hunters = int(hunters)
		except (TypeError, ValueError):
			return 'hunters is invalid number'
		try:
			record.smokers = int(smokers)
		except (TypeError, ValueError):
			return 'smokers is invalid number'
		try:
			record.boomers = int(boomers)
		except (TypeError, ValueError):
			return 'boomers is invalid number'
		try:
			record.tanks   = int(tanks)
		except (TypeError, ValueError):
			return 'tanks is invalid number'

		if game == 2:
			try:
				record.chargers = int(chargers)
			except (TypeError, ValueError):
				return 'chargers is invalid number'
			try:
				record.jockeys = int(jockeys)
			except (TypeError, ValueError):
				return 'jockeys is invalid number'
			try:
				record.spitters = int(spitters)
			except (TypeError, ValueError):
				return 'spitters is invalid number'
	return None

#--------------------------------------------------
# add_records_google_spreadsheet_rt
#--------------------------------------------------
def add_records_google_spreadsheet_rt(rt, game, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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
			new_message_list.append(';'.join(message))
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
				err_msg = create_record_from_strings_rt(rt, 1, v['date'], v['time'], v['map'], v['players'], v['groups'], v['common'], v['hunters'], v['smokers'], v['boomers'], v['tanks'])
			else:
				err_msg = create_record_from_strings_rt(rt, 2, v['date'], v['time'], v['map'], v['players'], v['groups'], v['common'], v['hunters'], v['smokers'], v['boomers'], v['tanks'], chargers=v['chargers'], jockeys=v['jockeys'], spitters=v['spitters'])
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
				
			err_msg = add_group_record_from_strings_rt \
			( \
				rt, \
				game, \
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
			err_msg = edit_record_date_from_strings_rt \
			( \
				rt, \
				game, \
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
			err_msg = edit_record_time_from_strings_rt \
			( \
				rt, \
				game, \
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
				err_msg = edit_record_from_strings_rt \
				( \
					rt, \
					1, \
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
				err_msg = edit_record_from_strings_rt \
				( \
					rt,
					2, \
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
					v['jockeys'], \
					v['spitters'], \
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
				err_msg = edit_record_from_strings_rt \
				( \
					rt, \
					1, \
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
				err_msg = edit_record_from_strings_rt \
				( \
					rt, \
					2, \
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
				err_msg = edit_record_from_strings_rt \
				( \
					rt, \
					1, \
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
				err_msg = edit_record_from_strings_rt \
				( \
					rt, \
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
				err_msg = edit_record_from_strings_rt \
				( \
					rt, \
					1, \
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
				err_msg = edit_record_from_strings_rt \
				( \
					rt, \
					2, \
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

#--------------------------------------------------
# weekly_achievements
#--------------------------------------------------
def weekly_achievements_rt(rt, players, message_list = [], display_date = datetime.date.today()):
	"""Gets the list of weekly achievements for players."""
	# get the sunday
	start_day = display_date - datetime.timedelta(days=(display_date.weekday()))

	# get the last day, saturday
	end_day = display_date + datetime.timedelta(days=(6 - display_date.weekday()))

	# get all records of the week
	week_records = filter(lambda r: start_day <= r.date <= end_day, rt.records)

	# find the honor groups
	l4d1_20 = filter(lambda g: g.name == 'Left 4 Dead 1 All 20s', rt.honorlists)[0]
	l4d1_30 = filter(lambda g: g.name == 'Left 4 Dead 1 All 30s', rt.honorlists)[0]
	l4d1_40 = filter(lambda g: g.name == 'Left 4 Dead 1 All 40s', rt.honorlists)[0]
	l4d2_20 = filter(lambda g: g.name == 'Left 4 Dead 2 All 20s', rt.honorlists)[0]

	player_records = []

	for player in sorted(players, key = lambda p: p.name.lower()):
		"""
		The threshold for records is:

		over 20 min if in all 20 honor group
		over 30 min if in all 30 honor group
		over 15 min if in no honor groups

		at least 80% of best recorded time
		"""
		if player in l4d1_40.players:
			l4d1_thresh = datetime.timedelta(minutes=40)
		elif player in l4d1_30.players:
			l4d1_thresh = datetime.timedelta(minutes=30)
		elif player in l4d1_20.players:
			l4d1_thresh = datetime.timedelta(minutes=20)
		else:
			l4d1_thresh = datetime.timedelta(minutes=15)

		if player in l4d2_20.players:
			l4d2_thresh = datetime.timedelta(minutes=20)
		else:
			l4d2_thresh = datetime.timedelta(minutes=15)

		# only count the official maps
		for game in [1, 2]:
			for m in (rt.official_maps_1 if game == 1 else rt.official_maps_2):
				# determine the best time on this map
				try:
					best_time = filter(lambda r: r.date <= end_day and player in r.players, rt.find_map_records_sorted(m, -1, sv.Record.TimeFactor))[0]
					best_time_thresh = datetime.timedelta(days = best_time.time.days * 0.9, seconds = best_time.time.seconds * 0.9, microseconds = best_time.time.microseconds * 0.9)
				except IndexError:
					best_time = None
					best_time_thresh = None

				# find the week's records with the matching map and matching player
				try:
					best_rec = sorted(filter(lambda r: r.map == m and player in r.players, week_records), key = lambda r: r.time, reverse = True)[0]

					if ((game == 1 and best_rec.time >= l4d1_thresh) or (game == 2 and best_rec.time >= l4d2_thresh)) and best_rec.time >= best_time_thresh:
						pb = filter(lambda r: r.date <= best_rec.date and player in r.players, rt.find_map_records_sorted(m, -1, sv.Record.TimeFactor))[0]
						player_records.append((player, best_rec, best_rec == pb))
				except IndexError:
					pass
	for (p,r,pb) in player_records:
		message_list.append \
		( \
			'%s achieved %.1f minutes on %s with %s%s' % \
			( \
				p.name, \
				round(r.time.seconds / 60.0 * 2) / 2, \
				r.map.name, \
				', '.join([ player.name for player in sorted(r.players, key = lambda pl: (0 if p == pl else 1, pl.name.lower()))[1:] ]), \
				' (PB!)' if pb else ''
			) \
		) \

	return message_list

#--------------------------------------------------
# export_maps_google_spreadsheet_rt
#--------------------------------------------------
def export_maps_google_spreadsheet_rt(rt, user, pw, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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
	for i,typ in enumerate(['Official', 'Custom']):
		for game in [1, 2]:
			message_list = []
			message_list.append('Left 4 Dead %d %s Maps' % (game, typ))
			if typ == 'Official':
				message_list.append('campaign;name;records')
				message_list += ['%s;%s;%d' % (m.campaign, m.name, len(filter(lambda r: r.map == m, rt.records))) for m in \
					sorted \
					( \
						rt.official_maps_1 if game == 1 else rt.official_maps_2, \
						key = lambda m: (m.order(), m.campaign.lower(), m.name.lower()) \
					)]
			else:
				message_list.append('campaign;name;records;url')
				message_list += ['%s;%s;%d;=HYPERLINK("%s"\\;"link")' % (m.campaign, m.name, len(filter(lambda r: r.map == m, rt.records)), m.url) for m in \
					sorted \
					( \
						rt.custom_maps_1 if game == 1 else rt.custom_maps_2, \
						key = lambda m: (m.order(), m.campaign.lower(), m.name.lower()) \
					)]

			message_lists.append(message_list)
	#print message_lists
	combined = combine_all_message_lists(message_lists, 1)

	export_batch_text_google_spreadsheet(user, pw, combined, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = curr_wksht_id, verbose=verbose)

#--------------------------------------------------
# export_players_google_spreadsheet_rt
#--------------------------------------------------
def export_players_google_spreadsheet_rt(rt, user, pw, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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
	message_list.append('name;country;records;aliases;playergroups')
	message_list += \
	[ \
		'%s;%s;%d;%s;%s' % \
		( \
			m.name, \
			m.country, \
			len(filter(lambda r: m in r.players, rt.records)), \
			', '.join(m.aliases), \
			', '.join(map(lambda g: g.abbreviation if g.abbreviation != '' else g.name, sorted(find_groups_player_rt(rt, m, False), key=lambda g: g.name.lower()))) \
		) \
		for m in sorted \
		( \
			rt.players, \
			key = lambda p: p.name.lower() \
		) \
	]
	message_list.append('')
	message_list.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))

#--------------------------------------------------
# export_records_google_spreadsheet_rt
#--------------------------------------------------
def export_records_google_spreadsheet_rt(rt, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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
	message_list1.append('Left 4 Dead 1;%d games recorded' % len(rt.records_1))
	message_list1.append('date;time;map;p1;p2;p3;p4;common;hunters;smokers;boomers;tanks;trash factor;kill factor;score factor;groups')

	if verbose:
		print '  Populating message lists...'
	message_list1 += \
	[ \
		'%s;%s;%s;%s;%d;%d;%d;%d;%d;%.03f;%.03f;%d;%s' % \
		( \
			r.date, \
			format_time(r.time), \
			r.map.name, \
			';'.join([player.name for player in r.players]) + ';' * (4 - len(r.players)), \
			r.common, \
			r.hunters, \
			r.smokers, \
			r.boomers, \
			r.tanks, \
			sv.Record.TrashFactor(r), \
			sv.Record.KillFactor(r), \
			sv.Record.ScoreFactor(r), \
			', '.join([group.name for group in r.groups]) \
		) \
		for r in rt.records_1 \
	]

	#message_list.append('')
	message_list2 = []
	message_list2.append('Left 4 Dead 2;%d games recorded' % len(rt.records_2))
	message_list2.append('date;time;map;p1;p2;p3;p4;common;hunters;smokers;boomers;chargers;jockeys;spitters;tanks;trash factor;kill factor;score factor;groups')

	message_list2 += \
	[ \
		'%s;%s;%s;%s;%d;%d;%d;%d;%d;%d;%d;%d;%.03f;%.03f;%d;%s' % \
		( \
			r.date, \
			format_time(r.time), \
			r.map.name, \
			';'.join([player.name for player in r.players]) + ';' * (4 - len(r.players)), \
			r.common, \
			r.hunters, \
			r.smokers, \
			r.boomers, \
			r.chargers, \
			r.jockeys, \
			r.spitters, \
			r.tanks, \
			sv.Record.TrashFactor(r), \
			sv.Record.KillFactor(r), \
			sv.Record.ScoreFactor(r), \
			', '.join([group.name for group in r.groups]) \
		) \
		for r in rt.records_2 \
	]

	message_list = combine_message_lists(message_list1, message_list2, 1)
	message_list.append('')
	message_list.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))

	#print '\n'.join(message_list)
	export_batch_text_google_spreadsheet(user, pw, message_list, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = curr_wksht_id, verbose = verbose)

#--------------------------------------------------
# export_stats_google_spreadsheet_rt
#--------------------------------------------------
def export_stats_google_spreadsheet_rt(rt, records, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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
		stats = gen_statistics_rt(rt, filter(lambda r: not r.is_mutation(), records), rt.official_maps if map_type == 'official' else rt.custom_maps, factor = fcn)
		for game in [1, 2]:
			if more_info == '':
				mlist.append('Best %s L4D%d' % (label,game))
			else:
				mlist.append('Best %s L4D%d (%s)' % (label,game,more_info))

			for (m, rlist) in filter(lambda s: s[0].game == game, stats):
				if len(rlist) == 0:
					mlist.append('%s' % m.name)
				else:
					rec = rlist[0]
					if add_stat == True:
						mlist.append \
						( \
							'%s;%s;%s;%s;%s' % \
							( \
								m.name, \
								display_fcn(fcn(rec)), \
								format_time(rec.time), \
								';'.join([p.name for p in rec.players]), \
								'%s%s' % (';' * (4 - len(rec.players)), rec.date) \
							) \
						)
					else:
						mlist.append \
						( \
							'%s;%s;%s;%s' % \
							( \
								m.name, \
								format_time(rec.time), \
								';'.join([p.name for p in rec.players]), \
								'%s%s' % (';' * (4 - len(rec.players)), rec.date) \
							) \
						)
			mlist.append('')

	message_list1 = []
	add_stat_message_list('Time', sv.Record.TimeFactor, mlist = message_list1)
	add_stat_message_list('Gore Factor', sv.Record.GoreFactor, display_fcn = lambda s: '%.03f' % s, add_stat = True, more_info='total SI kills', mlist = message_list1)
	add_stat_message_list('Tank Kills', sv.Record.TankFactor, add_stat = True, mlist = message_list1)
	add_stat_message_list('Common Kills', sv.Record.CommonFactor, add_stat = True, more_info='', mlist = message_list1)

	message_list2 = []
	add_stat_message_list('Trash Factor', sv.Record.TrashFactor, display_fcn = lambda s: '%.03f' % s, add_stat = True, more_info='total SI kills/min', mlist = message_list2)
	add_stat_message_list('Kill Factor', sv.Record.KillFactor, display_fcn = lambda s: '%.03f' % s, add_stat = True, more_info='avg SI kills/min', mlist = message_list2)
	add_stat_message_list('Score Factor', sv.Record.ScoreFactor, display_fcn = lambda s: '%.03f' % s, add_stat = True, more_info='', mlist = message_list2)

	message_list3 = []
	add_stat_message_list('Time', sv.Record.TimeFactor, map_type = 'custom', mlist=message_list3)


	combined = combine_all_message_lists([message_list1, message_list2, message_list3], 1)

	combined.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))
	export_batch_text_google_spreadsheet(user, pw, combined, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=curr_wksht_id, verbose = verbose, remove_extra_text = True)

def export_na_stats_google_spreadsheet_rt(rt, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
	na = ['US', 'Canada', 'Mexico']
	def na_players(plist):
		nap = filter(lambda p: p.country in na, plist)
		nao = filter(lambda p: not p.country in na, plist)
		return len(nap) > len(nao)
	na_records = filter(lambda r: na_players(r.players), rt.records)
	export_stats_google_spreadsheet_rt(rt, records=na_records, user=user, pw=pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=curr_wksht_id, verbose=verbose)

#--------------------------------------------------
# export_stats_top10_google_spreadsheet_rt
#--------------------------------------------------
def export_stats_top10_google_spreadsheet_rt(rt, records, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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

	# get top times
	def add_stat_message_list(label, fcn, display_fcn = lambda s: '%s' % s, more_info = '', add_stat = False, message_list = []):
		stats = gen_statistics_rt(rt, filter(lambda r: not r.is_mutation(), records), rt.official_maps, factor = fcn, n = 10)
		mlists = []
		for (game, mlist) in [(1, []), (2, [])]:
			mlist.append('Best %s L4D%d;%s' % (label,game,more_info))
			for (m, rlist) in filter(lambda s: s[0].game == game, stats):
				mlist.append(m.name)
				for i,rec in enumerate(rlist):
					if add_stat == True:
						mlist.append \
						( \
							'%d:;%s;%s;%s;%s' % \
							( \
								i+1, \
								display_fcn(fcn(rec)), \
								format_time(rec.time), \
								';'.join([p.name for p in rec.players]), \
								rec.date \
							) \
						)
					else:
						mlist.append \
						( \
							'%d:;%s;%s;%s' % \
							( \
								i+1, \
								format_time(rec.time), \
								';'.join([p.name for p in rec.players]), \
								rec.date \
							) \
						)
				for index in range(len(rlist) + 1, 11):
					mlist.append('%d:' % (index))
				mlist.append('')
			mlists.append(mlist)
		message_list += combine_all_message_lists(mlists, 1)
		return message_list

	message_list = []
	add_stat_message_list('Time', sv.Record.TimeFactor, message_list=message_list)
	message_list2 = []
	add_stat_message_list('Score Factor', sv.Record.ScoreFactor, display_fcn = lambda s: '%.03f' % s, add_stat = True, more_info='', message_list=message_list2)
	add_stat_message_list('Trash Factor', sv.Record.TrashFactor, display_fcn = lambda s: '%.03f' % s, add_stat = True, more_info='total SI kills/min', message_list=message_list2)
	combined = combine_message_lists(message_list, message_list2, 1)

	combined.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))

	export_batch_text_google_spreadsheet(user, pw, combined, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=curr_wksht_id, verbose=verbose)

def export_na_stats_top10_google_spreadsheet_rt(rt, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
	na = ['US', 'Canada', 'Mexico']
	def na_players(plist):
		nap = filter(lambda p: p.country in na, plist)
		nao = filter(lambda p: not p.country in na, plist)
		return len(nap) > len(nao)
	na_records = filter(lambda r: na_players(r.players), rt.records)
	export_stats_top10_google_spreadsheet_rt(rt, records=na_records, user=user, pw=pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=curr_wksht_id, verbose=verbose)

#--------------------------------------------------
# export_group_stats_google_spreadsheet_rt
#--------------------------------------------------
def export_group_stats_google_spreadsheet_rt(rt, user = None, pw = None, gd_client = None, curr_key = None, curr_wksht_id = None, verbose = False):
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
		stats = gen_statistics_group_strategy_rt(rt, sorted(rt.official_maps, key = lambda m: (m.order(), m.campaign.lower(), m.name.lower())), \
			fcn)

		for (g, rlist) in sorted(stats, key = lambda (g,r): (g.map.order(), g.map.campaign.lower(), g.map.name.lower(), g.name.lower())):
			if rlist == []:
				mlist.append('%s;%s;' % (g.map.name, g.name))
			else:
				rec = rlist[0]
				if add_stat == True:
					mlist.append \
					( \
						'%s;%s;%s;%s;%s' % \
						( \
							g.map.name, \
							g.name, \
							display_fcn(fcn(rec)), \
							format_time(rec.time), \
							';'.join([p.name for p in sorted(rec.players, key = lambda p: p.name.lower())]) \
						) \
					)
				else:
					mlist.append \
					( \
						'%s;%s;%s;%s' % \
						( \
							g.map.name, \
							g.name, \
							format_time(rec.time), \
							';'.join([p.name for p in sorted(rec.players, key = lambda p: p.name.lower())]) \
						) \
					)
		return mlist

	# get top times
	def add_stat_message_list_gamemode(label, fcn, gamemode, message_list, display_fcn = lambda s: '%s' % s,more_info = '', add_stat = False):
		stats = gen_statistics_rt(rt, find_group_records_rt(rt, gamemode), filter(lambda m: (m.game == gamemode.game) or (gamemode.game == sv.Gamemode.ANY_GAME), sorted(rt.official_maps, key = lambda m: (m.order(), m.campaign.lower(), m.name.lower()))), factor = fcn)
		for game in [1, 2]:
			#message_list.append('Best %s L4D%d;%s' % (label,game,more_info))
			for (m, rlist) in filter(lambda s: s[0].game == game, \
				sorted(stats, key = lambda (m, rlist): (m.order(), m.campaign.lower(), m.name.lower()))):
				if len(rlist) == 0:
					message_list.append('%s' % m.name)
				else:
					rec = rlist[0]
					if add_stat == True:
						message_list.append \
						( \
							'%s;%s;%s;%s' % \
							( \
								m.name, \
								display_fcn(fcn(rec)), \
								format_time(rec.time), \
								';'.join([p.name for p in sorted(rec.players, key = lambda p: p.name.lower())]) \
							) \
						)
					else:
						message_list.append \
						( \
							'%s;%s;%s' % \
							( \
								m.name, \
								format_time(rec.time), \
								';'.join([p.name for p in sorted(rec.players, key = lambda p: p.name.lower())]) \
							) \
						)
			if game == 1:
				message_list.append('')
		return message_list

	lists = []
	add_stat_message_list('Time', sv.time_factor())
	lists.append(message_list)

	gamemodes = ['smashtv', 'solo', 'nomv']
	list1 = []
	for gamemode in filter(lambda g: g.name in gamemodes, rt.gamemodes):
		list1.append('Best Timess mode %s' % gamemode.name)
		list1.append('map;time;player 1;player 2;player 3;player 4')
		add_stat_message_list_gamemode('Time', sv.Record.TimeFactor, gamemode, list1)
		list1.append('')
	lists.append(list1)

	combined = combine_all_message_lists(lists, 1)
	combined.append('last updated:;%s UTC' % (datetime.datetime.utcnow()))
	export_batch_text_google_spreadsheet(user, pw, combined, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=curr_wksht_id, verbose = verbose)

#--------------------------------------------------
# main
#--------------------------------------------------
def main():
	rt = sv.RecordTracker()
	rt.read_players("../players.txt")
	rt.read_maps("../maps.txt")
	rt.read_records("../records.txt")
	rt.read_groups("../groups.txt")
	print '='*20
	print 'Read %d players' % len(rt.players)
	print 'Read %d maps' % len(rt.maps)
	print 'Read %d records' % len(rt.records)
	print 'Read %d strategies' % len(rt.strategies)
	print '     %d gamemodes' % len(rt.gamemodes)
	print '     %d playergroups' % len(rt.playergroups)
	print '     %d honorlists' % len(rt.honorlists)
	print '     %d total groups' % (len(rt.honorlists) + len(rt.playergroups) + len(rt.gamemodes) + len(rt.strategies))
	print '='*20

	if len(rt.records) == 0:
		return

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
		#curr_key = get_key(gd_client, prompt=False, input='0')
		curr_key = get_key_match(gd_client, prompt=False, input='Survival Records Beta 2.0')
		maps_wksht, \
		player_wksht, \
		records_wksht, \
		stats_wksht, \
		top10_wksht, \
		na_wksht, \
		na_top10_wksht, \
		group_stats_wksht, \
		add_player_wksht, \
		add_record1_wksht, \
		add_record2_wksht, \
		group_wksht = \
			get_wksht(gd_client, curr_key, prompt=False, input='0'), \
			get_wksht(gd_client, curr_key, prompt=False, input='1'), \
			get_wksht(gd_client, curr_key, prompt=False, input='2'), \
			get_wksht(gd_client, curr_key, prompt=False, input='3'), \
			get_wksht(gd_client, curr_key, prompt=False, input='4'), \
			get_wksht(gd_client, curr_key, prompt=False, input='5'), \
			get_wksht(gd_client, curr_key, prompt=False, input='6'), \
			get_wksht(gd_client, curr_key, prompt=False, input='7'), \
			get_wksht(gd_client, curr_key, prompt=False, input='8'), \
			get_wksht(gd_client, curr_key, prompt=False, input='9'), \
			get_wksht(gd_client, curr_key, prompt=False, input='10'), \
			get_wksht(gd_client, curr_key, prompt=False, input='11')
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

	testing = False
	if testing:
		export_batch_text_google_spreadsheet_test(user, pw, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = records_wksht)
		return;

	print 'adding new players'
	add_players_google_spreadsheet_rt(rt, user, pw, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = add_player_wksht, verbose = False)
	rt.write_players('../players.txt')

	print 'adding l4d1 records'
	add_records_google_spreadsheet_rt(rt, 1, user, pw, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = add_record1_wksht, verbose = True)
	print 'adding l4d2 records'
	add_records_google_spreadsheet_rt(rt, 2, user, pw, gd_client = gd_client, curr_key = curr_key, curr_wksht_id = add_record2_wksht, verbose = True)

	rt.write_records('../records.txt')
	rt.write_groups('../groups.txt')

	#--------------------------------------------------
	print 'Calculating weekly achievements'
	week_file = open('week.txt', 'w')
	mlist = []
	for i, day in enumerate([datetime.date.today() - datetime.timedelta(days = 7 * i) for i in range(3, -1, -1)]):
		na_group = filter(lambda g: g.name == 'North American Survivors', rt.playergroups)[0]
		mlist += ['Week of %s to %s' % (day - datetime.timedelta(days = day.weekday()), day + datetime.timedelta(days = 6-day.weekday()))]
		weekly_achievements_rt(rt, filter(lambda p: p in na_group.players, rt.players), message_list = mlist, display_date = day)

	week_file.write('\n'.join(mlist))
	week_file.close()
	#--------------------------------------------------

	print 'updating maps'
	export_maps_google_spreadsheet_rt(rt, user, pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=maps_wksht, verbose = verbose)

	print 'updating players'
	export_players_google_spreadsheet_rt(rt, user, pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=player_wksht, verbose = verbose)

	print 'updating records'
	export_records_google_spreadsheet_rt(rt, user=user, pw=pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=records_wksht, verbose = verbose)

	print 'updating stats'
	export_stats_google_spreadsheet_rt(rt, rt.records, user=user, pw=pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=stats_wksht, verbose = verbose)

	print 'updating top10'
	export_stats_top10_google_spreadsheet_rt(rt, rt.records, user = user, pw = pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=top10_wksht, verbose = verbose)

	print 'updating na stats'
	export_na_stats_google_spreadsheet_rt(rt, user=user, pw=pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=na_wksht, verbose = verbose)

	print 'updating na top10'
	export_na_stats_top10_google_spreadsheet_rt(rt, user = user, pw = pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=na_top10_wksht, verbose = verbose)

	print 'updating group stats'
	export_group_stats_google_spreadsheet_rt(rt, user=user, pw=pw, gd_client=gd_client, curr_key=curr_key, curr_wksht_id=group_stats_wksht, verbose=verbose)

	print 'updating groups'
	export_groups_google_spreadsheet_rt(rt, user, pw, gd_client, curr_key, group_wksht, verbose = verbose)

if __name__ == '__main__':
  main()
