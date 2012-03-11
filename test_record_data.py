from record_data import *

def test1():
	m = Map('Mall Atrium', 'Dead Center', 'Left 4 Dead 2')

	assert m.name == 'Mall Atrium'
	assert m.campaign == 'Dead Center'
	assert m.game == 'Left 4 Dead 2'

	return True

test_suite = [test1]

#--------------------------------------------------
# main script
#--------------------------------------------------
print 'Running tests'

for test_fcn in test_suite:
	assert(test_fcn())

print 'Complete'
