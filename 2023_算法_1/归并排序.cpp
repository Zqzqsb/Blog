#include<iostream>
using namespace std;

const int N = 1e6;
int a[N];

void MergeSort(int a[] , int start , int end)
{
    if(start >= end) // 终止条件
        return;

    // 分割区间
    int mid = (start + end) / 2; 
    MergeSort(a , start , mid);
    MergeSort(a , mid+1 , end);

    // 在运行到这一步时 start-mid , mid+1 - end 分别为两段有序序列
    int t[end - start+1] , i = 0; // 临时数组和插入位置指针
    int l = start , r = mid+1; // 左右子数组中的指针

    // 合并
    while(l <= mid && r <= end) 
        t[i++] = a[l] < a[r] ? a[l++] : a[r++];
    while(l <= mid)
        t[i++] = a[l++];
    while(r <= end)
        t[i++] = a[r++];

    // 将临时数组的内容写回原数组
    for(i = 0 ; i < end-start+1 ; i++) 
    {
        a[start + i] =  t[i];
    }
}

int main()
{
    int n; cin >> n;
    for(int i = 0 ; i < n ; i++) cin >> a[i];
    MergeSort(a , 0 , n-1);
    for(int i = 0 ; i < n ; i++) cout << a[i] << " ";
}