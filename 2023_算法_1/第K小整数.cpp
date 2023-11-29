#include<algorithm>
#include<iostream>
using namespace std;

const int N = 1e7;
int a[N];

int main()
{
    int n , k; cin >> n >> k;
    for(int i = 0 ; i < n ; i++)
        cin >> a[i];
    sort(a  , a+n);
    int* res = unique(a , a+n);
    int split = res - a;
    if(split < k) cout << "NO result" << endl;
    else cout << a[k-1];
}