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
using namespace std;
using namespace boost::python;
namespace bp = boost::python;
using boost::posix_time::time_duration;
using boost::gregorian::date;

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

BOOST_PYTHON_MODULE(survival)
{
	bind_datetime();

	class_<vector<string> >("StringList")
		.def(vector_indexing_suite<vector<string> >())
	;

	set_wrapper<std::multiset< Player *, Player::LessPtr >, Player *>().wrap("PlayerList");
	set_wrapper<std::multiset< Record *, Record::LessPtr >, Record *>().wrap("RecordList");
	set_wrapper<std::multiset< Strategy *, Strategy::LessPtr >, Strategy *>().wrap("StrategyList");
	set_wrapper<std::multiset< Gamemode *, Group::LessPtr >, Gamemode *>().wrap("GamemodeList");
	set_wrapper<std::multiset< PlayerGroup *, Group::LessPtr >, PlayerGroup *>().wrap("PlayerGroupList");
	set_wrapper<std::multiset< Map *, Map::LessPtr >, Map *>().wrap("MapList");

	class_<Player, Player*>("Player", init<unsigned int const &, string const &, string const &, string const &>(args("id","name","country","aliases")))
		.add_property("name",
			make_function(static_cast<const string &(Player::*)() const>(&Player::name), return_value_policy<copy_const_reference>()),
			static_cast<void (Player::*)(const string &)>(&Player::name)
		)

		.add_property("country",
			make_function(static_cast<const string &(Player::*)() const>(&Player::country), return_value_policy<copy_const_reference>()),
			static_cast<void (Player::*)(const string &)>(&Player::country)
		)

		.add_property("id",
			make_function(static_cast<const unsigned int &(Player::*)() const>(&Player::id), return_value_policy<copy_const_reference>())
		)

		.add_property("aliases",
			make_function(&Player::aliases, return_internal_reference<>())
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

	class_<Strategy, Strategy*>("Strategy", init<unsigned int const &, string const &, string const &, Map *, Strategy::RecordList, string const &>(args("id","name","description","map","records","aliases")))
	//class_<Strategy, Strategy*, bases<Group> >("Strategy", init<unsigned int const &, string const &, string const &, Map *, Strategy::RecordList, string const &>(args("id","name","description","map","records","aliases")))
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

		.add_property("aliases",
			make_function(&Strategy::aliases, return_internal_reference<>())
		)
	;

	class_<Gamemode, Gamemode* >("Gamemode", init<unsigned int const &, string const &, string const &, bool const &, string const &>(args("id","name","description","mutation","aliases")))
	//class_<Gamemode, Gamemode*, bases<Group> >("Gamemode", init<unsigned int const &, string const &, string const &, bool const &, string const &>(args("id","name","description","mutation","aliases")))
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

		.add_property("mutation",
			make_function(static_cast<const bool & (Gamemode::*)() const>(&Gamemode::mutation), return_value_policy<copy_const_reference>())
		)

		.add_property("aliases",
			make_function(&Gamemode::aliases, return_value_policy<copy_const_reference>())
		)

		.add_property("records",
			make_function(static_cast<const Gamemode::RecordList & (Gamemode::*)() const>(&Gamemode::records), return_value_policy<copy_const_reference>())
		)
	;

	class_<PlayerGroup, PlayerGroup* >("PlayerGroup", init<unsigned int const &, string const &, string const &, PlayerGroup::PlayerList const &, string const &>(args("id","name","description","players","aliases")))
	//class_<PlayerGroup, PlayerGroup*, bases<Group> >("PlayerGroup", init<unsigned int const &, string const &, string const &, PlayerGroup::PlayerList const &, string const &>(args("id","name","description","players","aliases")))
		.add_property("name",
			make_function(static_cast<const string &(Group::*)() const>(&PlayerGroup::name), return_value_policy<copy_const_reference>()),
			static_cast<void (Group::*)(const string &)>(&PlayerGroup::name)
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
	;

	class_<Record, Record*>("Record", init<unsigned int const &, Record::Time const &, Map *, Record::Date const &, int, int, int, int, int, Player *, Player *, Player *, Player *>(args("id","time","map","date","common","hunters","smokers","boomers","tanks","p1","p2","p3","p4")))
		.add_property("id",
			make_function(static_cast<const unsigned int &(Record::*)() const>(&Record::id), return_value_policy<copy_const_reference>())
		)
		.add_property("map",
			make_function(static_cast<const Map *(Record::*)() const>(&Record::map), return_internal_reference<>())
		)
		.add_property("date",
			make_function(static_cast<const Record::Date &(Record::*)() const>(&Record::date), return_value_policy<return_by_value>())
		)
		.add_property("time",
			make_function(static_cast<const Record::Time &(Record::*)() const>(&Record::time), return_value_policy<return_by_value>())
		)
		.add_property("common",
			make_function(static_cast<const int &(Record::*)() const>(&Record::common), return_value_policy<copy_const_reference>())
		)
		.add_property("hunters",
			make_function(static_cast<const int &(Record::*)() const>(&Record::hunters), return_value_policy<copy_const_reference>())
		)
		.add_property("smokers",
			make_function(static_cast<const int &(Record::*)() const>(&Record::smokers), return_value_policy<copy_const_reference>())
		)
		.add_property("boomers",
			make_function(static_cast<const int &(Record::*)() const>(&Record::boomers), return_value_policy<copy_const_reference>())
		)
		.add_property("tanks",
			make_function(static_cast<const int &(Record::*)() const>(&Record::tanks), return_value_policy<copy_const_reference>())
		)
	;

	class_<RecordTracker, RecordTracker*>("RecordTracker")
		.add_property("maps",
			make_function(&RecordTracker::maps, return_internal_reference<>())
		)
		.add_property("records",
			make_function(static_cast<RecordTracker::RecordList & (RecordTracker::*)()>(&RecordTracker::records), return_internal_reference<>())
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
			make_function(&RecordTracker::strategies, return_internal_reference<>())
		)
		.add_property("players",
			make_function(&RecordTracker::players, return_internal_reference<>())
		)
		.add_property("gamemodes",
			make_function(&RecordTracker::gamemodes, return_internal_reference<>())
		)
		.add_property("playergroups",
			make_function(&RecordTracker::playergroups, return_internal_reference<>())
		)
		.def("read_players", &RecordTracker::read_players)
		.def("read_maps", &RecordTracker::read_maps)
		.def("read_records", &RecordTracker::read_records)
		.def("read_groups", &RecordTracker::read_groups)
		.def("find_map", &RecordTracker::find_map, return_internal_reference<>())
		.def("find_record", &RecordTracker::find_record, return_internal_reference<>())
		.def("find_player", &RecordTracker::find_player, return_internal_reference<>())
	;
}
