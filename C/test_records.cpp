#include "records.h"
#include <iostream>
using namespace std;

bool test1();

int main()
{
	test1();

	return 0;
}

bool test1()
{
	RecordTracker r;
	r.read_players("../players.txt");
	r.read_maps("../maps.txt");
	r.read_records("../records.txt");
	r.read_groups("../groups.txt");

	cout << r.players().size() << " players read\n";
	cout << r.maps().size() << " maps read\n";
	cout << r.records().size() << " records read\n";
	cout << (r.strategies().size() + r.gamemodes().size() + r.playergroups().size()) << " groups read\n";

/*
	cout << "Official Maps 1\n";

	for (RecordTracker::MapList::const_iterator i = r.official_maps_1().begin(); i != r.official_maps_1().end(); ++i)
	{
		assert(*i != NULL);
		cout << (*i)->name() << " " << (*i)->campaign() << "\n";
	}
	cout << "Official Maps 2\n";
	for (RecordTracker::MapList::const_iterator i = r.official_maps_2().begin(); i != r.official_maps_2().end(); ++i)
	{
		assert(*i != NULL);
		cout << (*i)->name() << " " << (*i)->campaign() << "\n";
	}
*/
	return true;
}
