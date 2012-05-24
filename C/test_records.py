import survival as sv
import datetime as dt
import survival_records_c as svr

def test1():
	"""Tests the Player class"""
	P1 = sv.Player(1, "test", "Canada", "A,B,C")
	assert (P1.id, P1.name, P1.country) == (1, "test", "Canada")

	for i,j in zip(P1.aliases, ["A", "B", "C"]):
		assert i == j

	#print P1.write_out_str()
	assert set(["ID=1", "name=test", "country=Canada", "aliases=A,B,C", "steamid_hash="]) <= set(P1.write_out_str().split(";"))

def test2():
	"""Tests the Map Class"""
	m = sv.Map(1, "TestCampaign", "TestName", 2, sv.Map.Type.CUSTOM, "", "")
	assert (m.id, m.campaign, m.name, m.game, m.type, m.url) == (1, "TestCampaign", "TestName", 2, sv.Map.Type.CUSTOM, "")

	assert len(m.aliases) == 0

	assert set(["name=TestName", "ID=1", "campaign=TestCampaign", "game=2", "type=custom", "url="]) <= set(m.write_out_str().split(";"))

def test3():
	"""Tests the Record Class"""
	ei = sv.ExtraInfo()
	ei.insert('extras', '1')
	P1 = sv.Player(1, "n1", "c1", "a11,a12,a13", '', ei)
	P2 = sv.Player(2, "n2", "c2", "a21,a22,a23")
	P3 = sv.Player(3, "n3", "c3", "a31,a32,a33")
	P4 = sv.Player(4, "n4", "c4", "a41,a42,a43")

	m = sv.Map(1, "TestCampaign", "TestName", 2, sv.Map.Type.CUSTOM, "", "")

	r = sv.Record(1, dt.timedelta(seconds = 10), m, dt.date(year=2012,month=1,day=2), 1, 2, 3, 4, 5, P1, P2, P3, P4)

	assert r.id == 1
	assert r.time == dt.timedelta(seconds=10)
	assert r.date == dt.date(year=2012,month=1,day=2)
	assert r.common == 1
	assert r.hunters == 2
	assert r.smokers == 3
	assert r.boomers == 4
	assert r.tanks == 5
	assert r.map == m

	str1 = P1.write_out_str()
	assert set(str1.split(';')) == set(['ID=1', 'name=n1', 'country=c1', 'aliases=a11,a12,a13', 'steamid_hash=', 'extras=1'])

	assert type(sv.score_factor()(r)) == float

def test4():
	"""Tests the Strategies"""
	rt = sv.RecordTracker()
	p1 = rt.add_player('P1', 'Canada', '')
	p2 = rt.add_player('P2', 'US', 'Player2')
	p3 = rt.add_player('P3', 'Germany', 'Plyr3,Player3')
	p4 = rt.add_player('P4', 'Sweden', '')

	m1 = rt.add_map('Dead Center', 'Mall Atrium', 2, sv.Map.Type.OFFICIAL, '', 'mall')

	r1 =  rt.add_record_ids(dt.timedelta(minutes=1, seconds=10), m1.id, dt.date.today(), 1, 2, 3, 4, 5, p1.id, p2.id, p3.id, p4.id)

	assert (r1.map, r1.date, r1.time, r1.common, r1.hunters, r1.smokers, r1.boomers, r1.tanks) == (m1, dt.date.today(), dt.timedelta(minutes=1, seconds=10), 1, 2, 3, 4, 5)
	assert set(["ID=%d" % r1.id, "time=00:01:10.00", "common=1", "hunters=2", "smokers=3", "boomers=4", "tanks=5"]) <= set(r1.write_out_str().split(";"))

	rlist = sv.RecordList()
	rlist.insert(r1)
	s1 = rt.add_strategy("strategy_name", "strategy_description", m1, rlist, "")

	assert set(['ID=%d' % s1.id, 'type=strategy', 'map=%d' % m1.id, 'records=%d' % r1.id, 'aliases=']) <= set(s1.write_out_str().split(';'))

def test5():
	"""Tests out Gamemodes"""
	pass

def test6():
	"""Tests out PlayerGroups"""
	rt = sv.RecordTracker()
	p1 = rt.add_player('P1', 'Canada', '')
	p2 = rt.add_player('P2', 'US', 'Player2')
	p3 = rt.add_player('P3', 'Germany', 'Plyr3,Player3')
	p4 = rt.add_player('P4', 'Sweden', '')
	m1 = rt.add_map('Dead Center', 'Mall Atrium', 2, sv.Map.Type.OFFICIAL, '', 'mall')
	r1 =  rt.add_record_ids(dt.timedelta(minutes=1, seconds=10), m1.id, dt.date.today(), 1, 2, 3, 4, 5, p1.id, p2.id, p3.id, p4.id)

	pg1 = rt.add_playergroup('SV', 'Survival Group', 'Survival group description', sv.PlayerList(), 'survivor group', '')

def test7():
	"""test create player and edit_player_name_rt"""
	rt = sv.RecordTracker()
	p1 = rt.add_player('P1', 'Canada', '')
	p2 = rt.add_player('P2', 'US', 'Player2')
	p3 = rt.add_player('P3', 'Germany', 'Plyr3,Player3')
	p4 = rt.add_player('P4', 'Sweden', '')
	m1 = rt.add_map('Dead Center', 'Mall Atrium', 2, sv.Map.Type.OFFICIAL, '', 'mall')
	r1 =  rt.add_record_ids(dt.timedelta(minutes=1, seconds=10), m1.id, dt.date.today(), 1, 2, 3, 4, 5, p1.id, p2.id, p3.id, p4.id)

	pg1 = rt.add_playergroup('SV', 'Survival Group', 'Survival group description', sv.PlayerList(), 'survivor group', '')

	assert svr.create_player_rt(rt, 'P5', 'Canada', ['Players5', '5'], 'Survival group') == None

	assert len(filter(lambda p: svr.equal_name('P5', p.name), rt.players)) != 0
	assert filter(lambda p: svr.equal_name('P6', p.name), rt.players) == []

	assert len(pg1.players) != 0

	assert svr.edit_player_name_rt(rt, 'Player1', ['P1']) == None
	assert filter(lambda p: svr.equal_name('Player1', p.name), rt.players) != []

def test8():
	"""test editing players"""
	rt = sv.RecordTracker()
	p1 = rt.add_player('P1', 'Canada', '')
	p2 = rt.add_player('P2', 'US', 'Player2')
	p3 = rt.add_player('P3', 'Germany', 'Plyr3,Player3')
	p4 = rt.add_player('P4', 'Sweden', '')
	m1 = rt.add_map('Dead Center', 'Mall Atrium', 2, sv.Map.Type.OFFICIAL, '', 'mall')
	r1 =  rt.add_record_ids(dt.timedelta(minutes=1, seconds=10), m1.id, dt.date.today(), 1, 2, 3, 4, 5, p1.id, p2.id, p3.id, p4.id)

	pg1 = rt.add_playergroup('SV', 'Survival Group', 'Survival group description', sv.PlayerList(), 'survivor group', '')

	assert svr.create_player_rt(rt, 'P5', 'Canada', ['Players5', '5'], 'Survival group') == None
	assert svr.edit_player_rt(rt, 'P2', 'Canada', ['Players2', 'PP2'], True, True) == None
	assert 'Players2' in p2.aliases
	assert 'PP2' in p2.aliases
	assert p2.country == 'Canada'

def test9():
	"""Test creation of records"""
	rt = sv.RecordTracker()
	p1 = rt.add_player('P1', 'Canada', '')
	p2 = rt.add_player('P2', 'US', 'Player2')
	p3 = rt.add_player('P3', 'Germany', 'Plyr3,Player3')
	p4 = rt.add_player('P4', 'Sweden', '')

	m1 = rt.add_map('Dead Center', 'Mall Atrium', 2, sv.Map.Type.OFFICIAL, '', 'mall')

	r1 =  rt.add_record_ids(dt.timedelta(minutes=1, seconds=10), m1.id, dt.date.today(), 1, 2, 3, 4, 5, p1.id, p2.id, p3.id, p4.id)

	rlist = sv.RecordList()
	rlist.insert(r1)
	s1 = rt.add_strategy("strategy_name", "strategy_description", m1, rlist, "")

	assert svr.create_record_from_strings_rt(rt, 2, '2012-05-13', '01:02:03.99', 'Mall', 'P1,P2,P3,P4', 'strategy_name', 1, 2, 3, 4, 5, 6, 7, 8) == None
	assert svr.edit_record_time_from_strings_rt(rt, 2, '2012-05-13', '01:00:03.99', 'Mall', 'P1,P2,P3,P4') == None
	assert svr.edit_record_date_from_strings_rt(rt, '2', '2012-05-14', '01:00:03.99', 'Mall', 'P1,P2,P3,P4') == None

	rt.add_strategy("circuit", "running circuit", m1, sv.RecordList(), "")
	rt.add_strategy("mallbridge", "hold the bridge", m1, sv.RecordList(), "")
	svr.create_record_from_strings_rt(rt, 2, '2012-05-14', '00:30:30.30', 'Mall', 'P1,P2,P3,P4', 'circuit', 9, 10, 11, 12, 13, 14, 15, 16)
	svr.create_record_from_strings_rt(rt, 2, '2012-05-15', '00:40:40.40', 'Mall', 'P1,P2,P3,P4', 'circuit', 9, 10, 11, 12, 13, 14, 15, 16)
	#print svr.add_group_record_from_strings_rt(rt, 2, '2012-05-14', '00:30:30.30', 'Mall', 'P1,P2,P3,P4', 'circuit')
	assert svr.add_group_record_from_strings_rt(rt, 2, '2012-05-14', '00:30:30.30', 'Mall', 'P1,P2,P3,P4', 'circuit') != None
	assert svr.add_group_record_from_strings_rt(rt, 2, '2012-05-15', '00:40:40.40', 'Mall', 'P1,P2,P3,P4', 'mallbridge') == None

tests = [test1, test2, test3, test4, test5, test6, test7, test8, test9]

for t in tests:
	t()

rt = sv.RecordTracker()

rt.read_players("../players.txt")
rt.read_maps("../maps.txt")
rt.read_records("../records.txt")
rt.read_groups("../groups.txt")

#print '\n'.join(['%s, %s' % (p.name, p.country) for p in rt.players][:5])
print '%d players' % len(rt.players)
print '%s official maps (%d l4d1, %d l4d2)' % (len(rt.official_maps), len(rt.official_maps_1), len(rt.official_maps_2))

for name, ls in [('strategies', rt.strategies), ('gamemodes', rt.gamemodes), ('playergroups', rt.playergroups)]:
	print '%d %s' % (len(ls), name)
