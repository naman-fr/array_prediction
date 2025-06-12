#include <bits/stdc++.h>
using namespace std;
int main(){

    int T;
    cin>>T;
    while(T--){
        int n,k;
        cin>>n>>k;
        string s;
        s.append(k,'1');
        s.append(n-k,'0');
        int c1=0,c2=0;
        for(int i=0;i+2<n;i++)
            if(s[i]=='1'&&s[i+1]=='0'&&s[i+2]=='1') c1++;
        for(int i=0;i+2<n;i++)
            if(s[i]=='0'&&s[i+1]=='1'&&s[i+2]=='0') c2++;
        cout<<s<<"\n";
    }
    return 0;
}
