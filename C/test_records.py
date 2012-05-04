import survival as sv
import datetime as dt

def test1():
	"""Tests the Player class"""
	P1 = sv.Player(1, "test", "Canada", "A,B,C")
	assert (P1.id, P1.name, P1.country) == (1, "test", "Canada")

	for i,j in zip(P1.aliases, ["A", "B", "C"]):
		assert i == j

def test2():
	"""Tests the Map Class"""
	m = sv.Map(1, "TestCampaign", "TestName", 2, sv.Map.Type.CUSTOM, "", "")
	assert (m.id, m.campaign, m.name, m.game, m.type, m.url) == (1, "TestCampaign", "TestName", 2, sv.Map.Type.CUSTOM, "")

	assert len(m.aliases) == 0

def test3():
	"""Tests the Record Class"""
	P1 = sv.Player(1, "n1", "c1", "a11,a12,a13")
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

tests = [test1, test2, test3]

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
