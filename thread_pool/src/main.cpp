#include "pqsort.h"

#include <cstdlib>
#include <vector>

int main(int argc, char *argv[]) {
    int threads_nm = atoi(argv[1]);
    int n = atoi(argv[2]);
    int depth = atoi(argv[3]);

    std::vector<int> v(n);
    srand(42);
    for (int i = 0; i < n; i++)
        v[i] = rand();
    pqsort(&v.front(), n, threads_nm, depth);

    return 0;
}
