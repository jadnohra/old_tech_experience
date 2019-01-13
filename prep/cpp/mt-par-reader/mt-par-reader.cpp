#include <iostream>
#include <string>
#include <limits>
#include <atomic>
#include <mutex>
#include <thread>
#include <vector>
using namespace std;

typedef size_t Cursor;
const Cursor EOP = numeric_limits<Cursor>::max();

const int thread_count = 5;
const string paragraph = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book.";

atomic<int> cursor;		// shared, rw
atomic<int> turn;			// shared, rw
mutex mu;

// Also works if already at EOP, returning EOP without any printing
Cursor read_next_word(Cursor cursor)
{
	assert(EOP >= paragraph.length());


	while (cursor < paragraph.length() && paragraph[cursor] != ' ')
	{
			cout << paragraph[cursor];
			cursor = cursor + 1;
	}
	cout << " " << flush;

	if (cursor == paragraph.length())
		return EOP;

	return cursor + 1;
}

void thread_func(int my_index)
{
	assert(thread_count > 1);
	while (true)
	{
		this_thread::yield();

		lock_guard<mutex> lock(mu);
		int curr_turn = turn.load();
		int curr_cursor = cursor.load();

		if (curr_cursor == EOP)
		{
			break;
		}

		if (curr_turn != my_index)
		{
			continue;
		}

		int new_cursor = read_next_word(curr_cursor);
		cursor.store(new_cursor);
		turn.store((curr_turn+1) % thread_count);
	}
}

int main(int argc, const char** argv)
{
	cursor.store(0);
	turn.store(0);

	vector<thread> threads;

	for (int i=0; i < thread_count; i++)
	{
		threads.push_back(thread(thread_func, i));
	}

	for (int i=0; i < thread_count; i++)
	{
		threads[i].join();
	}

	return 0;
}