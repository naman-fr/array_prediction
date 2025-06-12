#include <bits/stdc++.h>
using namespace std;
using ull = unsigned long long;
using i128 = __int128_t;

ull initBeauty(const vector<ull>& a) {
    ull b = 0;
    for (auto x : a) b += __builtin_popcountll(x);
    return b;
}

void genCostsFor(ull v, ull k, vector<ull>& c) {
    ull cur = v;
    while (true) {
        int p = __builtin_ctzll(~cur);
        if (p >= 63) break;
        ull cost = 1ULL << p;
        if (cost > k) break;
        c.push_back(cost);
        cur += cost;
    }
}

ull solveCase(int n, ull k, vector<ull>& a) {
    ull b = initBeauty(a);
    vector<ull> c;
    c.reserve(n * 64);
    for (auto& x : a) genCostsFor(x, k, c);
    sort(c.begin(), c.end());
    i128 used = 0;
    ull gain = 0;
    for (auto& cost : c) {
        if (used + cost > (i128)k) break;
        used += cost;
        gain++;
    }
    return b + gain;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;
    while (t--) {
        int n;
        ull k;
        cin >> n >> k;
        vector<ull> a(n);
        for (int i = 0; i < n; i++) cin >> a[i];
        cout << solveCase(n, k, a) << '\n';
    }
    return 0;
}
