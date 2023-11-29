#include<iostream>
using namespace std;

const int N = 1e6;
int a[N];

void QuickSort(int a[] , int start , int end)
{
    if(start >= end) //终止条件
        return;
    int p = a[end]; // 分割点
    int i = start , j = start; // 快慢指针
    for( ; j < end ; j++) // 快指针前进搜索 start ~ end-1
    {
        if(a[j] <= p)
        {
            swap(a[i++] , a[j]); // 将小元素交换给慢指针
        }
    }
    swap(a[i] , a[end]); // 交换慢指针所在位置和分割点
    QuickSort(a , start , i-1); // 对两端区间分别做快排
    QuickSort(a , i+1 , end);
}

int main()
{
    int n; cin >> n;
    for(int i = 0 ; i < n ; i++) cin >> a[i];
    QuickSort(a , 0 , n-1);
    for(int i = 0 ; i < n ; i++) cout << a[i] << " ";
}