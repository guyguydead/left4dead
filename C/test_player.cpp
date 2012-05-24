#include "records.h"
#include <iostream>
#include <sstream>
using namespace std;

bool test1();
bool test2();

int main()
{
	test1();
	test2();

	return 0;
}

bool test1()
{
	RecordTracker r;
	r.read_players("test_player_file.txt");

	return true;
}

bool test2()
{
	ExtraInfo ei;
	ei.insert("info1", "1");
	ei.insert("info2", "2");
	ei.insert("info3", "3");

	stringstream ss(stringstream::in | stringstream::out);

	ss << ei;

	string s;
	ss >> s;

	assert(s == "info1=1;info2=2;info3=3");
	return true;
}
