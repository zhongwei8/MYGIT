# 1 [numpy 关于 copy 有三种情况](https://blog.csdn.net/u010099080/article/details/59111207)
+ 完全不复制
+ 视图(view)，或浅复制(shallow copy)
+ 深复制(deep copy)

# 2 切片
```python
b = a[:]    # 切片属于第二种，即视图；所有的切片操作返回的都是试图
# 具体来说，b = a[:]，会创建一个新的对象 b，(id(b) 和 id(a) 返回的结果是不一样的)，
# 但是 b 的数据完全来自于 a，和 a 保持完全一致。
# 换句话说，b 的数据完全由 a 保管，他们两个的数据变化是一致的

a = np.arange(4)
b = a[:]

b.flags.owndata # 返回 False，b 并不保管数据
a.flags.owndata # 返回 True， 数据由 a 保管

# a b 相互影响
a[-1] = 10
print(b)    # array([0, 1, 2, 10])

b[0] = 10
print(a)    # array([10, 1, 2, 10])
```
# 3 `b = a` 和 `b = a[:]` 的区别
+ `b = a`： 不创建新对象，`b` 和 `a` 是同一个对象
+ `b = a[:]`： 创建新对象 `b`，`b` 和 `a` 不是同一个对象

# 4 [深拷贝和浅拷贝](https://blog.csdn.net/hlg1995/article/details/80330628?utm_medium=distribute.pc_relevant.none-task-blog-baidujs_title-0&spm=1001.2101.3001.4242)
1. 浅拷贝：对一个对象的顶层拷贝；拷贝了引用，没有拷贝内容
2. 深拷贝：对一个对象所有层次的拷贝(递归)
3. 浅拷贝对不可变类型和可变类型的 copy 不同
