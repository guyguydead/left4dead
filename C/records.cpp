#include "records.h"
#include "utility.h"
#include <sstream>
#include <algorithm>
#include <iterator>
#include <fstream>
#include <cassert>
#include <vector>
#include <iostream>
#include <cstdio>
using namespace std;

template class EqualIDPtr<Player>;
template class EqualIDPtr<Map>;
template class EqualIDPtr<Record>;
template class EqualIDPtr<Group>;
template class EqualIDPtr<PlayerGroup>;
template class EqualIDPtr<Strategy>;
template class EqualIDPtr<Gamemode>;

inline bool find_in_string_vector(const vector<string> & list, const string & target)
{
	vector<string>::const_iterator i = find(list.begin(), list.end(), target);

	return i != list.end();
}

//==================================================
// ExtraInfo class
//==================================================

ostream & operator<<(ostream & stream, const ExtraInfo & ei)
{
	for (map<string, string>::const_iterator i = ei.info().begin(); i != ei.info().end(); ++i)
	{
		if (i != ei.info().begin())
			stream << ";";
		stream << i->first << "=" << i->second;
	}

	return stream;
}

//==================================================
// Player class
//==================================================
const string Player::INVALID_STEAMID = "";

//--------------------------------------------------
// Player(id, name, country, aliases)
//!
//! \brief Constructs the player with the given id, name, country, and aliases
//--------------------------------------------------
Player::Player(const unsigned int & id, const string & name, const string & country, const string & aliases, const string & steamid_hash, const ExtraInfo & ei)
	: id_(id),
	name_(name),
	country_(country),
	aliases_(),
	steamid_hash_(steamid_hash),
	extra_(ei)
{
	StringTokenizer st(aliases, ",");
	string temp;

	while (st.hasMoreTokens())
	{
		st.nextToken(temp);
		temp = trim(temp);
		aliases_.push_back(temp);
	}
}

bool Player::LessPtr::operator()(const Player * p1, const Player * p2) const
{
	using std::string;
	string name1(p1->name());
	string name2(p2->name());
	transform(name1.begin(), name1.end(), name1.begin(), ::tolower);
	transform(name2.begin(), name2.end(), name2.begin(), ::tolower);

	return name1 < name2;
}

void Player::write_out(ostream & o) const
{
	o << "ID=" << id() << ";name=" << name() << ";country=" << country() << ";aliases=";

	for (NameList::const_iterator i = aliases().begin(); i != aliases().end(); ++i)
	{
		if (i != aliases().begin())
			o << ",";
		o << (*i);
	}

	o << ";steamid_hash=" << steamid_hash();

	if (extra_.empty() == false)
		o << ";" << extra_;
}

//==================================================
// Map class
//==================================================
const std::map<std::string, int> Map::campaign_order_map_1 = Map::create_campaign_order_map_1();
const std::map<std::string, int> Map::campaign_order_map_2 = Map::create_campaign_order_map_2();
const std::map<std::string, int> Map::name_order_map = Map::create_name_order_map();

//--------------------------------------------------
// order
//--------------------------------------------------
int Map::order() const
{
	int campaign_order;
	int name_order;
	map<string, int>::const_iterator i;
	if (game() == 1)
	{
		i = Map::campaign_order_map_1.find(campaign());

		if (i != campaign_order_map_1.end())
			campaign_order = i->second;
		else
			campaign_order = Map::campaign_order_map_1.size() + Map::campaign_order_map_2.size() + (type() == CUSTOM ? 1 : 0);
	}
	else
	{
		i = Map::campaign_order_map_2.find(campaign());

		if (i != campaign_order_map_2.end())
			campaign_order = i->second;
		else
			campaign_order = Map::campaign_order_map_1.size() + Map::campaign_order_map_2.size() + (type() == CUSTOM ? 1 : 0);
	}

	i = Map::name_order_map.find(name());

	if (i != name_order_map.end())
		name_order = i->second;
	else
		name_order = name_order_map.size();

	return campaign_order * 1000 + name_order;
}

bool Map::LessPtr::operator()(const Map * m1, const Map * m2) const
{
	return m1->order() < m2->order();
}

bool Map::find_alias(const std::string & target) const
{
	return find_in_string_vector(aliases(), target);
}

void Map::write_out(ostream & o) const
{
	o << "ID=" << id() << ";name=" << name();
	o << ";campaign=" << campaign();
	o << ";game=" << game() << ";url=" << url() << ";type=" << (type() == Map::OFFICIAL ? "official" : "custom") << ";aliases=";

	for (NameList::const_iterator i = aliases().begin(); i != aliases().end(); ++i)
	{
		if (i != aliases().begin())
			o << ",";
		o << (*i);
	}

	if (extra_.empty() == false)
		o << ";" << extra_;
}

//==================================================
// Group class
//==================================================
Group::Group(const unsigned int & id, const std::string & name, const std::string & description, const std::string & aliases, const ExtraInfo & ei)
	: id_(id),
	name_(name),
	description_(description),
	aliases_(),
	extra_(ei)
{
	StringTokenizer st(aliases, ",");
	string temp;

	while (st.hasMoreTokens())
	{
		st.nextToken(temp);
		temp = trim(temp);
		aliases_.push_back(temp);
	}
}

void time_duration_out(ostream & o, const boost::posix_time::time_duration & t)
{
	using boost::posix_time::time_duration;

	char hours[5];
	char minutes[5];
	char seconds[5];
	char frac[5];
	sprintf(hours,   "%02d", t.hours());
	sprintf(minutes, "%02d", t.minutes());
	sprintf(seconds, "%02d", t.seconds());
	sprintf(frac, "%02ld", (t.total_milliseconds() % 1000 / 10));

	o << hours << ":" << minutes << ":" << seconds << "." << frac;
}

void Group::write_out(ostream & o) const
{
	o << "ID=" << id();
	o << ";description=" << description();
	o << ";name=" << name();

	o << ";aliases=";
	for (NameList::const_iterator i = aliases().begin(); i != aliases().end(); ++i)
	{
		if (i != aliases().begin())
			o << ",";
		o << (*i);
	}

	if (extra_.empty() == false)
		o << ";" << extra_;
}

std::string time_duration_str(const boost::posix_time::time_duration & t)
{
	stringstream ss( stringstream::in | stringstream::out );
	time_duration_out(ss, t);
	return ss.str();
}

//==================================================
// Record class
//==================================================

const Record::Date Record::invalid_date = Record::Date(1900, boost::gregorian::Jan, 1);
const Record::Time Record::invalid_time = boost::posix_time::hours(100);

const Record::trash_factor  Record::TrashFactor;
const Record::kill_factor   Record::KillFactor;
const Record::score_factor  Record::ScoreFactor;
const Record::gore_factor   Record::GoreFactor;
const Record::common_factor Record::CommonFactor;
const Record::tank_factor   Record::TankFactor;
const Record::time_factor   Record::TimeFactor;

//--------------------------------------------------
// Constructor
//--------------------------------------------------
Record::Record(const unsigned int & id, const Record::Time & time, Map * const map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & tanks, Player * const p1, Player * const p2, Player * const p3, Player * const p4, const ExtraInfo & ei)
	: id_(id),
	time_(time),
	map_(map),
	date_(date),
	players_(),
	common_(common),
	hunters_(hunters),
	smokers_(smokers),
	boomers_(boomers),
	tanks_(tanks),
	groups_(),
	extra_(ei)
{
	if (p1 != NULL)
		players_.insert(p1);
	if (p2 != NULL)
		players_.insert(p2);
	if (p3 != NULL)
		players_.insert(p3);
	if (p4 != NULL)
		players_.insert(p4);
}

Record::Record(const unsigned int & id, const Time & time, Map * const map, const Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & tanks, PlayerList players, const ExtraInfo & ei)
	: id_(id),
	time_(time),
	map_(map),
	date_(date),
	players_(players),
	common_(common),
	hunters_(hunters),
	smokers_(smokers),
	boomers_(boomers),
	tanks_(tanks),
	groups_(),
	extra_(ei)
{
	//
}

void Record::write_out(ostream & o) const
{
	assert(map() != NULL);

	o << "ID=" << id() << ";date=" << boost::gregorian::to_iso_extended_string(date());

	o << ";time=";
	time_duration_out(o, time());

	o << ";players=";
	for (Record::PlayerList::iterator i = players().begin(); i != players().end(); ++i)
	{
		assert((*i) != NULL);

		if (i != players().begin())
			o << ",";

		o << (*i)->id();
	}

	o << ";map=" << map()->id();
	o << ";common=" << common();
	o << ";hunters=" << hunters();
	o << ";smokers=" << smokers();
	o << ";boomers=" << boomers();
	o << ";tanks=" << tanks();

	if (extra_.empty() == false)
		o << ";" << extra_;
}

//--------------------------------------------------
// is_mutation
//!
//! \brief Determines whether the record is a mutation by checking the groups it belongs to and seeing whether it belongs to a gamemode that is a mutation.
//--------------------------------------------------
bool Record::is_mutation() const
{
	for (GroupList::const_iterator i = groups().begin(); i != groups().end(); ++i)
	{
		assert(*i != NULL);
		if (dynamic_cast<Gamemode *>(*i) != NULL)
		{
			Gamemode * g = (Gamemode *)(*i);
			if (g->mutation() == true)
				return true;
		}
	}

	return false;
}

//==================================================
// Record2 class
//==================================================
Record2::Record2(const unsigned int & id, const Record::Time & time, Map * const map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & chargers, const int & jockeys, const int & spitters, const int & tanks, Player * const p1, Player * const p2, Player * const p3, Player * const p4, const ExtraInfo & ei)
	: Record(id, time, map, date, common, hunters, smokers, boomers, tanks, p1, p2, p3, p4, ei),
	chargers_(chargers),
	jockeys_(jockeys),
	spitters_(spitters)
{
	//
}

Record2::Record2(const unsigned int & id, const Record::Time & time, Map * const map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & chargers, const int & jockeys, const int & spitters, const int & tanks, Record::PlayerList players, const ExtraInfo & ei)
	: Record(id, time, map, date, common, hunters, smokers, boomers, tanks, players, ei),
	chargers_(chargers),
	jockeys_(jockeys),
	spitters_(spitters)
{
	//
}

bool Record::LessPtr::operator()(const Record * r1, const Record * r2) const
{
	assert(r1 != NULL && r2 != NULL);
	int o1 = r1->map()->order();
	int o2 = r2->map()->order();

	if (o1 != o2)
		return o1 < o2;

	string c1 = r1->map()->campaign();
	string c2 = r2->map()->campaign();
	transform(c1.begin(), c1.end(), c1.begin(), ::tolower);
	transform(c2.begin(), c2.end(), c2.begin(), ::tolower);

	if (c1 != c2)
		return c1 < c2;

	c1 = r1->map()->name();
	c2 = r2->map()->name();
	transform(c1.begin(), c1.end(), c1.begin(), ::tolower);
	transform(c2.begin(), c2.end(), c2.begin(), ::tolower);

	if (c1 != c2)
		return c1 < c2;

	if (r1->date() != r2->date())
		return r1->date() < r2->date();

	return r1->time() < r2->time();
}

void Record2::write_out(ostream & o) const
{
	Record::write_out(o);

	o << ";chargers=" << chargers();
	o << ";jockeys=" << jockeys();
	o << ";spitters=" << spitters();
}

//--------------------------------------------------
// trash factor
//!
//! \brief total kills / minutes
//!
//! \details trash: highest time is cool but what you want is the hightest kill factor which is way better.what you do is add all si killed without the tanks and divide by the minutes and you get a number. in l4d the number should be over 7 and l4d2 the number should be over 6. the best or most fun games are over 9
//!
//! \param[in] r The record to analyze
//! \return The calculated factor for the record, which is a decimal value
//--------------------------------------------------
float Record::trash_factor::operator()(const Record * r) const
{
	if (r->map()->game() == 1)
	{
		float minutes = r->time().total_seconds() / 60.0;
		float kills = (r->hunters() + r->smokers() + r->boomers() + r->tanks());
		return kills / minutes;
	}
	else if (r->map()->game() == 2)
	{
		const Record2 * r2 = (const Record2 *)r;
		float minutes = r2->time().total_seconds() / 60.0;
		float kills = (r2->hunters() + r2->smokers() + r2->boomers() + r2->chargers() + r2->jockeys() + r2->spitters() + r2->tanks());
		return kills / minutes;
	}
	else
	{
		assert(false);
		return -1;
	}
}


//--------------------------------------------------
// kill factor
//!
//! \brief Measures the average SI kills per minute
//!
//! \param[in] r The record to analyze
//! \return The calculated factor for the record, which is a decimal value
//--------------------------------------------------
float Record::kill_factor::operator()(const Record * r) const
{
	if (r->map()->game() == 1)
	{
		float minutes = r->time().total_seconds() / 60.0;
		float kills = (r->hunters() + r->smokers() + r->boomers() + r->tanks()) / 4.0;
		return kills / minutes;
	}
	else if (r->map()->game() == 2)
	{
		const Record2 * r2 = (const Record2 *)r;
		float minutes = r2->time().total_seconds() / 60.0;
		float kills = (r2->hunters() + r2->smokers() + r2->boomers() + r2->chargers() + r2->jockeys() + r2->spitters() + r2->tanks()) / 7.0;
		return kills / minutes;
	}
	else
	{
		assert(false);
		return -1;
	}
}

//--------------------------------------------------
// score_factor
//!
//! \brief Calculates the score of the given record
//!
//! \param[in] r The record to analyze
//! \return The calculated factor for the record, which is a decimal value
//--------------------------------------------------
float Record::score_factor::operator()(const Record * r) const
{
	assert(r != NULL);

	if (r->map()->game() == 1)
	{
		return round(r->time().seconds() + r->time().total_milliseconds() % 1000 / 1e3) + r->common()/2.0 + (r->hunters() + r->smokers() + r->boomers()) * 6.0 + r->tanks() * 25.0;
	}
	else if (r->map()->game() == 2)
	{
		const Record2 * r2 = (const Record2 *)r;
		float si_score = (r2->hunters() + r2->smokers() + r2->boomers() + r2->chargers() + r2->spitters() + r2->jockeys()) * 6.0;
		float si_per_min = round((r2->hunters() + r2->smokers() + r2->boomers() + r2->chargers() + r2->spitters() + r2->jockeys()) / (r2->time().seconds() + r2->time().total_milliseconds() % 1000 / 1e3) * 60, 2);
		float bonus = (si_per_min / 10.0 + 1) * si_score;
		return round(r2->time().seconds() + r2->time().total_milliseconds() % 1000 / 1e3) + round(r2->common() * 0.5) + bonus + r2->tanks() * 25;
	}
	else
	{
		assert(false);
	}
	return -1;
}

//--------------------------------------------------
// gore_factor
//!
//! \brief Calculates the total kills of the given record
//!
//! \param[in] r The record to analyze
//! \return The calculated factor for the record, which is a decimal value
//--------------------------------------------------
float Record::gore_factor::operator()(const Record * r) const
{
	if (r->map()->game() == 1)
	{
		return (r->hunters() + r->smokers() + r->boomers() + r->tanks());
	}
	else if (r->map()->game() == 2)
	{
		const Record2 * r2 = (const Record2 *)r;
		return (r2->hunters() + r2->smokers() + r2->boomers() + r2->chargers() + r2->jockeys() + r2->spitters() + r2->tanks());
	}
	else
	{
		assert(false);
		return -1;
	}
}

//==================================================
// Strategy class
//==================================================
Strategy::Strategy(const unsigned int & id, const std::string & name, const std::string & description, Map * map, Strategy::RecordList records, const std::string & aliases, const ExtraInfo & ei)
	: Group(id, name, description, aliases, ei),
	map_(map),
	records_(records)
{
	//
}

bool Strategy::LessPtr::operator()(const Strategy * g1, const Strategy * g2) const
{
	assert(g1 != NULL && g2 != NULL);

	int o1 = g1->map()->order();
	int o2 = g2->map()->order();

	if (o1 != o2)
		return o1 < o2;

	string c1 = g1->map()->campaign();
	string c2 = g2->map()->campaign();
	transform(c1.begin(), c1.end(), c1.begin(), ::tolower);
	transform(c2.begin(), c2.end(), c2.begin(), ::tolower);

	if (c1 != c2)
		return c1 < c2;

	c1 = g1->map()->name();
	c2 = g2->map()->name();
	transform(c1.begin(), c1.end(), c1.begin(), ::tolower);
	transform(c2.begin(), c2.end(), c2.begin(), ::tolower);

	if (c1 != c2)
		return c1 < c2;

	c1 = g1->name();
	c2 = g2->name();
	transform(c1.begin(), c1.end(), c1.begin(), ::tolower);
	transform(c2.begin(), c2.end(), c2.begin(), ::tolower);

	return c1 < c2;
}

void Strategy::write_out(ostream & o) const
{
	Group::write_out(o);

	o << ";type=strategy";
	o << ";map=" << map()->id();
	o << ";records=";

	for (RecordList::const_iterator i = records().begin(); i != records().end(); ++i)
	{
		if (i != records().begin())
			o << ",";
		o << (*i)->id();
	}
}

//==================================================
// class Gamemode
//==================================================
const int Gamemode::ANY_GAME;
const int Gamemode::ANY_NUM_PLAYERS;

Gamemode::Gamemode(const unsigned int & id, const std::string & name, const std::string & description, const bool & mutation, int game, const std::string & aliases, const int & numplayers, const ExtraInfo & ei)
	: Group(id, name, description, aliases, ei),
	mutation_(mutation),
	records_(),
	game_(),
	numplayers_(numplayers)
{
	//
}

Gamemode::Gamemode(const unsigned int & id, const std::string & name, const std::string & description, const bool & mutation, int game, const Gamemode::RecordList & records, const std::string & aliases, const int & numplayers, const ExtraInfo & ei)
	: Group(id, name, description, aliases, ei),
	mutation_(mutation),
	records_(records),
	game_(game),
	numplayers_(numplayers)
{
	//
}

void Gamemode::write_out(ostream & o) const
{
	Group::write_out(o);

	o << ";type=gamemode";
	o << ";mutation=" << (mutation() ? "yes" : "no");
	o << ";game=" << game();
	o << ";records=";

	for (RecordList::const_iterator i = records().begin(); i != records().end(); ++i)
	{
		if (i != records().begin())
			o << ",";
		o << (*i)->id();
	}

	o << ";numplayers=" << numplayers();
}

//==================================================
// class PlayerGroup
//==================================================
PlayerGroup::PlayerGroup(const unsigned int & id, const string & name, const string & description, const PlayerList & players, const string & aliases, const string & countries, const string & url, const ExtraInfo & ei)
	: Group(id, name, description, aliases, ei),
	abbreviation_(name),
	players_(players),
	countries_(),
	url_(url)
{
	StringTokenizer st(countries, ",");
	string temp;

	while (st.hasMoreTokens())
	{
		st.nextToken(temp);
		temp = trim(temp);
		countries_.insert(temp);
	}
}

PlayerGroup::PlayerGroup(const unsigned int & id, const string & abbreviation, const string & name, const string & description, const PlayerList & players, const string & aliases, const string & countries, const string & url, const ExtraInfo & ei)
	: Group(id, name, description, aliases, ei),
	abbreviation_(abbreviation),
	players_(players),
	countries_(),
	url_(url)
{
	StringTokenizer st(countries, ",");
	string temp;

	while (st.hasMoreTokens())
	{
		st.nextToken(temp);
		temp = trim(temp);
		countries_.insert(temp);
	}
}

void PlayerGroup::write_out(std::ostream & o) const
{
	Group::write_out(o);
	o << ";type=playergroup";
	o << ";abbreviation=" << abbreviation();
	o << ";players=";

	for (PlayerList::const_iterator i = players().begin(); i != players().end(); ++i)
	{
		if (i != players().begin())
			o << ",";

		o << (*i)->id();
	}

	o << ";countries=";
	for (CountryList::const_iterator i = countries().begin(); i != countries().end(); ++i)
	{
		if (i != countries().begin())
			o << ",";

		o << (*i);
	}
}

//==================================================
// class HonorList
//==================================================

//--------------------------------------------------
// Constructor
//--------------------------------------------------
HonorList::HonorList(const unsigned int & id, const std::string & name, const string & description, const PlayerList & players, const std::string & aliases, const ExtraInfo & ei)
	: Group(id, name, description, aliases, ei),
	players_(players)
{
	//
}

//--------------------------------------------------
// write_out
//--------------------------------------------------
void HonorList::write_out(std::ostream & o) const
{
	Group::write_out(o);
	o << ";type=honorlist";
	o << ";players=";

	for (PlayerList::const_iterator i = players().begin(); i != players().end(); ++i)
	{
		if (i != players().begin())
			o << ",";

		o << (*i)->id();
	}
}

//==================================================
// RecordTracker class
//==================================================

//--------------------------------------------------
// Constructor
//--------------------------------------------------
RecordTracker::RecordTracker()
	: player_list(Player::LessPtr()),
	map_list(),
	official_map_list(),
	official_map_list_1(),
	official_map_list_2(),
	custom_map_list(),
	custom_map_list_1(),
	custom_map_list_2(),
	record_list(),
	record_list_1(),
	record_list_2(),
	strategy_list(),
	gamemode_list(),
	playergroup_list(),
	honorlist_list(),
	groups_(),
	next_player_id(1),
	next_map_id(1),
	next_record_id(1),
	next_group_id(1)
{
	//
}

//--------------------------------------------------
// destructor
//!
//! \brief Deletes all records that were created.
//--------------------------------------------------
RecordTracker::~RecordTracker()
{
	for (PlayerList::iterator i = players().begin(); i != players().end(); ++i)
	{
		delete *i;
	}
	for (MapList::iterator i = maps().begin(); i != maps().end(); ++i)
	{
		delete *i;
	}
	for (GroupList::iterator i = groups_.begin(); i != groups_.end(); ++i)
	{
		delete *i;
	}
}

//--------------------------------------------------
// find_map
//--------------------------------------------------
Map * RecordTracker::find_map(unsigned int x) const
{
	Map target(x);
	MapList::iterator i = find_if(maps().begin(), maps().end(), bind2nd(Map::EqualIDPtr(), &target));

	if (i == maps().end())
	{
		return NULL;
	}
	else
	{
		return *i;
	}
}

//--------------------------------------------------
// find_record
//--------------------------------------------------
Record * RecordTracker::find_record(unsigned int x) const
{
	Record target(x);
	RecordList::iterator i = find_if(records().begin(), records().end(), bind2nd(Record::EqualIDPtr(), &target));

	if (i == records().end())
	{
		return NULL;
	}
	else
	{
		return *i;
	}
}

//--------------------------------------------------
// find_player
//--------------------------------------------------
Player * RecordTracker::find_player(unsigned int x) const
{
	Player target(x);
	PlayerList::iterator i = find_if(players().begin(), players().end(), bind2nd(Player::EqualIDPtr(), &target));

	if (i == players().end())
	{
		return NULL;
	}
	else
	{
		return *i;
	}
}

//--------------------------------------------------
// read_players
//!
//! \brief Reads the player list from a file and populates the PlayerList.
//--------------------------------------------------
int RecordTracker::read_players(const char * filename)
{
	ifstream fin(filename, ifstream::in);
	string line;
	string token;

	unsigned int id;
	string name;
	string country;
	string aliases;
	string steamid;
	ExtraInfo ei;

	int count = 0;

	while (fin.good())
	{
		// read in a line from the file
		getline(fin, line);

		id        = 0;
		name      = "";
		country   = "";
		aliases   = "";
		steamid   = "";
		ei.clear();

		// tokenize the string using ";" as a delimiter
		StringTokenizer st(line, ";");

		while (st.hasMoreTokens())
		{
			st.nextToken(token);
			int pos = token.find_first_of("=");

			if (pos != -1)
			{
				string s1 = token.substr(0, pos);
				string s2 = token.substr(pos+1, string::npos);
				transform(s1.begin(), s1.end(), s1.begin(), ::tolower);

				if (s1 == "name")
				{
					name = s2;
				}
				else if (s1 == "id" || s1 == "ID")
				{
					id = atoi(s2.c_str());
				}
				else if (s1 == "country")
				{
					country = s2;
				}
				else if (s1 == "aliases")
				{
					aliases = s2;
				}
				else if (s1 == "steamid_hash")
				{
					steamid = s2;
				}
				else
				{
					ei.insert(trim(s1), trim(s2));
				}
			}
		}
		Player * p = new Player(id, name, country, aliases, steamid, ei);
		assert(p != NULL);

		count++;
		if (id >= next_player_id)
			next_player_id = id + 1;
		player_list.insert(p);
	}

	fin.close();

	return count;
}

//--------------------------------------------------
// read_maps
//!
//! \brief Reads the player list from a file and populates the PlayerList.
//--------------------------------------------------
int RecordTracker::read_maps(const char * filename)
{
	ifstream fin(filename, ifstream::in);
	string line;
	string token;

	unsigned int  id;
	string        name;
	string        campaign;
	int           game;
	string        aliases;
	Map::Type     type;
	string        url;
	ExtraInfo     ei;

	int  count = 0;

	while (fin.good())
	{
		// read in a line from the file
		getline(fin, line);
		trim(line);

		id        = 0;
		name      = "";
		campaign  = "";
		game      = -1;
		aliases   = "";
		type      = Map::CUSTOM;
		url       = "";
		ei.clear();

		// tokenize the string using ";" as a delimiter
		StringTokenizer st(line, ";");

		while (st.hasMoreTokens())
		{
			st.nextToken(token);
			int pos = token.find_first_of("=");

			if (pos != -1)
			{
				string s1 = token.substr(0, pos);
				string s2 = token.substr(pos+1, string::npos);
				transform(s1.begin(), s1.end(), s1.begin(), ::tolower);

				if (s1 == "name")
				{
					name = s2;
				}
				else if (s1 == "game")
				{
					game = atoi(s2.c_str());
				}
				else if (s1 == "id" || s1 == "ID")
				{
					id = atoi(s2.c_str());
				}
				else if (s1 == "campaign")
				{
					campaign = s2;
				}
				else if (s1 == "aliases")
				{
					aliases = s2;
				}
				else if (s1 == "type")
				{
					type = (s2 == "official") ? Map::OFFICIAL : Map::CUSTOM;
				}
				else if (s1 == "url")
				{
					url = s2;
				}
				else
				{
					ei.insert(trim(s1), trim(s2));
				}
			}
		}

		if (id > 0 && name != "" && campaign != "" && game > 0)
		{
			Map * m = new Map(id, campaign, name, game, type, url, aliases, ei);
			assert(m != NULL);

			if (id >= next_map_id)
				next_map_id = id + 1;
			map_list.insert(m);

			if (type == Map::OFFICIAL)
			{
				official_map_list.insert(m);
				if (game == 1)
					official_map_list_1.insert(m);
				else if (game == 2)
					official_map_list_2.insert(m);
			}
			else
			{
				custom_map_list.insert(m);
				if (game == 1)
					custom_map_list_1.insert(m);
				else if (game == 2)
					custom_map_list_2.insert(m);
			}
			count++;
		}
		else
		{
			//
		}
	}

	fin.close();

	return count;
}

//--------------------------------------------------
// read_records
//!
//! \brief Reads the record list from a file and populates the RecordList.
//--------------------------------------------------
int RecordTracker::read_records(const char * filename, bool verbose)
{
	ifstream fin(filename, ifstream::in);
	string line;
	string token;

	unsigned int id;
	Record::Date date;
	Record::Time time;
	Map * m;
	Record::PlayerList players;
	int common;
	int hunters;
	int smokers;
	int boomers;
	int chargers;
	int spitters;
	int jockeys;
	int tanks;
	ExtraInfo ei;

	int count = 0;

	while (fin.good())
	{
		if (verbose)
		{
			cout << "Reading line " << count << "...\n";
		}
		// read in a line from the file
		getline(fin, line);
		trim(line);

		id = 0;
		date = Record::invalid_date;
		time = Record::invalid_time;
		m = NULL;
		players.clear();
		common = -1;
		hunters = -1;
		smokers = -1;
		boomers = -1;
		chargers = -1;
		spitters = -1;
		jockeys = -1;
		tanks = -1;
		ei.clear();

		// tokenize the string using ";" as a delimiter
		StringTokenizer st(line, ";");

		while (st.hasMoreTokens())
		{
			st.nextToken(token);
			int pos = token.find_first_of("=");

			if (pos != -1)
			{
				string s1 = token.substr(0, pos);
				string s2 = token.substr(pos+1, string::npos);
				transform(s1.begin(), s1.end(), s1.begin(), ::tolower);

				if (s1 == "id" || s1 == "ID")
				{
					id = atoi(s2.c_str());
				}
				else if (s1 == "date")
				{
					date = boost::gregorian::from_string(s2);
				}
				else if (s1 == "time")
				{
					time = create_time_duration(s2);
				}
				else if (s1 == "map")
				{
					m = find_map(atoi(s2.c_str()));
				}
				else if (s1 == "players")
				{
					StringTokenizer st2(s2, ",");
					string token2;

					while (st2.hasMoreTokens())
					{
						st2.nextToken(token2);
						trim(token2);
						int player_id = atoi(token2.c_str());

						Player * p = find_player(player_id);

						if (p != NULL)
						{
							players.insert(p);
						}
					}
				}
				else if (s1 == "common")
				{
					common = atoi(s2.c_str());
				}
				else if (s1 == "hunters")
				{
					hunters = atoi(s2.c_str());
				}
				else if (s1 == "smokers")
				{
					smokers = atoi(s2.c_str());
				}
				else if (s1 == "boomers")
				{
					boomers = atoi(s2.c_str());
				}
				else if (s1 == "chargers")
				{
					chargers = atoi(s2.c_str());
				}
				else if (s1 == "jockeys")
				{
					jockeys = atoi(s2.c_str());
				}
				else if (s1 == "spitters")
				{
					spitters = atoi(s2.c_str());
				}
				else if (s1 == "tanks")
				{
					tanks = atoi(s2.c_str());
				}
				else
				{
					ei.insert(trim(s1), trim(s2));
				}
			}
		}

		if (verbose)
		{
			if (id == 0)
				cout << "Error adding " << line << ": id is 0\n";
			if (date == Record::invalid_date)
				cout << "Error adding " << line << ": date is invalid\n";
			if (time == Record::invalid_time)
				cout << "Error adding " << line << ": time is invalid\n";
			if (m == NULL)
				cout << "Error adding " << line << ": map is invalid\n";
			if (players.empty())
				cout << "Error adding " << line << ": no players found\n";
			if (common == -1)
				cout << "Error adding " << line << ": invalid common count\n";
			if (tanks == -1)
				cout << "Error adding " << line << ": invalid tank count\n";
		}
		if (id != 0 && date != Record::invalid_date && time != Record::invalid_time && m != NULL && !players.empty() && common != -1 && tanks != -1)
		{
			Record * r = NULL;
			if (m->game() == 1)
			{
				r = new Record(id, time, m, date, common, hunters, smokers, boomers, tanks, players, ei);
				assert(r != NULL);
				record_list_1.insert(r);
			}
			else if (m->game() == 2)
			{
				r = new Record2(id, time, m, date, common, hunters, smokers, boomers, chargers, jockeys, spitters, tanks, players, ei);
				assert(r != NULL);
				record_list_2.insert(r);
			}

			if (id >= next_record_id)
				next_record_id = id + 1;

			record_map.insert(pair<Map *, Record *>(m, r));

			records().insert(r);
			count++;
		}
	}

	fin.close();
	return count;
}

//--------------------------------------------------
// read_groups
//!
//! \brief Reads the record list from a file and populates the RecordList.
//--------------------------------------------------
int RecordTracker::read_groups(const char * filename, bool verbose)
{
	ifstream fin(filename, ifstream::in);
	string line;
	string token;

	unsigned int id;
	int game;
	int numplayers;
	string abbreviation;
	string name;
	string description;
	string aliases;
	string countries;
	string url;
	Map * m;
	PlayerGroup::PlayerList players;
	Gamemode::RecordList records;
	bool mutation;
	ExtraInfo ei;

	enum Type {PLAYERGROUP, STRATEGY, GAMEMODE, HONORLIST};

	Type type;

	int count = 0;

	while (fin.good())
	{
		// read in a line from the file
		getline(fin, line);
		trim(line);
		if (line == "")
			continue;

		id = 0;
		game = Gamemode::ANY_GAME;
		numplayers = Gamemode::ANY_NUM_PLAYERS;
		abbreviation = "";
		name = "";
		description = "";
		aliases = "";
		countries = "";
		url = "";
		m = NULL;
		players.clear();
		records.clear();
		mutation = false;
		ei.clear();
		type = GAMEMODE;

		// tokenize the string using ";" as a delimiter
		StringTokenizer st(line, ";");

		while (st.hasMoreTokens())
		{
			st.nextToken(token);
			int pos = token.find_first_of("=");

			if (pos != -1)
			{
				string s1 = token.substr(0, pos);
				string s2 = token.substr(pos+1, string::npos);
				transform(s1.begin(), s1.end(), s1.begin(), ::tolower);

				if (s1 == "id" || s1 == "ID")
				{
					id = atoi(s2.c_str());
				}
				else if (s1 == "numplayers")
				{
					numplayers = atoi(s2.c_str());
				}
				else if (s1 == "abbreviation")
				{
					abbreviation = s2;
				}
				else if (s1 == "name")
				{
					name = s2;
				}
				else if (s1 == "url")
				{
					url = s2;
				}
				else if (s1 == "game")
				{
					game = atoi(s2.c_str());
				}
				else if (s1 == "description")
				{
					description = s2;
				}
				else if (s1 == "aliases")
				{
					aliases = s2;
				}
				else if (s1 == "countries")
				{
					countries = s2;
				}
				else if (s1 == "map")
				{
					int map_id = atoi(s2.c_str());
					m = find_map(map_id);
				}
				else if (s1 == "players")
				{
					StringTokenizer st2(s2, ",");
					string token;
					int plyr;
					Player * p;

					while (st2.hasMoreTokens())
					{
						st2.nextToken(token);

						plyr = atoi(token.c_str());
						p = find_player(plyr);

						if (p != NULL)
						{
							players.insert(p);
						}
					}
				}
				else if (s1 == "mutation")
				{
					mutation = !(s2 == "no");
				}
				else if (s1 == "records")
				{
					StringTokenizer st2(s2, ",");
					string token;
					int rec_id;
					Record * r;

					while (st2.hasMoreTokens())
					{
						st2.nextToken(token);
						rec_id = atoi(token.c_str());
						r = find_record(rec_id);
						if (r != NULL)
						{
							records.insert(r);
						}
					}
				}
				else if (s1 == "type")
				{
					if (s2 == "strategy")
					{
						type = STRATEGY;
					}
					else if (s2 == "gamemode")
					{
						type = GAMEMODE;
					}
					else if (s2 == "playergroup")
					{
						type = PLAYERGROUP;
					}
					else //if (s2 == "honorlist")
					{
						type = HONORLIST;
					}
				}
				else
				{
					ei.insert(trim(s1), trim(s2));
				}
			}
		}

		int errors = 0;

		if (id == 0)
		{
			if (verbose)
				cout << "Error for line " << line << " invalid id\n";
			errors++;
		}
		if (name == "")
		{
			if (verbose)
				cout << "Error for line " << line << " invalid name\n";
			errors++;
		}

		if (errors == 0)
		{
			switch (type)
			{
				case GAMEMODE:
				{
					Gamemode * g = new Gamemode(id, name, description, mutation, game, records, aliases, numplayers, ei);
					for (Gamemode::RecordList::iterator i = records.begin(); i != records.end(); ++i)
					{
						(*i)->groups().insert(g);
					}
					// find all records matching the number of players
					if (numplayers != Gamemode::ANY_NUM_PLAYERS)
					{
						for (RecordTracker::RecordList::iterator i = record_list.begin(); i != record_list.end(); ++i)
						{
							if (g->game() == Gamemode::ANY_GAME || g->game() == (*i)->map()->game())
							{
								if ((*i)->players().size() == (unsigned int)numplayers && (*i)->groups().find(g) == (*i)->groups().end())
								{
									(*i)->groups().insert(g);
								}
							}
						}
					}

					assert(g != NULL);
					gamemode_list.insert(g);
					groups_.insert(g);
				} break;

				case STRATEGY:
				{
					Strategy * g = new Strategy(id, name, description, m, records, aliases, ei);
					for (Strategy::RecordList::iterator i = records.begin(); i != records.end(); ++i)
					{
						(*i)->groups().insert(g);
					}
					assert(g != NULL);
					strategy_list.insert(g);
					groups_.insert(g);
				} break;

				case PLAYERGROUP:
				{
					PlayerGroup * g = NULL;

					if (abbreviation == "")
					{
						g = new PlayerGroup(id, name, description, players, aliases, countries, url, ei);
					}
					else
					{
						g = new PlayerGroup(id, abbreviation, name, description, players, aliases, countries, url, ei);
					}

					assert(g != NULL);
					playergroup_list.insert(g);
					groups_.insert(g);
				} break;

				case HONORLIST:
				{
					HonorList * g = NULL;

					g = new HonorList(id, name, description, players, aliases);
					assert(g != NULL);

					honorlist_list.insert(g);
					groups_.insert(g);
				} break;
			}

			count++;
		} // end if

		if (verbose)
			cout << "count: " << count << " <" << line << ">\n";
	}

	fin.close();
	return count;
}

class factor_less : public binary_function<Record *, Record *, bool>
{
private:
	const Factor & factor;

public:
	factor_less(const Factor & factor)
		: factor(factor)
	{
		//
	}

	bool operator()(const Record * r1, const Record * r2) const
	{
		return factor(r1) < factor(r2);
	}
};

//--------------------------------------------------
// find_map_records_sorted
//!
//! \brief Finds the records that belong to the given map. \details Note: do not send a NULL pointer to the map parameter
//! \param[in] m The map to find the records for. This cannot be NULL.
//! \param[in] n The number of records to find
//! \param[in] factor The factor by which the records are sorted. Records are sorted in reverse order by the factor
//! \return A list of the matching records. It is not sorted in any particular order.
//--------------------------------------------------
vector<Record *> RecordTracker::find_map_records_sorted(Map * m, int n, const Factor & factor) const
{
	vector<Record *> rlist(find_map_records(m));
	sort(rlist.rbegin(), rlist.rend(), factor_less(factor));
	//cout << "found " << rlist.size() << " maps\n";
	return vector<Record *>(rlist.begin(), rlist.size() > (unsigned int)n ? rlist.begin() + n : rlist.end());
}

//--------------------------------------------------
// find_map_records_filtered
//!
//! \brief Finds the records that belong to the given map. \details Only maps in the eligible list are considered. Note: do not send a NULL pointer to the map parameter
//! \param[in] m The map to find the records for. This cannot be NULL.
//! \param[in] n The number of records to find
//! \param[in] factor The factor by which the records are sorted. Records are sorted in reverse order by the factor
//! \param[in] eligible_records List of records that are allowed to be considered.
//! \return A list of the matching records. It is not sorted in any particular order.
//--------------------------------------------------
vector<Record *> RecordTracker::find_map_records_filtered(Map * m, int n, const Factor & factor, const vector<Record *> & eligible_records) const
{
	assert(m != NULL);
	Map::Equal me;

	// find all the records that have this map
	typedef std::vector<Record *> List;

	List rlist;

	for (vector<Record *>::const_iterator i = eligible_records.begin(); i != eligible_records.end(); ++i)
	{
		if (me(*((*i)->map()), *m))
		{
			rlist.push_back(*i);
		}
	}

	sort(rlist.rbegin(), rlist.rend(), factor_less(factor));
	//cout << "found " << rlist.size() << " maps\n";
	return vector<Record *>(rlist.begin(), rlist.size() > (unsigned int)n ? rlist.begin() + n : rlist.end());
}

// TODO: this is unfinished
void RecordTracker::export_records(vector<string> & mlist, const string & format) const
{
	StringTokenizer st(format, ";");
	string token;

	while (st.hasMoreTokens())
	{
		st.nextToken(token);
	}
}

void RecordTracker::write_players(const char * filename)
{
	ofstream f(filename);

	if (f.good() == false)
		return;

	for (PlayerList::iterator i = player_list.begin(); i != player_list.end(); ++i)
	{
		assert(*i != NULL);

		if (i != player_list.begin())
			f << "\n";

		(*i)->write_out(f);
		f.flush();
	}


	f.close();
}

void RecordTracker::write_maps(const char * filename)
{
	ofstream f(filename);

	if (f.good() == false)
		return;

	for (MapList::iterator i = map_list.begin(); i != map_list.end(); ++i)
	{
		assert(*i != NULL);

		if (i != map_list.begin())
			f << "\n";

		(*i)->write_out(f);
		f.flush();
	}

	f.close();
}

void RecordTracker::write_records(const char * filename)
{
	ofstream f(filename);

	if (f.good() == false)
		return;

	for (RecordList::iterator i = record_list.begin(); i != record_list.end(); ++i)
	{
		assert(*i != NULL);

		if (i != record_list.begin())
			f << "\n";

		(*i)->write_out(f);
		f.flush();
	}

	f.close();
}

void RecordTracker::write_groups(const char * filename)
{
	ofstream f(filename);

	if (f.good() == false)
		return;

	for (GroupList::const_iterator i = groups().begin(); i != groups().end(); ++i)
	{
		assert(*i != NULL);

		if (i != groups().begin())
			f << "\n";

		(*i)->write_out(f);
		f.flush();
	}

	f.close();
}

Player * RecordTracker::add_player(const string & name, const string & country, const string & aliases)
{
	//unsigned int id = 0;
	Player * new_player = new Player(next_player_id, name, country, aliases);
	assert(new_player != NULL);
	player_list.insert(new_player);
	//id = next_player_id;
	next_player_id++;
	return new_player;
}

Map * RecordTracker::add_map(const std::string & campaign, const std::string & name, int game, Map::Type type, const std::string & url, const std::string & aliases)
{
	//unsigned int id = 0;
	Map * new_map = new Map(next_map_id, campaign, name, game, type, url, aliases);
	//id = next_map_id;
	next_map_id++;
	map_list.insert(new_map);
	if (type == Map::OFFICIAL)
	{
		official_map_list.insert(new_map);
		if (game == 1)
		{
			official_map_list_1.insert(new_map);
		}
		else
		{
			official_map_list_2.insert(new_map);
		}
	}
	else
	{
		custom_map_list.insert(new_map);
		if (game == 1)
		{
			custom_map_list_1.insert(new_map);
		}
		else
		{
			custom_map_list_2.insert(new_map);
		}
	}

	return new_map;
}

Record * RecordTracker::add_record(const Record::Time & time, Map * map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & tanks, Player * const p1, Player * const p2, Player * const p3, Player * const p4)
{
	//unsigned int id = 0;
	Record * r = new Record(next_record_id, time, map, date, common, hunters, smokers, boomers, tanks, p1, p2, p3, p4);
	assert(r != NULL);
	//id = next_record_id;
	next_record_id++;

	records().insert(r);
	records_1().insert(r);
	return r;
}

Record * RecordTracker::add_record(const Record::Time & time, unsigned int map_id, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & tanks, unsigned int p1_id, unsigned int p2_id, unsigned int p3_id, unsigned int p4_id)
{
	Map * m     = find_map(map_id);
	Player * p1 = find_player(p1_id);
	Player * p2 = find_player(p2_id);
	Player * p3 = find_player(p3_id);
	Player * p4 = find_player(p4_id);
	return add_record(time, m, date, common, hunters, smokers, boomers, tanks, p1, p2, p3, p4);
}

Record2 * RecordTracker::add_record_2(const Record::Time & time, Map * map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & chargers, const int & jockeys, const int & spitters, const int & tanks, Player * const p1, Player * const p2, Player * const p3, Player * const p4)
{
	//unsigned int id = 0;
	Record2 * r = new Record2(next_record_id, time, map, date, common, hunters, smokers, boomers, chargers, jockeys, spitters, tanks, p1, p2, p3, p4);
	assert(r != NULL);
	//id = next_record_id;
	next_record_id++;

	records_2().insert(r);
	records().insert(r);
	return r;
}

Strategy * RecordTracker::add_strategy(const std::string & name, const std::string & description, Map * m, Strategy::RecordList records, const std::string & aliases)
{
	//unsigned int id = 0;
	Strategy * s = new Strategy(next_group_id, name, description, m, records, aliases);
	assert(s != NULL);
	//id = next_group_id;
	next_group_id++;
	strategy_list.insert(s);
	return s;
}

Gamemode * RecordTracker::add_gamemode(const std::string & name, const std::string & description, const bool & mutation, int game, const Gamemode::RecordList & records, const std::string & aliases, const int & numplayers)
{
	//unsigned int id = 0;
	Gamemode * g = new Gamemode(next_group_id, name, description, mutation, game, records, aliases, numplayers);
	assert(g != NULL);
	gamemode_list.insert(g);
	//id = next_group_id;
	next_group_id++;
	return g;
}

PlayerGroup * RecordTracker::add_playergroup(const std::string & abbreviation, const std::string & name, const std::string & description, const PlayerGroup::PlayerList & players, const std::string & aliases, const std::string & countries)
{
	//unsigned int id = 0;
	PlayerGroup * p = new PlayerGroup(next_group_id, abbreviation, name, description, players, aliases, countries);
	assert(p != NULL);
	playergroup_list.insert(p);
	//id = next_group_id;
	next_group_id++;
	return p;
}
