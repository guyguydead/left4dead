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
	r.read_players("test_player_file.txt");

	return true;
}
