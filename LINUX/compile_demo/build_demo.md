# 1. 静态链接库和动态链接库
## 1.1 静态链接库
&emsp;&emsp;Linux 下的静态链接库是以 `.a` 结尾的二进制文件，它作为程序的一个模块，在链接期间被组合到程序中。
## 1.2 动态链接库
&emsp;&emsp;以 `.so` 结尾的二进制文件，它在程序运行阶段被加载进内存。
## 1.3 静态链接库文件的命名规则
```linux
libxxx.a
```
其中，`xxx` 表示库的名字。例如， `libc.a`，`libm.a`，`libieee.a` 都是 Linux 自带的静态库。
# 2. GCC 生成静态链接库
## 2.1 使用 gcc 命令把源文件编译为目标文件，即 `.o` 文件
```linux
gcc -c 源文件列表   # -c 选项表示只编译，不链接，详见 GCC -c 选项
```
## 2.2 使用 ar 命令将 `.o` 文件打包成静态链接库
```linux
ar rcs + 静态库文件的名字 +目标文件列表
```
`ar` 是 `linux` 的一个备份压缩命令，它可以将多个文件打包成一个备份文件，也可以从备份文件提取成员文件。`ar` 命名最常见的用法是将目标文件打包为静态链接库

例如，下面将目标文件 `a.o`、`b.o`、`c.o` 打包成一个静态库文件 `libdemo.a`

```C
ar rcs libdemo.a a.o b.o c.o
```
# 3 示例
&emsp;&emsp;创建一个文件夹 test，将 test 文件夹作为整个项目的基础目录。在 test 文件夹下再创建四个源文件，分别是 `add.c`、`sub.c`、`div.c`、`test.h`
## 3.1 文件准备
1. add.c 实现两个数相加
```C++
#include "test.h"

int add(int a, int b) {
    return a + b;
}
```
2. sub.c 实现两个数相减
```C++
int sub(int a, int b) {
    return a - b;
}
```
3. div.c 实现两个数相除
```C++
int div(int a, int b) {
    return a / b;
}
```
4. 还有一个头文件，用来声明三个函数
```C++
#ifndef __TEST_H_
#define __TEST_H_

int add(int a, int b);
int sub(int a, int b);
int div(int a, int b);

#endif
```
## 3.2 将上述代码制作成静态链接库
1. 将所有源文件都编译成目标文件
```C
gcc -c *.c
```
&emsp;&emsp;`*c` 表示所有以 `.c` 结尾的文件，也即所有的源文件。执行完该命令后，会发现 test 目录下多了三个文件，分别是 `add.o`、`sub.o`、`div.o`。

2. 把所有目标文件打包成静态库文件：

```C
ar rcs libtest.a *.o
```

&emsp;&emsp;`*.o` 表示所有以 `.o` 结尾的文件，也即所有的目标文件。执行完该命令，发现 `test` 目录下多了一个静态库文件 `libtest.a`，大功告成。

3. 完整命令
```C
cd test
gcc -c *.c
ar rcs libtest.a *.o
```
4. GCC 使用静态链接库

&emsp;&emsp;使用静态链接库时，除了需要库文件本身，还需要对应的头文件
+ **库文件**包含了真正的函数代码，也即函数定义部分；
+ **头文件**包含了函数的调用方法，也即函数声明部分。

&emsp;&emsp;为了使用上面生成的静态链接库 `libtest.a` ，我们需要启用一个新的项目。创建一个 test 的兄弟目录 math，将 math 作为新项目的基础目录。

&emsp;&emsp;在比较规范的项目目录中
+ `lib` 文件夹一般用来存放**库文件**
+ `include` 文件夹一般用来存放**头文件**
+ `src` 文件夹一般用来存放**源文件**
+ `bin` 文件一般用来存放**可执行文件**。

&emsp;&emsp;为了规范，我们将前面生成的
+ `libtest.a` 放到 math 目录下的 lib 文件夹
+ `test.h` 放到 math 目录下的 include 文件夹
+ 在 `src` 中再创建一个 main.c 源文件
此时，math 目录中文件结构如下所示：

```C
|-- include
|  `-- test.h
|-- lib
|   `--libtest.a
`-- src
    `-- main.c
```
在 main.c 中，可以像下面这样使用 libtest.a 中的函数：
```C++
#include <stdio.h>
#include "test.h"  //必须引入头文件
int main(void)
{
    int m, n;
    printf("Input two numbers: ");
    scanf("%d %d", &m, &n);
    printf("%d+%d=%d\n", m, n, add(m, n));
    printf("%d-%d=%d\n", m, n, sub(m, n));
    printf("%d÷%d=%d\n", m, n, div(m, n));
    return 0;
}
```
编译 main.c 的时候，我们需要使用 `-I`(大写的字母 `i`)，选项指明**头文件**的包含路径，使用 `-L` 选项指明**静态库**的包含路径，使用 `-l` (小写)选项指明 **静态库的名字**。所以，`main.c` 的完整编译命令为：
```C
gcc src/main.c -I include/ -L lib/ -l test -o main.out
```
打开 `math` 目录，发现多了一个 `math.out` 可执行文件，使用 `./math.out` 命令可以运行 `math.out` 进行数学计算。
完整的使用命令如下：
```C
cd math
gcc src/main.c -I include/ -L lib/ -l test -o math.out
```
