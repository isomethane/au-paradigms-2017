#ifndef THREAD_POOL_H_
#define THREAD_POOL_H_

#include <pthread.h>
#include <queue>
#include <vector>

class ThreadPool;

struct Task {
    friend class ThreadPool;
public:
    void (*f)(void *);
    void *arg;
private:
    bool finished;
    pthread_mutex_t mutex;
    pthread_cond_t  cond;

public:
    Task();
    ~Task();
    Task(void (*f)(void *), void *arg);
    void wait();

private:
    Task(const Task &);
    Task & operator=(const Task &);
};

class ThreadPool {
private:
    std::vector<pthread_t> threads;
    std::queue<Task *> tasks;
    pthread_mutex_t queue_mutex;
    pthread_cond_t  queue_cond;
    bool to_finish, finished;
public:
    explicit ThreadPool(unsigned threads_nm);
    ~ThreadPool();
    void submit(Task *task);
    void finit();
private:
    static void * thread_lifecycle(void *arg);

private:
    ThreadPool(const ThreadPool &);
    ThreadPool & operator=(const ThreadPool &);
};

#endif
