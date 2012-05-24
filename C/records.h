#ifndef SURVIVAL_RECORDS_H_
#define SURVIVAL_RECORDS_H_

/*==================================================*/
/** \file records.h                                 */
/*
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
#include <sstream>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/date_time/gregorian/gregorian.hpp>

template <typename Type>
class EqualIDPtr : public std::binary_function<Type *, Type *, bool>
{
public:
	bool operator()(const Type * t1, const Type * t2) const
	{
		assert(t1 != NULL && t2 != NULL);
		return t1->id() == t2->id();
	}
};

//==================================================
// ExtraInfo Class
//!
//! \brief Holds an extra (unused) information pertaining to the class
//==================================================
class ExtraInfo
{
private:
	std::map<std::string, std::string> info_;
	std::map<std::string, std::string> & info();

public:
	ExtraInfo();
	ExtraInfo(const ExtraInfo & ei);
	const std::map<std::string, std::string> & info() const;
	void insert(const std::string & key, const std::string & value);
	bool empty() const;
	void clear();
	friend std::ostream & operator<<(std::ostream & stream, const ExtraInfo & ei);
};

//==================================================
// Player Class
//!
//! \brief Keeps track of the players
//==================================================
class Player
{
public:
	typedef std::vector<std::string> NameList;
private:
	unsigned int id_;          //!< The unique id of the player
	std::string name_;         //!< The main name of the player
	std::string country_;      //!< The country that the player resides in
	NameList aliases_;         //!< A list of aliases belonging to the player
	std::string steamid_hash_; //!< A human-readable hash of the steamid
	ExtraInfo extra_;          //!< Any extra information to be added to the player that is not yet supported

	static const std::string INVALID_STEAMID;

public:
	Player(const unsigned int & id, const std::string & name = "", const std::string & country = "", const std::string & aliases = "", const std::string & steamid_hash = "", const ExtraInfo & ei = ExtraInfo());

	class LessPtr;
	class EqualIDPtr;

	void name(const std::string & n);
	void country(const std::string & n);
	const unsigned int & id() const;
	const std::string & name() const;
	const std::string & country() const;
	const std::string & steamid_hash() const;
	const NameList & aliases() const;
	NameList & aliases();
	void aliases(const NameList & l);
	void write_out(std::ostream & o) const;
	void write_out_stdout() const;
	std::string write_out_str() const;
};

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

	unsigned int id_;          //!< The unique id
	std::string campaign_;     //!< name of the campaign
	std::string name_;         //!< main name given to the map
	int game_;                 //!< 1 for l4d1, 2 for l4d2
	Type type_;                //!< Either official or custom
	std::string url_;          //!< The url of where to obtain the map if it is a custom map
	NameList aliases_;         //!< A list of aliases of the map
	ExtraInfo extra_;          //!< Any extra information to be added that is not yet supported

public:
	Map(unsigned int id, const std::string & campaign = "", const std::string & name = "", int game = 1, Type type = CUSTOM, const std::string & url = "", const std::string & aliases = "", const ExtraInfo & ei = ExtraInfo());

	int order() const;
	const unsigned int & id() const;
	const int & game() const;
	const std::string & campaign() const;
	const std::string & name() const;
	const Type & type() const;
	const std::string & url() const;
	const NameList & aliases() const;
	bool find_alias(const std::string & target) const;
	void write_out(std::ostream & o) const;
	std::string write_out_str() const;

	class LessPtr;
	class EqualIDPtr;
	class Equal;
};

inline ExtraInfo::ExtraInfo()
	: info_()
{
	//
}

inline ExtraInfo::ExtraInfo(const ExtraInfo & ei)
	: info_(ei.info_)
{
	//
}

inline std::map<std::string, std::string> & ExtraInfo::info()
{
	return info_;
}

inline const std::map<std::string, std::string> & ExtraInfo::info() const
{
	return info_;
}

inline void ExtraInfo::insert(const std::string & key, const std::string & value)
{
	info().insert( std::pair<std::string, std::string>(key, value) );
}

inline bool ExtraInfo::empty() const
{
	return info().size() == 0;
}

inline void ExtraInfo::clear()
{
	info().clear();
}

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

inline const std::string & Player::steamid_hash() const
{
	return steamid_hash_;
}

inline const Player::NameList & Player::aliases() const { return aliases_; }
inline Player::NameList & Player::aliases() { return aliases_; }

inline void Player::aliases(const Player::NameList & l)
{
	aliases_ = l;
}

inline void Player::write_out_stdout() const
{
	write_out(std::cout);
}

inline std::string Player::write_out_str() const
{
	using std::stringstream;
	stringstream ss(stringstream::in | stringstream::out);
	write_out(ss);
	return ss.str();
}

//==================================================
// class Player::LessPtr
//==================================================
class Player::LessPtr : public std::binary_function<Player *, Player *, bool>
{
public:
	bool operator()(const Player * p1, const Player * p2) const;
};

//==================================================
// class Player::EqualIDPtr
//==================================================
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

inline Map::Map(unsigned int id, const std::string & campaign, const std::string & name, int game, Type type, const std::string & url, const std::string & aliases, const ExtraInfo & ei)
	: id_(id),
	campaign_(campaign),
	name_(name),
	game_(game),
	type_(type),
	url_(url),
	extra_(ei)
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

inline std::string Map::write_out_str() const
{
	using std::stringstream;
	stringstream ss(stringstream::in | stringstream::out);
	write_out(ss);
	return ss.str();
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
	unsigned int id_;          //!< The unique id of the group
	std::string name_;         //!< The primary name of the group
	std::string description_;  //!< Description of the group
	NameList aliases_;         //!< A list of aliases
	ExtraInfo extra_;          //!< Any extra information to be added that is not yet supported

public:
	Group(const unsigned int & id, const std::string & name, const std::string & description, const std::string & aliases = "", const ExtraInfo & ei = ExtraInfo());
	virtual ~Group() = 0;
	void id(const unsigned int & i);
	void description(const std::string & d);
	void name(const std::string & n);
	const unsigned int & id() const;
	const std::string & description() const;
	const std::string & name() const;
	const NameList & aliases() const;
	virtual void write_out(std::ostream & o) const;
	virtual std::string write_out_str() const;

	class LessPtr;
	class LessIDPtr;
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

inline std::string Group::write_out_str() const
{
	using std::stringstream;
	stringstream ss(stringstream::in | stringstream::out);
	write_out(ss);
	return ss.str();
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

class Group::LessIDPtr : public std::binary_function<Group *, Group *, bool>
{
public:
	bool operator()(const Group * g1, const Group * g2) const;
};

inline bool Group::LessIDPtr::operator()(const Group * g1, const Group * g2) const
{
	assert(g1 != NULL && g2 != NULL);
	return g1->id() < g2->id();
}

void time_duration_out(std::ostream & o, const boost::posix_time::time_duration & t);
std::string time_duration_str(const boost::posix_time::time_duration & t);

class Record;
class Factor : public std::unary_function<Record *, float>
{
public:
	virtual float operator()(const Record * r) const = 0;
	virtual ~Factor() = 0;
};

inline Factor::~Factor() { }


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
	ExtraInfo extra_;

public:
	Record(const unsigned int & id, const Time & time = invalid_time, Map * const map = NULL, const Date & date = invalid_date, const int & common = 0, const int & hunters = 0, const int & smokers = 0, const int & boomers = 0, const int & tanks = 0, Player * const p1 = NULL, Player * const p2 = NULL, Player * const p3 = NULL, Player * const p4 = NULL, const ExtraInfo & ei = ExtraInfo());

	Record(const unsigned int & id, const Time & time, Map * const map, const Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & tanks, PlayerList players, const ExtraInfo & ei = ExtraInfo());
	virtual ~Record();

	const unsigned int & id() const;
	const Map * map() const;
	const Date & date() const;
	const Time & time() const;
	const int & common() const;
	const int & hunters() const;
	const int & smokers() const;
	const int & boomers() const;
	const int & tanks() const;

	void id(const unsigned int & i);
	void map(Map * m);
	void date(const Date & d);
	void time(const Time & t);
	void common(const int & i);
	void hunters(const int & i);
	void smokers(const int & i);
	void boomers(const int & i);
	void tanks(const int & i);
	GroupList & groups();
	const GroupList & groups() const;

	void add_group(Group * g);

	void players(const PlayerList & p);
	const PlayerList & players() const;

	virtual void write_out(std::ostream & o) const;
	virtual std::string write_out_str() const;

	virtual bool is_mutation() const;

	class LessPtr;
	class EqualIDPtr;
	class EqualPtr;

	class trash_factor : public Factor
	{
	public:
		trash_factor() { }
		float operator()(const Record * r) const;
	};

	class kill_factor : public Factor
	{
	public:
		kill_factor() { }
		float operator()(const Record * r) const;
	};

	class score_factor : public Factor
	{
	public:
		score_factor() { }
		float operator()(const Record * r) const;
	};

	class gore_factor : public Factor
	{
	public:
		gore_factor() { }
		float operator()(const Record * r) const;
	};

	class time_factor : public Factor
	{
	public:
		time_factor() { }
		float operator()(const Record * r) const { return r->time().total_milliseconds(); }
	};

	class common_factor : public Factor
	{
	public:
		common_factor() { }
		float operator()(const Record * r) const { return r->common(); }
	};

	class tank_factor : public Factor
	{
	public:
		tank_factor() { }
		float operator()(const Record * r) const { return r->tanks(); }
	};

	static const trash_factor  TrashFactor;
	static const kill_factor   KillFactor;
	static const score_factor  ScoreFactor;
	static const gore_factor   GoreFactor;
	static const common_factor CommonFactor;
	static const tank_factor   TankFactor;
	static const time_factor   TimeFactor;
};

//! \brief Get the (constant) list of participating players
inline const Record::PlayerList & Record::players() const { return players_; }
//! \brief Get the list of participating players
inline void Record::players(const PlayerList & p) { players_ = p; }
//! \brief Add a group to the list of records the group belongs to
inline void Record::add_group(Group * g) { groups_.insert(g); }

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

class Record::EqualPtr : public std::binary_function<Record *, Record *, bool>
{
public:
	bool operator()(const Record * r1, const Record * r2) const;
};

inline bool Record::EqualIDPtr::operator()(const Record * r1, const Record * r2) const
{
	assert(r1 != NULL && r2 != NULL);
	return r1->id() == r2->id();
}

inline bool Record::EqualPtr::operator()(const Record * r1, const Record * r2) const
{
	assert(r1 != NULL && r2 != NULL);
	return r1->id() == r2->id() &&
		r1->map() == r2->map() &&
		r1->date() == r2->date() &&
		r1->time() == r2->time() &&
		r1->common() == r2->common() &&
		r1->hunters() == r2->hunters() &&
		r1->smokers() == r2->smokers() &&
		r1->boomers() == r2->boomers() &&
		r1->tanks() == r2->tanks();
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

inline const Record::Date & Record::date() const { return date_; }
inline const Record::Time & Record::time() const { return time_; }
inline const int & Record::tanks() const { return tanks_; }
inline const int & Record::boomers() const { return boomers_; }
inline const int & Record::smokers() const { return smokers_; }
inline const int & Record::hunters() const { return hunters_; }
inline const int & Record::common() const { return common_; }
inline Record::GroupList & Record::groups() { return groups_; }
inline const Record::GroupList & Record::groups() const { return groups_; }

inline void Record::date(const Record::Date & d) { date_ = d; }
inline void Record::time(const Record::Time & t) { time_ = t; }
inline void Record::map(Map * m) { map_ = m; }
inline void Record::tanks(const int & i) { tanks_ = i; }
inline void Record::boomers(const int & i) { boomers_ = i; }
inline void Record::smokers(const int & i) { smokers_ = i; }
inline void Record::hunters(const int & i) { hunters_ = i; }
inline void Record::common(const int & i) { common_ = i; }

inline std::string Record::write_out_str() const
{
	using std::stringstream;
	stringstream ss(stringstream::in | stringstream::out);
	this->write_out(ss);
	return ss.str();
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
	Record2(const unsigned int & id, const Record::Time & time, Map * const map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & chargers, const int & jockeys, const int & spitters, const int & tanks, Player * const p1, Player * const p2 = NULL, Player * const p3 = NULL, Player * const p4 = NULL, const ExtraInfo & ei = ExtraInfo());
	Record2(const unsigned int & id, const Record::Time & time, Map * const map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & chargers, const int & jockeys, const int & spitters, const int & tanks, Record::PlayerList players, const ExtraInfo & ei = ExtraInfo());
	virtual ~Record2();

	void chargers(const int & i);
	const int & chargers() const;
	void jockeys(const int & i);
	const int & jockeys() const;
	void spitters(const int & i);
	const int & spitters() const;

	virtual void write_out(std::ostream & o) const;
};

inline Record2::~Record2()
{
	//
}

inline void Record2::chargers(const int & i) { chargers_ = i; }
inline void Record2::jockeys(const int & i)  { jockeys_  = i; }
inline void Record2::spitters(const int & i) { spitters_ = i; }
inline const int & Record2::chargers() const  { return chargers_; }
inline const int & Record2::jockeys() const   { return jockeys_; }
inline const int & Record2::spitters() const  { return spitters_; }

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
	Strategy(const unsigned int & id, const std::string & name, const std::string & description, Map * map, RecordList records, const std::string & aliases = "", const ExtraInfo & ei = ExtraInfo());
	virtual ~Strategy();

	const Map * map() const;
	void map(Map * m);

	const RecordList & records() const;
	void add_record(Record * r);

	virtual void write_out(std::ostream & o) const;

	class LessPtr;
};

inline Strategy::~Strategy()
{
	//
}

inline void Strategy::add_record(Record * r)
{
	records_.insert(r);
}

inline const Map * Strategy::map() const
{
	return map_;
}

inline void Strategy::map(Map * m)
{
	map_ = m;
}

inline const Strategy::RecordList & Strategy::records() const
{
	return records_;
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
	const static int ANY_GAME = -1;
	static const int ANY_NUM_PLAYERS = -1;

private:
	bool mutation_;
	RecordList records_;
	int game_;
	int numplayers_;

public:
	Gamemode(const unsigned int & id, const std::string & name, const std::string & description, const bool & mutation, int game = ANY_GAME, const std::string & aliases = "", const int & numplayers = ANY_NUM_PLAYERS, const ExtraInfo & ei = ExtraInfo());
	Gamemode(const unsigned int & id, const std::string & name, const std::string & description, const bool & mutation, int game, const RecordList & records, const std::string & aliases = "", const int & numplayers = ANY_NUM_PLAYERS, const ExtraInfo & ei = ExtraInfo());
	virtual ~Gamemode();
	void add_record(Record * r);
	const int & numplayers() const;
	const RecordList & records() const;
	const bool & mutation() const;
	int game() const;

	virtual void write_out(std::ostream & o) const;
};

inline Gamemode::~Gamemode() { }
inline void Gamemode::add_record(Record * r) { records_.insert(r); }
inline const Gamemode::RecordList & Gamemode::records() const { return records_; }
inline const bool & Gamemode::mutation() const { return mutation_; }
inline int Gamemode::game() const { return game_; }
inline const int & Gamemode::numplayers() const { return numplayers_; }

//==================================================
// PlayerGroup class
//==================================================
class PlayerGroup : public Group
{
public:
	typedef std::multiset<Player *, Player::LessPtr> PlayerList;
	typedef std::set<std::string> CountryList;
private:
	std::string abbreviation_;
	PlayerList players_;
	CountryList countries_;
	std::string url_;

public:
	PlayerGroup(const unsigned int & id, const std::string & name, const std::string & description, const PlayerList & players, const std::string & aliases = "", const std::string & countries = "", const std::string & url = "", const ExtraInfo & ei = ExtraInfo());
	PlayerGroup(const unsigned int & id, const std::string & abbreviation, const std::string & name, const std::string & description, const PlayerList & players, const std::string & aliases = "", const std::string & countries = "", const std::string & url = "", const ExtraInfo & ei = ExtraInfo());
	const std::string & abbreviation() const;
	std::string & abbreviation();
	const PlayerList & players() const;
	PlayerList & players();
	const CountryList & countries() const;
	CountryList & countries();
	void add_player(Player * p);
	void url(const std::string & s);
	std::string & url();
	const std::string & url() const;

	virtual void write_out(std::ostream & o) const;
};

inline std::string & PlayerGroup::abbreviation()
{
	return abbreviation_;
}

inline const std::string & PlayerGroup::abbreviation() const
{
	return abbreviation_;
}

inline PlayerGroup::PlayerList & PlayerGroup::players()
{
	return players_;
}

inline const PlayerGroup::PlayerList & PlayerGroup::players() const
{
	return players_;
}

inline PlayerGroup::CountryList & PlayerGroup::countries()
{
	return countries_;
}

inline const PlayerGroup::CountryList & PlayerGroup::countries() const
{
	return countries_;
}

inline void PlayerGroup::add_player(Player * p)
{
	players().insert(p);
}
inline void PlayerGroup::url(const std::string & s) { url_ = s; }
inline std::string & PlayerGroup::url() { return url_; }
inline const std::string & PlayerGroup::url() const { return url_; }

//==================================================
// HonorList class
//==================================================
class HonorList : public Group
{
public:
	typedef std::multiset<Player *, Player::LessPtr> PlayerList;
private:
	PlayerList players_;

public:
	HonorList(const unsigned int & id, const std::string & name, const std::string & description, const PlayerList & players, const std::string & aliases = "", const ExtraInfo & ei = ExtraInfo());
	const PlayerList & players() const;
	PlayerList & players();
	void add_player(Player * p);

	virtual void write_out(std::ostream & o) const;
};

inline const HonorList::PlayerList & HonorList::players() const { return players_; }
inline HonorList::PlayerList & HonorList::players() { return players_; }
inline void HonorList::add_player(Player * p) { players_.insert(p); }

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
	typedef std::multiset< HonorList *, Group::LessPtr > HonorlistList;
	typedef std::multiset< Group *, Group::LessIDPtr > GroupList;
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
	RecordList record_list_1;      //!< holds the list of all records (l4d1)
	RecordList record_list_2;      //!< holds the list of all records (l4d2)
	StrategyList strategy_list;    //!< holds the list of all strategies
	GamemodeList gamemode_list;        //!< holds the list of all game modes
	PlayerGroupList playergroup_list;  //!< holds the list of all player groups modes
	HonorlistList honorlist_list; //!< Holds the master list of all honor lists
	GroupList groups_;            //!< Holds the master list of all groups

	unsigned int next_player_id;
	unsigned int next_map_id;
	unsigned int next_record_id;
	unsigned int next_group_id;

	std::multimap<Map *, Record *> record_map; //!< This is used to lookup all records matching one of the official maps

public:
	RecordTracker();
	~RecordTracker();

	Map *         find_map(unsigned int i) const;
	Record *      find_record(unsigned int i) const;
	Player *      find_player(unsigned int i) const;
	Strategy *    find_strategy(unsigned int i) const;
	Gamemode *    find_gamemode(unsigned int i) const;
	PlayerGroup * find_playergroup(unsigned int i) const;

	const MapList & maps() const;
	RecordList & records();
	RecordList & records_1();
	RecordList & records_2();
	const RecordList & records() const;
	const RecordList & records_1() const;
	const RecordList & records_2() const;
	const MapList & official_maps() const;
	const MapList & official_maps_1() const;
	const MapList & official_maps_2() const;
	const MapList & custom_maps() const;
	const MapList & custom_maps_1() const;
	const MapList & custom_maps_2() const;
	int read_players(const char * filename);
	int read_maps(const char * filename);
	int read_records(const char * filename, bool verbose = false);
	int read_groups(const char * filename, bool verbose = false);
	void write_players(const char * filename);
	void write_maps(const char * filename);
	void write_records(const char * filename);
	void write_groups(const char * filename);
	const StrategyList & strategies() const;
	const PlayerList & players() const;
	const GamemodeList & gamemodes() const;
	const PlayerGroupList & playergroups() const;
	StrategyList & strategies();
	GamemodeList & gamemodes();
	PlayerGroupList & playergroups();
	HonorlistList & honorlists();
	GroupList & groups();

	Player * add_player(const std::string & name, const std::string & country, const std::string & aliases);
	Map * add_map(const std::string & campaign, const std::string & name, int game, Map::Type type, const std::string & url, const std::string & aliases);

	Record * add_record(const Record::Time & time, unsigned int map_id, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & tanks, unsigned int p1_id = 0, unsigned int p2_id = 0, unsigned int p3_id = 0, unsigned int p4_id = 0);

	Record * add_record(const Record::Time & time, Map * map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & tanks, Player * const p1, Player * const p2, Player * const p3, Player * const p4);
	Record2 * add_record_2(const Record::Time & time, Map * map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & chargers, const int & jockeys, const int & spitters, const int & tanks, Player * const p1, Player * const p2, Player * const p3, Player * const p4);
	Strategy * add_strategy(const std::string & name, const std::string & description, Map * m, Strategy::RecordList records, const std::string & aliases);
	Gamemode * add_gamemode(const std::string & name, const std::string & description, const bool & mutation, int game, const Gamemode::RecordList & records, const std::string & aliases, const int & numplayers);
	PlayerGroup * add_playergroup(const std::string & abbreviation, const std::string & name, const std::string & description, const PlayerGroup::PlayerList & players, const std::string & aliases, const std::string & countries);

	std::vector<Record *> find_map_records(Map * m) const;
	std::vector<Record *> find_map_records_sorted(Map * m, int n, const Factor & factor) const;
	std::vector<Record *> find_map_records_filtered(Map * m, int n, const Factor & factor, const std::vector<Record *> & eligible_records) const;

	void export_records(std::vector<std::string> &mlist, const std::string & format) const;
};

inline const RecordTracker::PlayerList & RecordTracker::players() const { return player_list; }
inline const RecordTracker::MapList & RecordTracker::maps() const { return map_list; }
inline const RecordTracker::MapList & RecordTracker::official_maps() const { return official_map_list; }
inline const RecordTracker::MapList & RecordTracker::official_maps_1() const { return official_map_list_1; }
inline const RecordTracker::MapList & RecordTracker::official_maps_2() const { return official_map_list_2; }
inline const RecordTracker::MapList & RecordTracker::custom_maps() const { return custom_map_list; }
inline const RecordTracker::MapList & RecordTracker::custom_maps_1() const { return custom_map_list_1; }
inline const RecordTracker::MapList & RecordTracker::custom_maps_2() const { return custom_map_list_2; }

inline const RecordTracker::RecordList & RecordTracker::records() const
{
	return record_list;
}

inline const RecordTracker::RecordList & RecordTracker::records_1() const
{
	return record_list_1;
}

inline const RecordTracker::RecordList & RecordTracker::records_2() const
{
	return record_list_2;
}

inline RecordTracker::RecordList & RecordTracker::records()
{
	return record_list;
}

inline RecordTracker::RecordList & RecordTracker::records_1()
{
	return record_list_1;
}

inline RecordTracker::RecordList & RecordTracker::records_2()
{
	return record_list_2;
}

inline const RecordTracker::StrategyList & RecordTracker::strategies() const
{
	return strategy_list;
}

inline RecordTracker::StrategyList & RecordTracker::strategies()
{
	return strategy_list;
}

inline const RecordTracker::GamemodeList & RecordTracker::gamemodes() const
{
	return gamemode_list;
}

inline RecordTracker::GamemodeList & RecordTracker::gamemodes()
{
	return gamemode_list;
}

inline RecordTracker::GroupList & RecordTracker::groups()
{
	return groups_;
}

inline const RecordTracker::PlayerGroupList & RecordTracker::playergroups() const { return playergroup_list; }
inline RecordTracker::PlayerGroupList & RecordTracker::playergroups() { return playergroup_list; }
inline RecordTracker::HonorlistList & RecordTracker::honorlists() { return honorlist_list; }

inline Strategy * RecordTracker::find_strategy(unsigned int i) const
{
	Strategy s(i, "", "", NULL, RecordList());
	StrategyList::const_iterator j = std::find_if(strategies().begin(), strategies().end(), std::bind2nd(EqualIDPtr<Strategy>(), &s));

	if (j == strategies().end())
		return NULL;
	else
		return *j;
}

inline Gamemode * RecordTracker::find_gamemode(unsigned int i) const
{
	Gamemode s(i, "", "", false);
	GamemodeList::const_iterator j = std::find_if(gamemodes().begin(), gamemodes().end(), std::bind2nd(EqualIDPtr<Gamemode>(), &s));

	if (j == gamemodes().end())
		return NULL;
	else
		return *j;
}

inline PlayerGroup * RecordTracker::find_playergroup(unsigned int i) const
{
	PlayerGroup s(i, "", "", PlayerList());
	PlayerGroupList::const_iterator j = std::find_if(playergroups().begin(), playergroups().end(), std::bind2nd(EqualIDPtr<PlayerGroup>(), &s));

	if (j == playergroups().end())
		return NULL;
	else
		return *j;
}

//--------------------------------------------------
// find_map_records
//!
//! \brief Finds the records that belong to the given map. \details Note: do not send a NULL pointer to the map parameter
//! \param[in] m The map to find the records for. This cannot be NULL.
//! \return A list of the matching records. It is not sorted in any particular order.
//--------------------------------------------------
inline std::vector<Record *> RecordTracker::find_map_records(Map * m) const
{
	assert(m != NULL);
	Map::Equal me;

	// find all the records that have this map
	typedef std::vector<Record *> List;

	List rlist;

	for
	(
		RecordList::const_iterator i = m->game() == 1 ? records_1().begin() : records_2().begin();
		i != (m->game() == 1 ? records_1().end() : records_2().end());
		++i
	)
	{
		if (me(*((*i)->map()), *m))
		{
			rlist.push_back(*i);
		}
	}

	return rlist;
}

#endif
