#ifndef SURVIVAL_RECORDS_H_
#define SURVIVAL_RECORDS_H_

/*==================================================
 * records.h
 *
 * required - -lboost_date_time
 *==================================================*/

#include <assert.h>
#include <string>
#include <vector>
#include <queue>
#include <set>
#include <map>
#include <stdio.h>
#include "utility.h"
#include <functional>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/date_time/gregorian/gregorian.hpp>

//==================================================
// Player Class
//==================================================
class Player
{
public:
	typedef std::vector<std::string> NameList;
private:
	unsigned int id_;
	std::string name_;
	std::string country_;
	NameList aliases_;

public:
	Player(const unsigned int & id, const std::string & name = "", const std::string & country = "", const std::string & aliases = "");

	class LessPtr;
	class EqualIDPtr;

	void name(const std::string & n);
	void country(const std::string & n);
	const unsigned int & id() const;
	const std::string & name() const;
	const std::string & country() const;
	const NameList & aliases() const;
};

inline void Player::name(const std::string & n)
{
	name_ = n;
}

inline void Player::country(const std::string & n)
{
	country_ = n;
}

inline const unsigned int & Player::id() const
{
	return id_;
}

inline const std::string & Player::name() const
{
	return name_;
}

inline const std::string & Player::country() const
{
	return country_;
}

inline const Player::NameList & Player::aliases() const
{
	return aliases_;
}

class Player::LessPtr : public std::binary_function<Player *, Player *, bool>
{
public:
	bool operator()(const Player * p1, const Player * p2) const;
};

class Player::EqualIDPtr : public std::binary_function<Player *, Player *, bool>
{
public:
	bool operator()(const Player * p1, const Player * p2) const;
};

inline bool Player::EqualIDPtr::operator()(const Player * p1, const Player * p2) const
{
	assert(p1 != NULL && p2 != NULL);
	return p1->id() == p2->id();
}

//==================================================
// Map Class
//!
//! \brief Class that holds map information
//==================================================
class Map
{
public:
	enum Type { OFFICIAL, CUSTOM };
	typedef std::vector<std::string> NameList;

private:
	static std::map<std::string, int> create_campaign_order_map_1();
	static std::map<std::string, int> create_campaign_order_map_2();
	static std::map<std::string, int> create_name_order_map();
	static const std::map<std::string, int> campaign_order_map_1;
	static const std::map<std::string, int> campaign_order_map_2;
	static const std::map<std::string, int> name_order_map;

	unsigned int id_;
	std::string campaign_;
	std::string name_;
	int game_;
	Type type_;
	std::string url_;
	NameList aliases_;
public:
	Map(unsigned int id, const std::string & campaign = "", const std::string & name = "", int game = 1, Type type = CUSTOM, const std::string & url = "", const std::string & aliases = "");

	int order() const;
	const unsigned int & id() const;
	const int & game() const;
	const std::string & campaign() const;
	const std::string & name() const;
	const Type & type() const;
	const std::string & url() const;
	const NameList & aliases() const;
	bool find_alias(const std::string & target) const;

	class LessPtr;
	class EqualIDPtr;
	class Equal;
};

inline std::map<std::string, int> Map::create_campaign_order_map_1()
{
	using std::map;
	using std::string;
	map<string, int> m;
	m["No Mercy"] = 0;
	m["Crash Course"] = 1;
	m["Death Toll"] = 2;
	m["Dead Air"] = 3;
	m["Blood Harvest"] = 4;
	m["Last Stand"] = 5;
	m["Sacrifice"] = 6;
	return m;
}

inline std::map<std::string, int> Map::create_campaign_order_map_2()
{
	using std::map;
	using std::string;
	map<string, int> m;
	m["Dead Center"] = 7;
	m["The Passing"] = 8;
	m["Dark Carnival"] = 9;
	m["Swamp Fever"] = 10;
	m["Hard Rain"] = 11;
	m["The Parish"] = 12;
	m["No Mercy"] = 13;
	m["The Sacrifice"] = 14;
	return m;
}

inline std::map<std::string, int> Map::create_name_order_map()
{
	using std::map;
	using std::string;
	map<string, int> m;
	m["Generator Room"]    = 0;
	m["Gas Station"]       = 1;
	m["Hospital"]          = 2;
	m["Rooftop"]           = 3;
	m["Bridge (CC)"]       = 4;
	m["Truck Depot"]       = 5;
	m["Drains"]            = 6;
	m["Street"]            = 7;
	m["Boathouse"]         = 8;
	m["Crane"]             = 9;
	m["Construction Site"] = 10;
	m["Terminal"]          = 11;
	m["Runway"]            = 12;
	m["Warehouse"]         = 13;
	m["Bridge (BH)"]       = 14;
	m["Farmhouse"]         = 15;
	m["Port (P)"]          = 16;
	m["Motel"]             = 17;
	m["Stadium Gate"]      = 18;
	m["Concert"]           = 19;
	m["Gator Village"]     = 20;
	m["Plantation"]        = 21;
	m["Burger Tank"]       = 22;
	m["Sugar Mill"]        = 23;
	m["Bus Depot"]         = 24;
	m["Generator Room"]    = 25;
	m["Traincar"]          = 26;
	m["Port (S)"]          = 27;
	m["Rooftop"]           = 28;
	return m;
}

inline Map::Map(unsigned int id, const std::string & campaign, const std::string & name, int game, Type type, const std::string & url, const std::string & aliases)
	: id_(id),
	campaign_(campaign),
	name_(name),
	game_(game),
	type_(type),
	url_(url)
{
	StringTokenizer st(aliases, ",");
	std::string temp;

	while (st.hasMoreTokens())
	{
		st.nextToken(temp);
		temp = trim(temp);
		aliases_.push_back(temp);
	}
}

inline const unsigned int & Map::id() const
{
	return id_;
}

inline const std::string & Map::campaign() const
{
	return campaign_;
}

inline const int & Map::game() const
{
	return game_;
}

inline const std::string & Map::name() const
{
	return name_;
}

inline const Map::Type & Map::type() const
{
	return type_;
}

inline const std::string & Map::url() const
{
	return url_;
}

inline const Map::NameList & Map::aliases() const
{
	return aliases_;
}

class Map::LessPtr : public std::binary_function<Map *, Map *, bool>
{
public:
	bool operator()(const Map * m1, const Map * m2) const;
};

class Map::EqualIDPtr : public std::binary_function<Map *, Map *, bool>
{
public:
	bool operator()(const Map * m1, const Map * m2) const;
};

inline bool Map::EqualIDPtr::operator()(const Map * m1, const Map * m2) const
{
	assert(m1 != NULL && m2 != NULL);
	return m1->id() == m2->id();
}

class Map::Equal : public std::binary_function<Map, Map, bool>
{
public:
	bool operator()(const Map & m1, const Map & m2) const;
};

inline bool Map::Equal::operator()(const Map & m1, const Map & m2) const
{
	bool match1 = m1.id() == m2.id() && m1.game() == m2.game() && m1.campaign() == m2.campaign() && m1.type() == m2.type() && m1.url() == m2.url();

	bool match2 = m1.aliases().size() == m2.aliases().size();

	for (Map::NameList::const_iterator i = m1.aliases().begin(); i != m1.aliases().end(); ++i)
	{
		match2 = match2 && m2.find_alias(*i);
	}

	return match1 && match2;
}

//==================================================
// Group Class
//==================================================
class Group
{
public:
	typedef std::vector<std::string> NameList;
private:
	unsigned int id_;
	std::string name_;
	std::string description_;
	NameList aliases_;

public:
	Group(const unsigned int & id, const std::string & name, const std::string & description, const std::string & aliases = "");
	virtual ~Group() = 0;
	void id(const unsigned int & i);
	void description(const std::string & d);
	void name(const std::string & n);
	const unsigned int & id() const;
	const std::string & description() const;
	const std::string & name() const;
	const NameList & aliases() const;

	class LessPtr;
};

inline Group::~Group()
{
	//
}

inline const unsigned int & Group::id() const
{
	return id_;
}

inline const std::string & Group::description() const
{
	return description_;
}

inline const std::string & Group::name() const
{
	return name_;
}

inline const Group::NameList & Group::aliases() const
{
	return aliases_;
}

inline void Group::id(const unsigned int & i)
{
	id_ = i;
}

inline void Group::name(const std::string & d)
{
	name_ = d;
}

inline void Group::description(const std::string & d)
{
	description_ = d;
}

class Group::LessPtr : public std::binary_function<Group *, Group *, bool>
{
public:
	bool operator()(const Group * g1, const Group * g2) const;
};

inline bool Group::LessPtr::operator()(const Group * g1, const Group * g2) const
{
	std::string c1 = g1->name();
	std::string c2 = g2->name();
	transform(c1.begin(), c1.end(), c1.begin(), ::tolower);
	transform(c2.begin(), c2.end(), c2.begin(), ::tolower);

	return c1 < c2;
}

//==================================================
// Record Class
//==================================================
class Record
{
public:
	typedef boost::gregorian::date Date;

	typedef std::multiset<Player *, Player::LessPtr> PlayerList;
	typedef boost::posix_time::time_duration Time;
	typedef std::multiset< Group *, Group::LessPtr > GroupList;

	static const Date invalid_date;
	static const Time invalid_time;

private:
	unsigned int id_;
	Time time_;          //!< The time achieved for the record
	Map * map_;          //!< The map played.
	Date date_;          //!< The date the game was played
	PlayerList players_; //!< The list of players that played
	int common_;         //!< Common kills
	int hunters_;        //!< Hunter kills
	int smokers_;        //!< Smoker kills
	int boomers_;        //!< Boomer kills
	int tanks_;          //!< Tank kills
	GroupList groups_;   //!< List of groups

public:
	Record(const unsigned int & id, const Time & time = invalid_time, Map * const map = NULL, const Date & date = invalid_date, const int & common = 0, const int & hunters = 0, const int & smokers = 0, const int & boomers = 0, const int & tanks = 0, Player * const p1 = NULL, Player * const p2 = NULL, Player * const p3 = NULL, Player * const p4 = NULL);
	Record(const unsigned int & id, const Time & time, Map * const map, const Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & tanks, PlayerList players);
	virtual ~Record();
	void id(const unsigned int & i);
	const unsigned int & id() const;
	const Map * map() const;
	void map(Map * m);
	const Date & date() const;
	const Time & time() const;
	void common(const int & i);
	const int & common() const;
	void hunters(const int & i);
	const int & hunters() const;
	void smokers(const int & i);
	const int & smokers() const;
	void boomers(const int & i);
	const int & boomers() const;
	void tanks(const int & i);
	const int & tanks() const;
	GroupList & groups();

	class LessPtr;
	class EqualIDPtr;
};

class Record::LessPtr : public std::binary_function<Record *, Record *, bool>
{
public:
	bool operator()(const Record * r1, const Record * r2) const;
};

class Record::EqualIDPtr : public std::binary_function<Record *, Record *, bool>
{
public:
	bool operator()(const Record * r1, const Record * r2) const;
};

inline bool Record::EqualIDPtr::operator()(const Record * r1, const Record * r2) const
{
	assert(r1 != NULL && r2 != NULL);
	return r1->id() == r2->id();
}

inline Record::~Record()
{
	//
}

inline const unsigned int & Record::id() const
{
	return id_;
}

inline void Record::id(const unsigned int & i)
{
	id_ = i;
}

inline const Map * Record::map() const
{
	return map_;
}

inline const Record::Date & Record::date() const
{
	return date_;
}

inline const Record::Time & Record::time() const
{
	return time_;
}

inline void Record::map(Map * m)
{
	map_ = m;
}

inline const int & Record::tanks() const
{
	return tanks_;
}

inline void Record::tanks(const int & i)
{
	tanks_ = i;
}

inline const int & Record::boomers() const
{
	return boomers_;
}

inline void Record::boomers(const int & i)
{
	boomers_ = i;
}

inline const int & Record::smokers() const
{
	return smokers_;
}

inline void Record::smokers(const int & i)
{
	smokers_ = i;
}

inline const int & Record::hunters() const
{
	return hunters_;
}

inline void Record::hunters(const int & i)
{
	hunters_ = i;
}

inline const int & Record::common() const
{
	return common_;
}

inline void Record::common(const int & i)
{
	common_ = i;
}

inline Record::GroupList & Record::groups()
{
	return groups_;
}

//==================================================
// Record2 Class
//!
//! \brief A Left 4 Dead 2 record, which includes chargers, spitters, and jockey count.
//==================================================
class Record2 : public Record
{
private:
	int chargers_;
	int jockeys_;
	int spitters_;

public:
	Record2(const unsigned int & id, const Record::Time & time, Map * const map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & chargers, const int & jockeys, const int & spitters, const int & tanks, Player * const p1, Player * const p2 = NULL, Player * const p3 = NULL, Player * const p4 = NULL);
	Record2(const unsigned int & id, const Record::Time & time, Map * const map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & chargers, const int & jockeys, const int & spitters, const int & tanks, Record::PlayerList players);
	virtual ~Record2();

	void chargers(const int & i);
	const int & chargers() const;
	void jockeys(const int & i);
	const int & jockeys() const;
	void spitters(const int & i);
	const int & spitters() const;
};

inline Record2::~Record2()
{
	//
}

//==================================================
// Strategy class
//==================================================
class Strategy : public Group
{
public:
	typedef std::multiset<Record *, Record::LessPtr> RecordList;
private:
	Map * map_;
	RecordList records_;
public:
	Strategy(const unsigned int & id, const std::string & name, const std::string & description, Map * map, RecordList records, const std::string & aliases = "");
	virtual ~Strategy();

	const Map * map() const;
	void map(Map * m);

	class LessPtr;
};

inline Strategy::~Strategy()
{
	//
}

inline const Map * Strategy::map() const
{
	return map_;
}

inline void Strategy::map(Map * m)
{
	map_ = m;
}

class Strategy::LessPtr : public std::binary_function<Strategy *, Strategy *, bool>
{
public:
	bool operator()(const Strategy * s1, const Strategy * s2) const;
};

//==================================================
// Gamemode class
//==================================================
class Gamemode : public Group
{
public:
	typedef std::multiset<Record *, Record::LessPtr> RecordList;
private:
	bool mutation_;
	RecordList records_;

public:
	Gamemode(const unsigned int & id, const std::string & name, const std::string & description, const bool & mutation, const std::string & aliases = "");
	Gamemode(const unsigned int & id, const std::string & name, const std::string & description, const bool & mutation, const RecordList & records, const std::string & aliases = "");
	virtual ~Gamemode();
	void addRecord(Record * r);
	const RecordList & records() const;
	const bool & mutation() const;
};

inline Gamemode::~Gamemode()
{
	//
}

inline void Gamemode::addRecord(Record * r)
{
	records_.insert(r);
}

inline const Gamemode::RecordList & Gamemode::records() const
{
	return records_;
}

inline const bool & Gamemode::mutation() const
{
	return mutation_;
}

//==================================================
// PlayerGroup class
//==================================================
class PlayerGroup : public Group
{
public:
	typedef std::multiset<Player *, Player::LessPtr> PlayerList;
private:
	PlayerList players_;

public:
	PlayerGroup(const unsigned int & id, const std::string & name, const std::string & description, const PlayerList & players, const std::string & aliases = "");
};

//==================================================
// RecordTracker Class
//==================================================
class RecordTracker
{
public:
	typedef std::multiset< Player *, Player::LessPtr > PlayerList;
	typedef std::multiset< Record *, Record::LessPtr > RecordList;
	typedef std::multiset< Strategy *, Strategy::LessPtr > StrategyList;
	typedef std::multiset< Gamemode *, Group::LessPtr > GamemodeList;
	typedef std::multiset< PlayerGroup *, Group::LessPtr > PlayerGroupList;
	typedef std::multiset< Map *, Map::LessPtr > MapList;
private:
	PlayerList player_list;
	MapList map_list;              //!< holds the list of all maps
	MapList official_map_list;     //!< holds the list of official maps only
	MapList official_map_list_1;   //!< holds the list of official maps only
	MapList official_map_list_2;   //!< holds the list of official maps only
	MapList custom_map_list;       //!< holds the list of custom maps only
	MapList custom_map_list_1;     //!< holds the list of custom maps only
	MapList custom_map_list_2;     //!< holds the list of custom maps only
	RecordList record_list;        //!< holds the list of all records
	StrategyList strategy_list;    //!< holds the list of all strategies
	GamemodeList gamemode_list;        //!< holds the list of all game modes
	PlayerGroupList playergroup_list;  //!< holds the list of all player groups modes

	unsigned int next_player_id;
	unsigned int next_map_id;
	unsigned int next_record_id;
	unsigned int next_group_id;

	std::multimap<Map *, Record *> record_map; //!< This is used to lookup all records matching one of the official maps

public:
	RecordTracker();
	~RecordTracker();

	Map * find_map(unsigned int i) const;
	Record * find_record(unsigned int i) const;
	Player * find_player(unsigned int i) const;

	const MapList & maps() const;
	RecordList & records();
	const RecordList & records() const;
	const MapList & official_maps() const;
	const MapList & official_maps_1() const;
	const MapList & official_maps_2() const;
	const MapList & custom_maps() const;
	const MapList & custom_maps_1() const;
	const MapList & custom_maps_2() const;
	void read_players(const char * filename);
	void read_maps(const char * filename);
	void read_records(const char * filename);
	void read_groups(const char * filename);
	void write_players(const char * filename);
	void write_maps(const char * filename);
	void write_records(const char * filename);
	const StrategyList & strategies() const;
	const PlayerList & players() const;
	const GamemodeList & gamemodes() const;
	const PlayerGroupList & playergroups() const;

	bool add_player(const std::string & name, const std::string & country, const std::string & aliases);

	void export_records(std::vector<std::string> &mlist, const std::string & format) const;
};

inline RecordTracker::RecordTracker()
	: player_list(Player::LessPtr()),
	map_list(),
	official_map_list(),
	official_map_list_1(),
	official_map_list_2(),
	custom_map_list(),
	custom_map_list_1(),
	custom_map_list_2(),
	record_list(),
	strategy_list(),
	gamemode_list(),
	playergroup_list(),
	next_player_id(1),
	next_map_id(1),
	next_record_id(1),
	next_group_id(1)
{
	//
}

inline const RecordTracker::PlayerList & RecordTracker::players() const
{
	return player_list;
}

inline const RecordTracker::MapList & RecordTracker::maps() const
{
	return map_list;
}

inline const RecordTracker::MapList & RecordTracker::official_maps() const
{
	return official_map_list;
}

inline const RecordTracker::MapList & RecordTracker::official_maps_1() const
{
	return official_map_list_1;
}

inline const RecordTracker::MapList & RecordTracker::official_maps_2() const
{
	return official_map_list_2;
}

inline const RecordTracker::MapList & RecordTracker::custom_maps() const
{
	return custom_map_list;
}

inline const RecordTracker::MapList & RecordTracker::custom_maps_1() const
{
	return custom_map_list_1;
}

inline const RecordTracker::MapList & RecordTracker::custom_maps_2() const
{
	return custom_map_list_2;
}

inline const RecordTracker::RecordList & RecordTracker::records() const
{
	return record_list;
}

inline RecordTracker::RecordList & RecordTracker::records()
{
	return record_list;
}

inline const RecordTracker::StrategyList & RecordTracker::strategies() const
{
	return strategy_list;
}

inline const RecordTracker::GamemodeList & RecordTracker::gamemodes() const
{
	return gamemode_list;
}

inline const RecordTracker::PlayerGroupList & RecordTracker::playergroups() const
{
	return playergroup_list;
}

#endif
