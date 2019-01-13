#include <vector>
#include <queue>
#include <set>
#include <thread>
#include <cmath>
#include <iostream>
#include <atomic>
#include <cassert>
#include <memory>
using namespace std;


#include <boost/program_options.hpp>
namespace po = boost::program_options;

bool g_verbose = false;

// No FIFO during unblocking, but simple
namespace impl_random
{

	class Semaphore
	{
		public:

			Semaphore(const Semaphore&) = delete;
			Semaphore(Semaphore&&) = delete;
			Semaphore operator=(const Semaphore&) = delete;
			Semaphore operator=(Semaphore&&) = delete;

			Semaphore(int n, int max_threads)
			:	n_(n)
			{
				tokens_ = unique_ptr<atomic<bool>[]>(new atomic<bool>[n]);
				mutexes_ = unique_ptr<mutex[]>(new mutex[n]);
				for (int i=0; i<n; i++)
				{
					tokens_[i].store(true);
				}
			}

			~Semaphore()
			{
			}

			int acquire()
			{
				int my_index = (int) ((counter_++) % n_);
				bool acquired = false;

				while (!acquired)
				{
					int iter = 0;
					while (!tokens_[my_index].load())
					{
						if (iter++ == 0 && g_verbose) cout << "?" << flush;
						this_thread::yield();
					}

					{
						lock_guard<mutex> lock(mutexes_[my_index]);
						if (tokens_[my_index].load())
						{
							acquired = true;
							tokens_[my_index].store(false);
						}
					}
				}

				return my_index;
			}

			void release(int my_index)
			{
				tokens_[my_index].store(true);
			}

		private:
			unsigned int n_;
			atomic<unsigned int> counter_;
			unique_ptr<atomic<bool>[]> tokens_; // true if token is available
			unique_ptr<mutex[]> mutexes_;
	};
}
namespace impl_3 = impl_random;

// clumsy_1 but trying to use condition_variable
namespace impl_cv_clumsy_1
{

	class Semaphore
	{
		public:

			Semaphore(const Semaphore&) = delete;
			Semaphore(Semaphore&&) = delete;
			Semaphore operator=(const Semaphore&) = delete;
			Semaphore operator=(Semaphore&&) = delete;

			Semaphore(int n, int max_threads)
			: n_(n)
			{
				counter_.store(n);
			}

			~Semaphore()
			{
			}

			int acquire()
			{
				bool enter_blocking = false;
				{
					lock_guard<mutex> lock(mu_counter_);
					if(counter_.load() == 0)
					{
						// If counter is 0 'while' another acquire or release is happening, it's ok to enter blocked state (wasting some time),
						// since we or some other thread will be woken up when the release finishes.
						enter_blocking = true;
					}
					else
					{
						// If counter is non-0 'while' another acquire or release is happening: cannot happen, mu_counter_ disallows this
						counter_--;
					}
				}

				if (enter_blocking)
				{
					unique_lock<mutex> lock(mu_block_);
					block_cond.wait(lock);	// TODO: handle spurious wake-up
				}

				return 0;
			}

			void release(int)
			{
				{
					lock_guard<mutex> lock(mu_counter_);
					counter_++;
				}

				{
					//unique_lock<mutex> lock(mu_block_);
					block_cond.notify_one();
				}
			}

		private:

			int n_;
			int max_threads_;
			atomic<int> counter_;
			mutex mu_counter_;
			condition_variable block_cond;
			mutex mu_block_;
	};
}
namespace impl_2 = impl_cv_clumsy_1;

// First clumsy attempt, trying to use mutexes only, and busy waiting
// Requires knowing the maximum number of threads and has to allocate
// large arrays to fit all of them even if they are not used
namespace impl_clumsy_1
{

	class Semaphore
	{
	public:

		Semaphore(const Semaphore&) = delete;
		Semaphore(Semaphore&&) = delete;
		Semaphore operator=(const Semaphore&) = delete;
		Semaphore operator=(Semaphore&&) = delete;

		Semaphore(int n, int max_threads)
		: n_(n), max_threads_(max_threads)
		{
			counter_.store(n);
			unblock_signal = unique_ptr<atomic<bool>[]>(new atomic<bool>[max_threads]);
			for (int i=0; i<max_threads; i++)
			{
				unblock_signal_free_list.push(i);
			}
		}

		~Semaphore()
		{
			{
				lock_guard<mutex> lock(mu_unblock_signal);
				assert(unblock_signal_free_list.size() == max_threads_);
				// Note that this is not enough, some thread could be acquiring while we check
			}
		}

		int acquire()
		{
			bool enter_blocking = false;
			{
				lock_guard<mutex> lock(mu_counter_);
				if(counter_.load() == 0)
				{
					// If counter is 0 'while' another acquire or release is happening, it's ok to enter blocked state (wasting some time),
					// since we or some other thread will be woken up when the release finishes.
					enter_blocking = true;
				}
				else
				{
					// If counter is non-0 'while' another acquire or release is happening: cannot happen, mu_counter_ disallows this
					counter_--;
				}
			}

			if (enter_blocking)
			{
				int my_id = acquire_id();
				while(unblock_signal[my_id] == false)
				{
					if (g_verbose) cout << "!" << flush;
					this_thread::yield();
				}
				release_id(my_id);
			}
			return 0;
		}

		void release(int)
		{
			lock_guard<mutex> lock(mu_counter_);
			counter_++;
			unblock_one();
		}

	private:

		int acquire_id()
		{
			lock_guard<mutex> lock(mu_unblock_signal);
			assert(!unblock_signal_free_list.empty());
			int id = unblock_signal_free_list.front();
			unblock_signal_free_list.pop();
			blocked_ids.insert(id);
			unblock_signal[id] = false;
			if (g_verbose) cout << "acquired " << id << endl;
			return id;
		}

		void release_id(int id)
		{
			lock_guard<mutex> lock(mu_unblock_signal);
			assert(unblock_signal[id]);
			unblock_signal_free_list.push(id);
			if (g_verbose) cout << "released " << id << endl;
		}

		void unblock_one()
		{
			lock_guard<mutex> lock(mu_unblock_signal);
			if (!blocked_ids.empty())
			{
				auto it = blocked_ids.begin();
				int id = *it;
				blocked_ids.erase(it);
				unblock_signal[id] = true;
				counter_--;	// only call this if mu_counter_ is already acquired!
			}
		}

		int n_;
		int max_threads_;
		atomic<int> counter_;
		mutex mu_counter_;
		mutex mu_unblock_signal;
		unique_ptr<atomic<bool>[]> unblock_signal;
		queue<int> unblock_signal_free_list;
		set<int> blocked_ids;
	};
}
namespace impl_1 = impl_clumsy_1;

int test_op(int j)
{
	return (int) log(float(1+j));
}

template<typename Sem>
void run_test(int n_threads, int n_loops, int n_ops, int sem_count)
{
	auto start = std::chrono::system_clock::now();

	Sem sem(sem_count, n_threads);
	auto thread_func = [n_loops, n_ops, &sem]()
	{
		for (int i=0; i<n_loops; i++)
		{
			int acq = sem.acquire();
			int accum = 0;
			for (int j=0; j<n_ops; j++)
			{
				accum += test_op(j);
			}
			sem.release(acq);
		}
	};

	vector<thread> threads;
	for (int i=0; i<n_threads; i++)
	{
		threads.push_back(thread(thread_func));
	}

	for (auto& t: threads)
	{
		t.join();
	}

	auto end = std::chrono::system_clock::now();
	auto elapsed =  std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
	std::cout << elapsed.count() << " millis \n";
}

template<typename Sem>
void run_test(const po::variables_map& vm)
{
	run_test<Sem>(vm["threads"].as<int>(), vm["loops"].as<int>(),
								vm["ops"].as<int>(), vm["sem"].as<int>());
}

po::variables_map handle_cmdline_options(int argc, const char** argv)
{
	po::options_description desc("Allowed options");
	desc.add_options()
	    ("help,h", "produce help message")
	    ("threads,t", po::value<int>()->default_value(1000), "set thread count")
			("loops,l", po::value<int>()->default_value(100), "set loop count in each thread")
			("ops,o", po::value<int>()->default_value(1000), "set operation count in each loop iteration")
			("sem,s", po::value<int>()->default_value(50), "set the semaphore's counter")
			("impl,i", po::value<int>()->default_value(0), "set the semaphore implementation")
	    ("verbose,v", po::bool_switch(&g_verbose), "enable verbose mode")
	;

	po::variables_map vm;
	po::store(po::parse_command_line(argc, argv, desc), vm);
	po::notify(vm);

	if (vm.count("help")) {
		cout << desc << "\n";
  }

	return vm;
}

int main(int argc, const char** argv)
{
	auto vm = handle_cmdline_options(argc, argv);
	if (vm.count("help")) return 0;

	switch(vm["impl"].as<int>())
	{
		case 2:
			run_test<impl_2::Semaphore>(vm); break;
		case 3:
			run_test<impl_3::Semaphore>(vm); break;
		default:
			run_test<impl_1::Semaphore>(vm); break;
	}
	return 0;
}