#include "thread_pool.h"
#include "pqsort.h"

#include <deque>
#include <algorithm>
#include <cassert>

using std::size_t;
using std::deque;
using std::partition;

class QsortManager;

struct QsortData {
    int *l, *r;
    unsigned levels_left;
    QsortManager *qsort_manager;

    QsortData(int *l, int *r,
              unsigned levels_left,
              QsortManager *qsort_manager);
    QsortData(const QsortData *mother, int *l, int *r);
};

QsortData::QsortData(int *l, int *r,
                     unsigned levels_left,
                     QsortManager *qsort_manager) :
    l(l), r(r), levels_left(levels_left), qsort_manager(qsort_manager) {}

QsortData::QsortData(const QsortData *mother, int *l, int *r) :
    l(l), r(r), levels_left(mother->levels_left - 1), qsort_manager(mother->qsort_manager) {}

class QsortManager {
private:
    ThreadPool *pool;
    deque<Task> tasks;
    deque<QsortData> args;
    pthread_mutex_t deque_mutex;

public:
    explicit QsortManager(ThreadPool *pool);
    ~QsortManager();
    void push(const QsortData &data);
    void wait();
private:
    static void pqsort_step(void *arg);

private:
    QsortManager(const QsortManager &);
    QsortManager & operator=(const QsortManager &);
};

QsortManager::QsortManager(ThreadPool *pool) : pool(pool) {
    pthread_mutex_init(&deque_mutex, NULL);
}

QsortManager::~QsortManager() {
    pthread_mutex_destroy(&deque_mutex);
}

void QsortManager::push(const QsortData &data) {
    pthread_mutex_lock(&deque_mutex);
    args.push_back(data);
    tasks.emplace_back(pqsort_step, &args.back());
    pool->submit(&tasks.back());
    pthread_mutex_unlock(&deque_mutex);
}

void QsortManager::wait() {
    for (size_t i = 0; true; i++) {
        pthread_mutex_lock(&deque_mutex);
        if (i == tasks.size()) {
            pthread_mutex_unlock(&deque_mutex);
            return;
        }
        Task *task = &tasks[i];
        pthread_mutex_unlock(&deque_mutex);
        task->wait();
    }
}

void QsortManager::pqsort_step(void *arg) {
    QsortData *data = (QsortData *)arg;

    if (data->r - data->l <= 1)
        return;

    if (data->levels_left == 0) {
        std::sort(data->l, data->r);
        return;
    }

    int pivot = *data->l;
    auto left_bound =  partition(data->l, data->r,
                                 [pivot](int a) { return a < pivot; });
    auto right_bound = partition(left_bound, data->r,
                                 [pivot](int a) { return a <= pivot; });

    data->qsort_manager->push(QsortData(data, data->l, left_bound));
    data->qsort_manager->push(QsortData(data, right_bound, data->r));
}

void pqsort(int *arr, size_t n, unsigned threads_nm, unsigned depth) {
    ThreadPool pool(threads_nm);
    QsortManager qsort_manager(&pool);

    qsort_manager.push(QsortData(arr, arr + n, depth, &qsort_manager));
    qsort_manager.wait();

    assert(std::is_sorted(arr, arr + n));
    pool.finit();
}
