#ifndef UTILITY_H_
#define UTILITY_H_

#include <algorithm>
#include <functional>
#include <locale>
#include <string>
#include <iostream>

//==================================================
// class StringTokenizer
//!
//! \brief Used to tokenize a string based on a token.
//==================================================
class StringTokenizer
{
private:
	StringTokenizer();
	std::string delim_;
	std::string str_;
	unsigned int count_;
	unsigned int begin_;
	unsigned int end_;

public:
	StringTokenizer(const std::string & s, const char * delim = NULL);
	size_t countTokens();
	bool hasMoreTokens() const;
	void nextToken(std::string & s);
};

inline StringTokenizer::StringTokenizer() { }

inline StringTokenizer::StringTokenizer(const std::string & s, const char * delim)
	: str_(s), count_(-1), begin_(0), end_(0)
{
	if (!delim)
		delim_ = " \f\n\r\t\v"; // default to whitespace
	else
		delim_ = delim;

	// point to the first token
	begin_ = str_.find_first_not_of(delim_);
	end_ = str_.find_first_of(delim_, begin_);
}

inline size_t StringTokenizer::countTokens()
{
	using std::string;
	if (count_ >= 0) // return if we've already counted
		return count_;

	string::size_type n = 0;
	string::size_type i = 0;

	for (;;)
	{
		// advance to the first token
		i = str_.find_first_not_of(delim_, i);
		if (i == string::npos)
			break;

		i = str_.find_first_of(delim_, i+1);
		n++;
		if (i == string::npos)
			break;
	}

	count_ = n;
	return count_;
}

inline bool StringTokenizer::hasMoreTokens() const
{
	return (begin_ != end_);
}

inline void StringTokenizer::nextToken(std::string & s)
{
	using std::string;
	if (begin_ != string::npos && end_ != string::npos)
	{
		s = str_.substr(begin_, end_ - begin_);
		begin_ = str_.find_first_not_of(delim_, end_);
		end_ = str_.find_first_of(delim_, begin_);
	}
	else if (begin_ != string::npos && end_ == string::npos)
	{
		s = str_.substr(begin_, str_.length() - begin_);
		begin_ = str_.find_first_not_of(delim_, end_);
	}
}

// trim from start
inline std::string &ltrim(std::string &s)
{
	s.erase(s.begin(), std::find_if(s.begin(), s.end(), std::not1(std::ptr_fun<int, int>(std::isspace))));
	return s;
}

// trim from end
inline std::string &rtrim(std::string &s)
{
	s.erase(std::find_if(s.rbegin(), s.rend(), std::not1(std::ptr_fun<int, int>(std::isspace))).base(), s.end());
	return s;
}

// trim from both ends
inline std::string &trim(std::string &s)
{
	return ltrim(rtrim(s));
}

#ifndef NO_BOOST_

#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/date_time/gregorian/gregorian.hpp>

inline boost::posix_time::time_duration create_time_duration(const std::string & s)
{
	StringTokenizer st(s, ":");
	boost::posix_time::time_duration d;

	if (st.countTokens() == 1)
	{
		d = boost::posix_time::duration_from_string("00:" + s);
	}
	else
	{
		d = boost::posix_time::duration_from_string(s);
	}

	return d;
}

#endif

#endif
