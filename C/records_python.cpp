/*==================================================
 * Python Records
 *==================================================*/
#include "records.h"
#include "datetime_python.h"
#include <boost/python.hpp>
#include <string>
#include <vector>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/python/module.hpp>
#include <boost/python/class.hpp>
#include <boost/python/scope.hpp>
#include <boost/python/enum.hpp>
#include <boost/python/def.hpp>
#include <boost/python/implicit.hpp>
#include <boost/python/overloads.hpp>
using namespace std;
using namespace boost::python;
namespace bp = boost::python;
using boost::posix_time::time_duration;
using boost::gregorian::date;

void set_player_aliases(Player & p, bp::list & l);
void set_player_aliases(Player & p, bp::object & o);
void set_record_players(Record & r, bp::list & l);
void set_record_players(Record & r, bp::object & o);

template <class SetType, class Type>
class set_wrapper
{
public:
	static void insert_set(SetType * self, Type i)
	{
		self->insert(i);
	}

	static void wrap(const char * python_name)
	{
		using namespace boost::python;
		class_<SetType>(python_name)
			.def(init<SetType &>())
			.def("insert", &set_wrapper::insert_set)
			.def("__len__", &SetType::size)
			.def("__iter__", range(&SetType::begin, &SetType::end))
		;
	}
};

bool EqualMap(const Map & m1, const Map & m2)
{
	return Map::Equal().operator()(m1, m2);
}

bool EqualRecord(const Record & r1, const Record & r2)
{
	return Record::EqualPtr().operator()(&r1, &r2);
}

void set_player_aliases(Player & p, bp::object & o)
{
	bp::extract<bp::list> l(o);
	
	if (l.check())
	{
		bp::list ls = bp::extract<bp::list>(o);
		static_cast<void (*)(Player &, bp::list &)>(set_player_aliases)(p, ls);
	}
	else
	{
		p.aliases(bp::extract<Player::NameList>(o));
	}
}

void set_player_aliases(Player & p, bp::list & l)
{
	Player::NameList names;
	for (int i = 0; i < bp::len(l); ++i)
	{
		names.push_back(bp::extract<std::string>(l[i]));
	}

	p.aliases(names);
}

void set_record_players(Record & r, bp::object & o)
{
	bp::extract<bp::list> l(o);

	if (l.check())
	{
		bp::list ls = bp::extract<bp::list>(o);
		static_cast<void (*)(Record &, bp::list &)>(set_record_players)(r, ls);
	}
	else
	{
		r.players(bp::extract<Record::PlayerList>(o));
	}
}

void set_record_players(Record & r, bp::list & l)
{
	Record::PlayerList players;
	for (int i = 0; i < bp::len(l); ++i)
	{
		players.insert(bp::extract<Player *>(l[i]));
	}

	r.players(players);
}

std::vector<Record *> find_map_records_filtered(RecordTracker & rt, Map * m, int n, const Factor & factor, bp::list & l)
{
	vector<Record *> records;
	for (int i = 0; i < bp::len(l); ++i)
	{
		records.push_back(bp::extract<Record *>(l[i]));
	}

	return rt.find_map_records_filtered(m, n, factor, records);
}

std::vector<Record *> find_map_records_filtered(RecordTracker & rt, Map * m, int n, const Factor & factor, bp::object & o)
{
	bp::extract<bp::list> l(o);

	if (l.check())
	{
		bp::list ls = bp::extract<bp::list>(o);
		return static_cast<std::vector<Record *> (*)(RecordTracker &, Map *, int, const Factor &, bp::list &)>(find_map_records_filtered)(rt, m, n, factor, ls);
	}
	else
	{
		return rt.find_map_records_filtered(m, n, factor, bp::extract<vector<Record *> >(o));
	}
}

int read_records1(RecordTracker & rt, const char * filename, bool verbose) { return rt.read_records(filename, verbose); }
int read_records2(RecordTracker & rt, const char * filename) { return rt.read_records(filename); }
int read_groups1(RecordTracker & rt, const char * filename, bool verbose) { return rt.read_groups(filename, verbose); }
int read_groups2(RecordTracker & rt, const char * filename) { return rt.read_groups(filename); }


BOOST_PYTHON_MODULE(survival)
{
	bind_datetime();

	def("time_duration_str", time_duration_str);

	class_<vector<string> >("StringList")
		.def(vector_indexing_suite<vector<string> >())
	;
	class_<vector<Record *> >("RecordVector")
		.def(vector_indexing_suite<vector<Record *> >())
	;

	set_wrapper<std::multiset< Player *, Player::LessPtr >, Player *>().wrap("PlayerList");
	set_wrapper<std::multiset< Record *, Record::LessPtr >, Record *>().wrap("RecordList");
	set_wrapper<std::multiset< Group *, Group::LessPtr >, Group *>().wrap("GroupList");
	set_wrapper<std::multiset< Group *, Group::LessIDPtr >, Group *>().wrap("GroupIDList");
	set_wrapper<std::multiset< Strategy *, Strategy::LessPtr >, Strategy *>().wrap("StrategyList");
	set_wrapper<std::multiset< Gamemode *, Group::LessPtr >, Gamemode *>().wrap("GamemodeList");
	set_wrapper<std::multiset< PlayerGroup *, Group::LessPtr >, PlayerGroup *>().wrap("PlayerGroupList");
	set_wrapper<std::set< std::string >, std::string>().wrap("StringSet");
	set_wrapper<std::multiset< HonorList *, Group::LessPtr >, HonorList *>().wrap("HonorlistList");
	set_wrapper<std::multiset< Map *, Map::LessPtr >, Map *>().wrap("MapList");

	class_<ExtraInfo, ExtraInfo*>("ExtraInfo")
		.def("insert", &ExtraInfo::insert)
		.def("empty",  &ExtraInfo::empty)
		.def("clear",  &ExtraInfo::clear)
	;

	class_<Player, Player*>("Player", init<unsigned int const &, string const &, string const &, string const &>(args("id","name","country","aliases")))
		.def(init<unsigned int const &, string const &, string const &, string const &, string const &>(args("id","name","country","aliases","steamid_hash")))
		.def(init<unsigned int const &, string const &, string const &, string const &, string const &, const ExtraInfo &>(args("id","name","country","aliases","steamid_hash","extra_info")))
		.def("write_out_stdout", &Player::write_out_stdout)
		.def("write_out_str", &Player::write_out_str)
		.add_property("name",
			make_function(static_cast<const string &(Player::*)() const>(&Player::name), return_value_policy<copy_const_reference>()),
			static_cast<void (Player::*)(const string &)>(&Player::name)
		)

		.add_property("country",
			make_function(static_cast<const string &(Player::*)() const>(&Player::country), return_value_policy<copy_const_reference>()),
			static_cast<void (Player::*)(const string &)>(&Player::country)
		)

		.add_property("steamid_hash",
			make_function(static_cast<const string &(Player::*)() const>(&Player::steamid_hash), return_value_policy<copy_const_reference>()),
			static_cast<void (Player::*)(const string &)>(&Player::country)
		)

		.add_property("id",
			make_function(static_cast<const unsigned int &(Player::*)() const>(&Player::id), return_value_policy<copy_const_reference>())
		)
		.add_property("id",
			make_function(static_cast<const unsigned int &(Player::*)() const>(&Player::id), return_value_policy<copy_const_reference>())
		)

		.add_property("aliases",
			make_function(static_cast<Player::NameList & (Player::*)()>(&Player::aliases), return_internal_reference<>()),
			//static_cast<void (Player::*)(const Player::NameList &)>(&Player::aliases)
			static_cast<void (*)(Player &, bp::object &)>(set_player_aliases)
		)
		;

	{
	scope map_scope
		= class_<Map, Map*>("Map", init<unsigned int, const std::string &, const std::string &, int, Map::Type, const std::string &, const std::string &>(args("id", "campaign", "name", "game", "type", "url", "aliases")))
			.add_property("id",
				make_function(static_cast<const unsigned int &(Map::*)() const>(&Map::id), return_value_policy<copy_const_reference>())
			)
			.add_property("game",
				make_function(static_cast<const int &(Map::*)() const>(&Map::game), return_value_policy<copy_const_reference>())
			)
			.add_property("type",
				make_function(static_cast<const Map::Type &(Map::*)() const>(&Map::type), return_value_policy<copy_const_reference>())
			)
			.add_property("campaign",
				make_function(static_cast<const string &(Map::*)() const>(&Map::campaign), return_value_policy<copy_const_reference>())
			)
			.add_property("url",
				make_function(static_cast<const string &(Map::*)() const>(&Map::url), return_value_policy<copy_const_reference>())
			)
			.add_property("name",
				make_function(static_cast<const string &(Map::*)() const>(&Map::name), return_value_policy<copy_const_reference>())
			)
			.add_property("aliases",
				make_function(&Map::aliases, return_internal_reference<>())
			)
			.def("order", &Map::order)
			.def("__eq__", &EqualMap)
			.def("write_out_str", &Map::write_out_str)
		;

	bp::enum_<Map::Type>("Type")
		.value("OFFICIAL", Map::OFFICIAL)
		.value("CUSTOM", Map::CUSTOM)
		.export_values()
		;
	}

	scope default_scope;

	class_<std::vector<bool> >("BoolVec")
		.def(vector_indexing_suite<std::vector<bool> >())
	;

	class_<Group, Group*, boost::noncopyable>("Group", no_init)
	;

	class_<Strategy, Strategy*, bases<Group> >("Strategy", init<unsigned int const &, string const &, string const &, Map *, Strategy::RecordList, string const &>(args("id","name","description","map","records","aliases")))
		.def(init<unsigned int const &, string const &, string const &, Map *, Strategy::RecordList, string const &>())
		.add_property("name",
			make_function(static_cast<const string &(Group::*)() const>(&Strategy::name), return_value_policy<copy_const_reference>()),
			static_cast<void (Group::*)(const string &)>(&Strategy::name)
		)

		.add_property("description",
			make_function(static_cast<const string &(Strategy::*)() const>(&Strategy::description), return_value_policy<copy_const_reference>()),
			static_cast<void (Strategy::*)(const string &)>(&Strategy::description)
		)

		.add_property("id",
			make_function(static_cast<const unsigned int &(Strategy::*)() const>(&Strategy::id), return_value_policy<copy_const_reference>())
		)

		.add_property("map",
			make_function(static_cast<const Map * (Strategy::*)() const>(&Strategy::map), return_internal_reference<>())
		)

		.add_property("records",
			make_function(static_cast<const Strategy::RecordList & (Strategy::*)() const>(&Strategy::records), return_internal_reference<>())
		)

		.add_property("aliases",
			make_function(&Strategy::aliases, return_internal_reference<>())
		)

		.def("add_record", &Strategy::add_record)
		.def("write_out_str", &Strategy::write_out_str)
	;

	class_<Gamemode, Gamemode*, bases<Group> >("Gamemode", init<unsigned int const &, string const &, string const &, bool const &, int, string const &, const int &>(args("id","name","description","mutation","game","aliases","numplayers")))
		.add_property("name",
			make_function(static_cast<const string &(Group::*)() const>(&Gamemode::name), return_value_policy<copy_const_reference>()),
			static_cast<void (Group::*)(const string &)>(&Gamemode::name)
		)

		.add_property("description",
			make_function(static_cast<const string &(Gamemode::*)() const>(&Gamemode::description), return_value_policy<copy_const_reference>()),
			static_cast<void (Gamemode::*)(const string &)>(&Gamemode::description)
		)

		.add_property("id",
			make_function(static_cast<const unsigned int &(Gamemode::*)() const>(&Gamemode::id), return_value_policy<copy_const_reference>())
		)
		.add_property("game",
			make_function(static_cast<int (Gamemode::*)() const>(&Gamemode::game))
		)

		.add_property("mutation",
			make_function(static_cast<const bool & (Gamemode::*)() const>(&Gamemode::mutation), return_value_policy<copy_const_reference>())
		)

		.add_property("aliases",
			make_function(&Gamemode::aliases, return_value_policy<copy_const_reference>())
		)

		.add_property("records",
			make_function(static_cast<const Gamemode::RecordList & (Gamemode::*)() const>(&Gamemode::records), return_value_policy<copy_const_reference>())
		)
		.def("add_record", &Gamemode::add_record)
		.add_property("numplayers",
			make_function(&Gamemode::numplayers, return_value_policy<copy_const_reference>())
		)
		.def("write_out_str", &Gamemode::write_out_str)
		.def_readonly("ANY_GAME", &Gamemode::ANY_GAME)
		.def_readonly("ANY_NUM_PLAYERS", &Gamemode::ANY_NUM_PLAYERS)
	;

	class_<PlayerGroup, PlayerGroup*, bases<Group> >("PlayerGroup", init<unsigned int const &, string const &, string const &, string const &, PlayerGroup::PlayerList const &, string const &, string const &>(args("id","abbreviation","name","description","players","aliases","countries")))
		.def(init<unsigned int const &, string const &, string const &, string const &, PlayerGroup::PlayerList const &, string const &, string const &, const string &>(args("id","abbreviation","name","description","players","aliases","countries","url")))
		.add_property("name",
			make_function(static_cast<const string &(PlayerGroup::*)() const>(&PlayerGroup::name), return_value_policy<copy_const_reference>()),
			static_cast<void (Group::*)(const string &)>(&PlayerGroup::name)
		)
		.add_property("url",
			make_function(static_cast<const string &(PlayerGroup::*)() const>(&PlayerGroup::url), return_value_policy<copy_const_reference>()),
			static_cast<void (PlayerGroup::*)(const string &)>(&PlayerGroup::url)
		)

		.add_property("description",
			make_function(static_cast<const string &(PlayerGroup::*)() const>(&PlayerGroup::description), return_value_policy<copy_const_reference>()),
			static_cast<void (PlayerGroup::*)(const string &)>(&PlayerGroup::description)
		)

		.add_property("id",
			make_function(static_cast<const unsigned int &(PlayerGroup::*)() const>(&PlayerGroup::id), return_value_policy<copy_const_reference>())
		)

		.add_property("aliases",
			make_function(&PlayerGroup::aliases, return_internal_reference<>())
		)
		.add_property("players",
			make_function(static_cast<PlayerGroup::PlayerList & (PlayerGroup::*)()>(&PlayerGroup::players), return_internal_reference<>())
		)
		.add_property("countries",
			make_function(static_cast<const PlayerGroup::CountryList & (PlayerGroup::*)() const>(&PlayerGroup::countries), return_internal_reference<>())
		)
		.def("write_out_str", &PlayerGroup::write_out_str)
		.def("add_player", &PlayerGroup::add_player)
	;

	class_<HonorList, HonorList*, bases<Group> >("HonorList", init<unsigned int const &, string const &, string const &, HonorList::PlayerList const &, string const &, ExtraInfo const &>(args("id","name","description","players","aliases","extra_info")))
		.add_property("name",
			make_function(static_cast<const string &(HonorList::*)() const>(&HonorList::name), return_value_policy<copy_const_reference>()),
			static_cast<void (Group::*)(const string &)>(&HonorList::name)
		)

		.add_property("description",
			make_function(static_cast<const string &(HonorList::*)() const>(&HonorList::description), return_value_policy<copy_const_reference>()),
			static_cast<void (HonorList::*)(const string &)>(&HonorList::description)
		)

		.add_property("id",
			make_function(static_cast<const unsigned int &(HonorList::*)() const>(&HonorList::id), return_value_policy<copy_const_reference>())
		)

		.add_property("aliases",
			make_function(&HonorList::aliases, return_internal_reference<>())
		)
		.add_property("players",
			make_function(static_cast<HonorList::PlayerList & (HonorList::*)()>(&HonorList::players), return_internal_reference<>())
		)
		.def("write_out_str", &HonorList::write_out_str)
		.def("add_player", &HonorList::add_player)
	;

	class_<std::unary_function<Record *, float>, std::unary_function<Record *, float>* >("factor", init<>());
	class_<Factor, Factor*, boost::noncopyable>("Factor", no_init);

	class_<Record::trash_factor, Record::trash_factor*, bases<Factor> >("trash_factor", init<>())
		.def("__call__", &Record::trash_factor::operator())
	;
	class_<Record::score_factor, Record::score_factor*, bases<Factor> >("score_factor", init<>())
		.def("__call__", &Record::score_factor::operator())
	;
	class_<Record::kill_factor, Record::kill_factor*, bases<Factor> >("kill_factor", init<>())
		.def("__call__", &Record::kill_factor::operator())
	;
	class_<Record::gore_factor, Record::gore_factor*, bases<Factor> >("gore_factor", init<>())
		.def("__call__", &Record::gore_factor::operator())
	;
	class_<Record::time_factor, Record::time_factor*, bases<Factor> >("time_factor", init<>())
		.def("__call__", &Record::time_factor::operator())
	;
	class_<Record::common_factor, Record::common_factor*, bases<Factor> >("common_factor", init<>())
		.def("__call__", &Record::common_factor::operator())
	;
	class_<Record::tank_factor, Record::tank_factor*, bases<Factor> >("tank_factor", init<>())
		.def("__call__", &Record::tank_factor::operator())
	;

	class_<Record, Record*>("Record", init<unsigned int const &, Record::Time const &, Map *, Record::Date const &, int, int, int, int, int, Player *, Player *, Player *, Player *>(args("id","time","map","date","common","hunters","smokers","boomers","tanks","p1","p2","p3","p4")))
		.add_property("id",
			make_function(static_cast<const unsigned int &(Record::*)() const>(&Record::id), return_value_policy<copy_const_reference>())
		)
		.add_property("groups",
			make_function(static_cast<Record::GroupList & (Record::*)()>(&Record::groups), return_internal_reference<>())
		)
		.add_property("map",
			make_function(static_cast<const Map *(Record::*)() const>(&Record::map), return_internal_reference<>())
		)
		.add_property("players",
			make_function(static_cast<const Record::PlayerList &(Record::*)() const>(&Record::players), return_internal_reference<>()),
			static_cast<void (*)(Record &, bp::object &)>(set_record_players)
		)
		.add_property("date",
			make_function(static_cast<const Record::Date &(Record::*)() const>(&Record::date), return_value_policy<return_by_value>()),
			static_cast<void (Record::*)(const Record::Date &)>(&Record::date)
		)
		.add_property("time",
			make_function(static_cast<const Record::Time &(Record::*)() const>(&Record::time), return_value_policy<return_by_value>()),
			static_cast<void (Record::*)(const Record::Time &)>(&Record::time)
		)
		.add_property("common",
			make_function(static_cast<const int &(Record::*)() const>(&Record::common), return_value_policy<copy_const_reference>()),
			static_cast<void (Record::*)(const int &)>(&Record::common)
		)
		.add_property("hunters",
			make_function(static_cast<const int &(Record::*)() const>(&Record::hunters), return_value_policy<copy_const_reference>()),
			static_cast<void (Record::*)(const int &)>(&Record::hunters)
		)
		.add_property("smokers",
			make_function(static_cast<const int &(Record::*)() const>(&Record::smokers), return_value_policy<copy_const_reference>()),
			static_cast<void (Record::*)(const int &)>(&Record::smokers)
		)
		.add_property("boomers",
			make_function(static_cast<const int &(Record::*)() const>(&Record::boomers), return_value_policy<copy_const_reference>()),
			static_cast<void (Record::*)(const int &)>(&Record::boomers)
		)
		.add_property("tanks",
			make_function(static_cast<const int &(Record::*)() const>(&Record::tanks), return_value_policy<copy_const_reference>()),
			static_cast<void (Record::*)(const int &)>(&Record::tanks)
		)
		.def("is_mutation", &Record::is_mutation)
		.def("write_out_str", &Record::write_out_str)
		.def("__eq__", &EqualRecord)
		.def_readonly("TrashFactor", &Record::TrashFactor)
		.def_readonly("KillFactor", &Record::KillFactor)
		.def_readonly("ScoreFactor", &Record::ScoreFactor)
		.def_readonly("GoreFactor", &Record::GoreFactor)
		.def_readonly("CommonFactor", &Record::CommonFactor)
		.def_readonly("TankFactor", &Record::TankFactor)
		.def_readonly("TimeFactor", &Record::TimeFactor)
	;

	class_<Record2, Record2*, bases<Record> >("Record2", init<unsigned int const &, Record::Time const &, Map *, Record::Date const &, int, int, int, int, int, int, int, int, Record::PlayerList>(args("id","time","map","date","common","hunters","smokers","boomers","chargers","jockeys","spitters","tanks","playerlist")))
  		.add_property("id",
		make_function(static_cast<const unsigned int &(Record2::*)() const>(&Record2::id), return_value_policy<copy_const_reference>())
		)
		.add_property("map",
			make_function(static_cast<const Map *(Record2::*)() const>(&Record2::map), return_internal_reference<>())
		)
		.add_property("date",
			make_function(static_cast<const Record2::Date &(Record2::*)() const>(&Record2::date), return_value_policy<return_by_value>()),
			static_cast<void (Record2::*)(const Record2::Date &)>(&Record2::date)
		)
		.add_property("time",
			make_function(static_cast<const Record2::Time &(Record2::*)() const>(&Record2::time), return_value_policy<return_by_value>()),
			static_cast<void (Record2::*)(const Record2::Time &)>(&Record2::time)
		)
		.add_property("common",
			make_function(static_cast<const int &(Record2::*)() const>(&Record2::common), return_value_policy<copy_const_reference>()),
			static_cast<void (Record2::*)(const int &)>(&Record2::common)
		)
		.add_property("hunters",
			make_function(static_cast<const int &(Record2::*)() const>(&Record2::hunters), return_value_policy<copy_const_reference>()),
			static_cast<void (Record2::*)(const int &)>(&Record2::hunters)
		)
		.add_property("smokers",
			make_function(static_cast<const int &(Record2::*)() const>(&Record2::smokers), return_value_policy<copy_const_reference>()),
			static_cast<void (Record2::*)(const int &)>(&Record2::smokers)
		)
		.add_property("boomers",
			make_function(static_cast<const int &(Record2::*)() const>(&Record2::boomers), return_value_policy<copy_const_reference>()),
			static_cast<void (Record2::*)(const int &)>(&Record2::boomers)
		)
		.add_property("chargers",
			make_function(static_cast<const int &(Record2::*)() const>(&Record2::chargers), return_value_policy<copy_const_reference>()),
			static_cast<void (Record2::*)(const int &)>(&Record2::chargers)
		)
		.add_property("jockeys",
			make_function(static_cast<const int &(Record2::*)() const>(&Record2::jockeys), return_value_policy<copy_const_reference>()),
			static_cast<void (Record2::*)(const int &)>(&Record2::jockeys)
		)
		.add_property("spitters",
			make_function(static_cast<const int &(Record2::*)() const>(&Record2::spitters), return_value_policy<copy_const_reference>()),
			static_cast<void (Record2::*)(const int &)>(&Record2::spitters)
		)
		.add_property("tanks",
			make_function(static_cast<const int &(Record2::*)() const>(&Record2::tanks), return_value_policy<copy_const_reference>()),
			static_cast<void (Record2::*)(const int &)>(&Record2::tanks)
		)
		.add_property("groups",
			make_function(static_cast<Record::GroupList & (Record::*)()>(&Record::groups), return_internal_reference<>())
		)
		.def("write_out_str", &Record2::write_out_str)
	;

	class_<RecordTracker, RecordTracker*>("RecordTracker")
		.add_property("maps",
			make_function(&RecordTracker::maps, return_internal_reference<>())
		)
		.add_property("records",
			make_function(static_cast<RecordTracker::RecordList & (RecordTracker::*)()>(&RecordTracker::records), return_internal_reference<>())
		)
		.add_property("records_1",
			make_function(static_cast<RecordTracker::RecordList & (RecordTracker::*)()>(&RecordTracker::records_1), return_internal_reference<>())
		)
		.add_property("records_2",
			make_function(static_cast<RecordTracker::RecordList & (RecordTracker::*)()>(&RecordTracker::records_2), return_internal_reference<>())
		)
		.add_property("official_maps",
			make_function(&RecordTracker::official_maps, return_internal_reference<>())
		)
		.add_property("official_maps_1",
			make_function(&RecordTracker::official_maps_1, return_internal_reference<>())
		)
		.add_property("official_maps_2",
			make_function(&RecordTracker::official_maps_2, return_internal_reference<>())
		)
		.add_property("custom_maps",
			make_function(&RecordTracker::custom_maps, return_internal_reference<>())
		)
		.add_property("custom_maps_1",
			make_function(&RecordTracker::custom_maps_1, return_internal_reference<>())
		)
		.add_property("custom_maps_2",
			make_function(&RecordTracker::custom_maps_2, return_internal_reference<>())
		)
		.add_property("strategies",
			make_function(static_cast<RecordTracker::StrategyList & (RecordTracker::*)()>(&RecordTracker::strategies), return_internal_reference<>())
		)
		.add_property("players",
			make_function(&RecordTracker::players, return_internal_reference<>())
		)
		.add_property("gamemodes",
			make_function(static_cast<RecordTracker::GamemodeList & (RecordTracker::*)()>(&RecordTracker::gamemodes), return_internal_reference<>())
		)
		.add_property("playergroups",
			make_function(static_cast<RecordTracker::PlayerGroupList & (RecordTracker::*)()>(&RecordTracker::playergroups), return_internal_reference<>())
		)
		.add_property("honorlists",
			make_function(static_cast<RecordTracker::HonorlistList & (RecordTracker::*)()>(&RecordTracker::honorlists), return_internal_reference<>())
		)
		.def("read_players", &RecordTracker::read_players)
		.def("read_maps", &RecordTracker::read_maps)
		.def("read_records", read_records1)
		.def("read_records", read_records2)
		.def("read_groups", read_groups1)
		.def("read_groups", read_groups2)
		.def("find_map", &RecordTracker::find_map, return_internal_reference<>())
		.def("find_record", &RecordTracker::find_record, return_internal_reference<>())
		.def("find_player", &RecordTracker::find_player, return_internal_reference<>())
		.def("find_strategy", &RecordTracker::find_strategy, return_internal_reference<>())
		.def("find_gamemode", &RecordTracker::find_gamemode, return_internal_reference<>())
		.def("find_playergroup", &RecordTracker::find_playergroup, return_internal_reference<>())
		.def("add_player", &RecordTracker::add_player, return_internal_reference<>())
		.def("add_map", &RecordTracker::add_map, return_internal_reference<>())
		.def("add_record", static_cast<Record * (RecordTracker::*)(const Record::Time &, Map *, const Record::Date &, const int &, const int &, const int &, const int &, const int &, Player *, Player *, Player *, Player *)>(&RecordTracker::add_record), return_internal_reference<>())
		.def("add_record_ids", static_cast<Record * (RecordTracker::*)(const Record::Time &, unsigned int, const Record::Date &, const int &, const int &, const int &, const int &, const int &, unsigned int, unsigned int, unsigned int, unsigned int)>(&RecordTracker::add_record), return_internal_reference<>())
		.def("add_record_2", &RecordTracker::add_record_2, return_internal_reference<>())
		.def("add_strategy", &RecordTracker::add_strategy, return_internal_reference<>())
		.def("add_gamemode", &RecordTracker::add_gamemode, return_internal_reference<>())
		.def("add_playergroup", &RecordTracker::add_playergroup, return_internal_reference<>())
		.def("write_players", &RecordTracker::write_players)
		.def("write_maps", &RecordTracker::write_maps)
		.def("write_records", &RecordTracker::write_records)
		.def("write_groups", &RecordTracker::write_groups)
		.def("find_map_records", &RecordTracker::find_map_records)
		.def("find_map_records_sorted", &RecordTracker::find_map_records_sorted)
		.def("find_map_records_filtered", static_cast<std::vector<Record *> (*)(RecordTracker &, Map *, int, const Factor &, bp::object &)>(find_map_records_filtered))
	;
}
