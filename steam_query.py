#==================================================
# steam_query.py -- Querying steam for xml data to get player and group information
#==================================================
import urllib
import xml.dom.minidom
import steam
import getopt
import sys

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
	            rc.append(node.data)
    return ''.join(rc)

def get_xml_page(groupname):
	url = """http://steamcommunity.com/groups/%s/memberslistxml/?xml=1""" % groupname

	page = urllib.urlopen(url).read()
	print 'got page'
	dom = xml.dom.minidom.parseString(page)

	members = dom.getElementsByTagName('members')[0]
	return [getText(e.childNodes) for e in members.getElementsByTagName('steamID64')]

def get_player_stats(ids):
	plist = []
	for i in ids:
		try:
			user = steam.user.profile(i)
			try:
				n = user.get_persona()
				l = user.get_location()

				if l != None:
					pair = (n, l['country'])
					print '%s %s' % (n, l['country'])
				else:
					pair = (n, None)
					print user.get_persona()
			except KeyError, TypeError:
				pair = (n, None)
				print user.get_persona()
			plist.append(pair)
		except steam.user.ProfileError:
			pass
	return plist

def check_players(plist, players, groups):
	f = open('nas_players.txt', 'w')
	#f.write('\n'.join(['%s' % n if l == None else '%s %s' % (n,l) for n,l in plist]))
	for n,l in plist:
		try:
			if l == None:
				f.write('%s Unknown\n' % n)
			else:
				f.write('%s %s\n' % (n, l))
		except UnicodeEncodeError:
			pass
	f.close()

# parse command line options
try:
	opts, args = getopt.getopt(sys.argv[1:], "", ["key="])
	# Process options
	for o, a in opts:
		if o == "--key":
			key = a
except getopt.error, msg:
	key = raw_input('key: ')

from survival_records import *
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

ids = get_xml_page('NorthAmericanSurvivors')
steam.set_api_key(key)
plist = get_player_stats(ids)
check_players(plist, players, groups)
#print '\n'.join(ids)
