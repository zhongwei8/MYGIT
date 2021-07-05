# 1. [Python 方法解析顺序(MRO)](https://www.cnblogs.com/Cwj-XFH/p/13166808.html)
&emsp;&emsp;对于 python 的 **多继承** 情况，运行时在搜索对象的属性或方法时，需要遵循一定的顺序规则，这个规则称为：**Method Resolution Order(MRO)**.

&emsp;&emsp;MRO 规则可以总结为以下三句话：
1. In the multiple inheritance scenario, any specified attribute is searched first in the current class. If not found, the search continues into parent classes in **depth-first, left-right fashion without searching the same class twice**.
2. So, first it goes to super class(and its super classes) given first in the list then second super class(and its super classes), from left to right order. Then finally Object class, which is a super class for all classes.
-------------
这里的 list 指的是多个父类组成的 list，如：
```python
class M(X, Y, Z):
    pass
# list 就是 (X, Y, Z)
```
-------------
3. When in MRO we have a super class before subclass then it must be removed from that position in MRO.

-------------

这一句和第一句对应起来看，一个类只被检索一次，所以基类要往后移。

-------------

# 2. Python MRO 方法解析顺序详解
&emsp;&emsp;**方法解析顺序(MRO)**：当调用类方法或属性时，需要对当前类以及它的基类进行搜索，以确定方法和属性的位置，而搜索的顺序就称为方法解析顺序。
&emsp;&emsp;Python 的 MRO 经历了三种 MRO 算法：
1. **旧式类的MRO**：从左往右，采用深度优先搜索(DFS)的算法；
2. **新式类的MRO**：从 Python2.2 版本开始，新式类在采用深度优先搜索算法的基础上，对其进行了优化；
3. **C3算法**：自 Python2.3 版本，对新式类采用了 C3 算法。由于 Python3.x 仅支持新式类，所以该版本只使用 C3 算法。
## 2.1 旧式类 MRO 算法
在使用旧式类的 MRO 算法时，以下面代码为例(程序一)：
```python
class A:
    def method(self):
      print("CommonA")
class B(A):
    pass
class C(A):
    def method(self):
      print("CommonC")
class D(B, C):
    pass
print(D().method())
```
通过分析可以想到，此程序中的 4 个类是一个"菱形"继承的关系，当使用D类对象访问 method() 方法时，根据深度优先算法，搜索顺序为 `D->B->A->C->A` 。
因此，使用旧式类的 MRO 算法最先搜索得到的是基类 A 中的 method() 方法，即在 Python2.x 版本中，此程序的运行结果为：
```
CommonA
```
&emsp;&emsp;但是，这个结果显然不是我们想要的，我们希望搜索到的是 C 类中的 method() 方法。
## 2.2 新式类的 MRO 算法
&emsp;&emsp;为解决旧式类 MRO 算法存在的问题，Python2.2 版本推出了新的计算新式类 MRO 的方法，它仍然采用**从左往右的深度优先遍历，但是如果出现重复的类，只保留最后一个**。
&emsp;&emsp;仍以上面程序为例，通过深度优先遍历，其搜索顺序为 `D->B->A->C->A`，由于此顺序中有 2 个 A，因此仅保留最后一个，简化后得到的搜索顺序为 `D->B->C->A`。
&emsp;&emsp;可以看到，新式类 MRO 方法已经能够解决“菱形继承”的问题，但是可能违反**单调性原则**。所谓单调性原则，是指在类存在多继承时，子类不能改变基类的 MRO 搜索顺序，否则会导致程序发生异常。

例如，分析如下程序(程序二)：
```python
class X(object):
  pass
class Y(object):
  pass
class A(X,Y):
  pass
class B(Y,X):
  pass
class C(A, B):
  pass
```
通过深度优先顺序，得到的搜索顺序为`C->A->X->object->Y->object->B->Y->object->X->object`，简化(相同取后者)，得到 `C->A->B->Y->X->object`

&emsp;&emsp;分析这样的搜索顺序是否合理，我们来看下各个类中的 MRO：
+ 对于 A，其搜索顺序为：`A->X->Y-object`;
+ 对于 B，其搜索顺序为：`B->Y->X->object`;
+ 对于 C，其搜索顺序为：`C->A->B->X->Y->object`。

&emsp;&emsp;可以看到，B 和 C 中，X、Y 的搜索顺序是相反的，也就是说，当B 被继承时，它本身的搜索顺序发生了改变，这违反了单调性原则。
## 2.3 MRO C3
为解决 Python2.3 中 MRO 所存在的问题，Python2.3 采用了 C3 方法来确定方法解析顺序。多数情况下，如果某人提到Python 中的 MRO，指的都是 C3 算法。
1. 在 Python2.3 及后续版本中，运行程序一，得到如下结果：

```python
CommonC
```
2. 运行程序二，会得到如下异常
```python
Traceback (most recent call last):
  File "C:\Users\mengma\Desktop\demo.py", line 9, in <module>
    class C(A, B):
TypeError: Cannot create a consistent method resolution
order (MRO) for bases X, Y
```
3. C3 可以有效解决前面 2 中算法的问题。那么 C3 算法是怎样实现的呢？
以程序一为主，C3 把各个类的 MRO 记为如下等式：
+ 类 A： `L[A] = merge(A, object)`
+ 类 B：`L[B] = [B] + merge(L[A], [A])`
+ 类 C：`L[C] = [C] + merge(L[A], [A])`
+ 类 D：`L[D] = [D] + merge(L[A], L[B], [A], [B])`

注意，以类 A 等式为例
