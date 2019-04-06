#include "thread_pool.h"

#include <cassert>

Task::Task() : finished(false) {
    pthread_mutex_init(&mutex, nullptr);
    pthread_cond_init(&cond, nullptr);
}

Task::Task(void (*f)(void *), void *arg) : f(f), arg(arg), finished(false) {
    pthread_mutex_init(&mutex, nullptr);
    pthread_cond_init(&cond, nullptr);
}

Task::~Task() {
    pthread_mutex_destroy(&mutex);
    pthread_cond_destroy(&cond);
}

ThreadPool::ThreadPool(unsigned threads_nm) : threads(threads_nm), to_finish(false), finished(false) {
    pthread_mutex_init(&queue_mutex, nullptr);
    pthread_cond_init(&queue_cond, nullptr);
    for (auto &thread : threads)
        assert(pthread_create(&thread, nullptr, thread_lifecycle, this) == 0);
}

ThreadPool::~ThreadPool() {
    assert(finished);
    pthread_mutex_destroy(&queue_mutex);
    pthread_cond_destroy(&queue_cond);
}

void * ThreadPool::thread_lifecycle(void *arg) {
    ThreadPool *pool = (ThreadPool *)arg;
    while (true) {
        pthread_mutex_lock(&pool->queue_mutex);
        while (pool->tasks.empty() && !pool->to_finish)
            pthread_cond_wait(&pool->queue_cond, &pool->queue_mutex);

        if (pool->to_finish && pool->tasks.empty()) {
            pthread_mutex_unlock(&pool->queue_mutex);
            return nullptr;
        }
        Task *task = pool->tasks.front();
        pool->tasks.pop();
        pthread_mutex_unlock(&pool->queue_mutex);

        task->f(task->arg);
        pthread_mutex_lock(&task->mutex);
        task->finished = true;
        pthread_cond_broadcast(&task->cond);
        pthread_mutex_unlock(&task->mutex);
    }
}

void ThreadPool::submit(Task *task) {
    pthread_mutex_lock(&queue_mutex);
    tasks.push(task);
    pthread_cond_signal(&queue_cond);
    pthread_mutex_unlock(&queue_mutex);
}

void ThreadPool::finit() {
    pthread_mutex_lock(&queue_mutex);
    to_finish = true;
    pthread_cond_broadcast(&queue_cond);
    pthread_mutex_unlock(&queue_mutex);
    for (auto &thread : threads)
        assert(pthread_join(thread, nullptr) == 0);
    finished = true;
}

void Task::wait() {
    pthread_mutex_lock(&mutex);
    while (!finished)
        pthread_cond_wait(&cond, &mutex);
    pthread_mutex_unlock(&mutex);
}
