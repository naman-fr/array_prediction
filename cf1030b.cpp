#include <bits/stdc++.h>
using namespace std;
int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int tt;
    if(!(cin >> tt)) tt = 1;
    while(tt--){
        int sz;
        cin >> sz;
        cout << 2*sz - 3 << '\n';
        int cur = 2;
        for(int i = 1; i < sz; ++i){
            cout << cur << ' ' << 1 << ' ' << i+1 << '\n';
            ++cur;
        }
        cur = 1;
        for(int i = 1; i < sz-1; ++i){
            cout << cur << ' ' << i+1 << ' ' << sz << '\n';
            ++cur;
        }
    }
    return 0;
}
