#include "records.h"
#include "utility.h"
#include <sstream>
#include <algorithm>
#include <iterator>
#include <fstream>
#include <cassert>
#include <vector>
using namespace std;

inline bool find_in_string_vector(const vector<string> & list, const string & target)
{
	vector<string>::const_iterator i = find(list.begin(), list.end(), target);

	return i != list.end();
}

//==================================================
// Player class
//==================================================

//--------------------------------------------------
// Player(id, name, country, aliases)
//!
//! \brief Constructs the player with the given id, name, country, and aliases
//--------------------------------------------------
Player::Player(const unsigned int & id, const string & name, const string & country, const string & aliases)
	: id_(id),
	name_(name),
	country_(country),
	aliases_()
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

//==================================================
// Group class
//==================================================
Group::Group(const unsigned int & id, const std::string & name, const std::string & description, const std::string & aliases)
	: id_(id),
	name_(name),
	description_(description),
	aliases_()
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

//==================================================
// Record class
//==================================================

const Record::Date Record::invalid_date = Record::Date(1900, boost::gregorian::Jan, 1);
const Record::Time Record::invalid_time = boost::posix_time::hours(100);

//--------------------------------------------------
// Constructor
//--------------------------------------------------
Record::Record(const unsigned int & id, const Record::Time & time, Map * const map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & tanks, Player * const p1, Player * const p2, Player * const p3, Player * const p4)
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
	groups_()
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

Record::Record(const unsigned int & id, const Time & time, Map * const map, const Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & tanks, PlayerList players)
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
	groups_()
{
	//
}

//==================================================
// Record2 class
//==================================================
Record2::Record2(const unsigned int & id, const Record::Time & time, Map * const map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & chargers, const int & jockeys, const int & spitters, const int & tanks, Player * const p1, Player * const p2, Player * const p3, Player * const p4)
	: Record(id, time, map, date, common, hunters, smokers, boomers, tanks, p1, p2, p3, p4),
	chargers_(chargers),
	jockeys_(jockeys),
	spitters_(spitters)
{
	//
}

Record2::Record2(const unsigned int & id, const Record::Time & time, Map * const map, const Record::Date & date, const int & common, const int & hunters, const int & smokers, const int & boomers, const int & chargers, const int & jockeys, const int & spitters, const int & tanks, Record::PlayerList players)
	: Record(id, time, map, date, common, hunters, smokers, boomers, tanks, players),
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

//==================================================
// Strategy class
//==================================================

Strategy::Strategy(const unsigned int & id, const std::string & name, const std::string & description, Map * map, Strategy::RecordList records, const std::string & aliases)
	: Group(id, name, description, aliases),
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

//==================================================
// class Gamemode
//==================================================

Gamemode::Gamemode(const unsigned int & id, const std::string & name, const std::string & description, const bool & mutation, const std::string & aliases)
	: Group(id, name, description, aliases),
	mutation_(mutation)
{
	//
}

Gamemode::Gamemode(const unsigned int & id, const std::string & name, const std::string & description, const bool & mutation, const Gamemode::RecordList & records, const std::string & aliases)
	: Group(id, name, description, aliases),
	mutation_(mutation),
	records_(records)
{
	//
}

//==================================================
// class PlayerGroup
//==================================================
PlayerGroup::PlayerGroup(const unsigned int & id, const std::string & name, const std::string & description, const PlayerList & players, const std::string & aliases)
	: Group(id, name, description, aliases),
	players_(players)
{
	//
}

//==================================================
// RecordTracker class
//==================================================

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
void RecordTracker::read_players(const char * filename)
{
	ifstream fin(filename, ifstream::in);
	string line;
	string token;

	unsigned int id;
	string name;
	string country;
	string aliases;

	while (fin.good())
	{
		// read in a line from the file
		getline(fin, line);

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
				else if (s1 == "id")
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
			}
		}
		Player * p = new Player(id, name, country, aliases);
		assert(p != NULL);
		player_list.insert(p);
	}

	fin.close();
}

//--------------------------------------------------
// read_maps
//!
//! \brief Reads the player list from a file and populates the PlayerList.
//--------------------------------------------------
void RecordTracker::read_maps(const char * filename)
{
	ifstream fin(filename, ifstream::in);
	string line;
	string token;

	unsigned int id;
	string name;
	string campaign;
	int game;
	string aliases;
	Map::Type type;
	string url;
	int count = 0;

	while (fin.good())
	{
		// read in a line from the file
		getline(fin, line);
		trim(line);

		id = 0;
		name = "";
		campaign = "";
		game = -1;
		aliases = "";
		type = Map::CUSTOM;
		url = "";

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
				else if (s1 == "id")
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
			}
		}

		if (id > 0 && name != "" && campaign != "" && game > 0)
		{
			Map * m = new Map(id, campaign, name, game, type, url, aliases);
			assert(m != NULL);
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
}

//--------------------------------------------------
// read_records
//!
//! \brief Reads the record list from a file and populates the RecordList.
//--------------------------------------------------
void RecordTracker::read_records(const char * filename)
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

	while (fin.good())
	{
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

				if (s1 == "id")
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
			}
		}

		if (id != 0 && date != Record::invalid_date && time != Record::invalid_time && m != NULL && !players.empty() && common != -1 && tanks != -1)
		{
			Record * r = NULL;
			if (m->game() == 1)
			{
				r = new Record(id, time, m, date, common, hunters, smokers, boomers, tanks, players);
			}
			else if (m->game() == 2)
			{
				r = new Record2(id, time, m, date, common, hunters, smokers, boomers, chargers, jockeys, spitters, tanks, players);
			}

			record_map.insert(pair<Map *, Record *>(m, r));

			records().insert(r);
		}
	}

	fin.close();
}

//--------------------------------------------------
// read_records
//!
//! \brief Reads the record list from a file and populates the RecordList.
//--------------------------------------------------
void RecordTracker::read_groups(const char * filename)
{
	ifstream fin(filename, ifstream::in);
	string line;
	string token;

	unsigned int id;
	string name;
	string description;
	string aliases;
	Map * m;
	PlayerGroup::PlayerList players;
	Gamemode::RecordList records;
	bool mutation;

	enum Type {PLAYERGROUP, STRATEGY, GAMEMODE};

	Type type;

	int count = 0;

	while (fin.good())
	{
		// read in a line from the file
		getline(fin, line);
		trim(line);

		id = 0;
		name = "";
		description = "";
		aliases = "";
		m = NULL;
		players.clear();
		records.clear();
		mutation = false;
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

				if (s1 == "id")
				{
					id = atoi(s2.c_str());
				}
				else if (s1 == "name")
				{
					name = s2;
				}
				else if (s1 == "description")
				{
					description = s2;
				}
				else if (s1 == "aliases")
				{
					aliases = s2;
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
					else //if (s2 == "playergroup")
					{
						type = PLAYERGROUP;
					}
				}
			}
		}

		switch (type)
		{
			case GAMEMODE:
			{
				Gamemode * g = new Gamemode(id, name, description, mutation, records, aliases);
				for (Gamemode::RecordList::iterator i = records.begin(); i != records.end(); ++i)
				{
					(*i)->groups().insert(g);
				}
				assert(g != NULL);
				gamemode_list.insert(g);
			} break;

			case STRATEGY:
			{
				Strategy * g = new Strategy(id, name, description, m, records, aliases);
				for (Strategy::RecordList::iterator i = records.begin(); i != records.end(); ++i)
				{
					(*i)->groups().insert(g);
				}
				assert(g != NULL);
				strategy_list.insert(g);
			} break;

			case PLAYERGROUP:
			{
				PlayerGroup * g = new PlayerGroup(id, name, description, players, aliases);
				assert(g != NULL);
				playergroup_list.insert(g);
			} break;
		}

		count++;

		//cout << "count: " << count << " <" << line << ">\n";
	}

	fin.close();
}

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
	FILE * f = fopen(filename, "w");

	for (PlayerList::iterator i = player_list.begin(); i != player_list.end(); ++i)
	{
		assert(*i != NULL);

		if (i != player_list.begin())
			fprintf(f, "\n");

		fprintf(f, "id=%u;name=%s;country=%s;aliases=", (*i)->id(), (*i)->name().c_str(), (*i)->country().c_str());

		for (Player::NameList::const_iterator j = (*i)->aliases().begin(); j != (*i)->aliases().end(); ++j)
		{
			if (j != (*i)->aliases().begin())
				fprintf(f, ",");
			fprintf(f, "%s", j->c_str());
		}
	}


	fclose(f);
}

void RecordTracker::write_maps(const char * filename)
{
	FILE * f = fopen(filename, "w");

	for (MapList::iterator i = map_list.begin(); i != map_list.end(); ++i)
	{
		assert(*i != NULL);

		if (i != map_list.begin())
			fprintf(f, "\n");

		fprintf(f, "id=%u;campaign=%s;name=%s;game=%d;type=%s;url=%s",
			(*i)->id(), (*i)->campaign().c_str(), (*i)->name().c_str(),
			(*i)->game(), (*i)->type() == Map::OFFICIAL ? "official" : "custom",
			(*i)->url().c_str());
	}


	fclose(f);
}

void RecordTracker::write_records(const char * filename)
{
	FILE * f = fopen(filename, "w");

	for (RecordList::iterator i = record_list.begin(); i != record_list.end(); ++i)
	{
	}

	fclose(f);
}

bool RecordTracker::add_player(const string & name, const string & country, const string & aliases)
{
	return false;
}
