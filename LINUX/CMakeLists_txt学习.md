&emsp;&emsp;书写一个完备的 **`CMakeLists.txt`** 文件，满足一般 **项目的基础构建要求**。
+ 自定义 **编译控制开关** ，自定义 **编译变量**，控制 **编译过程**。
+ 根据不同编译类型配置不同的 **编译选项** 和 **链接选项**
+ 添加 **头文件路径**、**编译宏** 等常规操作
+ 编译生成不同类型的 **目标文件**，包括 **可执行文件**、**静态链接库** 和 **动态链接库**
+ **安装**、**打包** 和 **测试**

# 1. 基础配置
## 1.1 设置项目版本和生成 `version.h`
&emsp;&emsp;项目需要配置一个 **版本号**，以便版本的发布。通过 **`project`** 命令配置项目信息：
```shell
project(CMakeTemplate VERSION 1.0.0 LANGUAGES C CXX)
```
第一个字段是项目名称，通过 `VERSION` 指定特定版本号。
## 1.2 指定编程语言版本
&emsp;&emsp;为了在不同机器上编译更加统一，最好指定语言的版本，比如声明 C 使用 c99 标准，C++ 使用 c++11 标准。
```shell
set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 11)
```

**内置变量**：以 **`CMAKE_`** 开头，用于配置 CMake 的构建行为。

## 1.3 配置编译选项
```shell
add_compile_option(-Wall -Wextra -pedantic -Werror)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -pipe -std=c99")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pipe -std=c++11")
```
## 1.4 配置编译类型
&emsp;&emsp;通过设置变量 **`CMAKE_BUILD_TYPE`** 来配置编译类型，可设置为 **`Debug`**、**`Release`**、**`RelWith`**、**`DebInfo`**、**`MinSizeRel`** 等。

```shell
set(CMAKE_BUILD_TYPE Debug)
```
&emsp;&emsp;更好的方式是在执行 **`cmake`** 命令的时候通过参数 **`-D`** 指定：
```shell
cmake -B build -DCMAKE_BUILD_TYPE=Debug
```
&emsp;&emsp;可以针对不同的编译类型设置不同的编译选项，比如对于 Debug 版本，开启调试信息，不进行代码优化：
```shell
set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -g -O0")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_RELEASE} -O2")
```
## 1.5 添加全局宏定义
&emsp;&emsp;在源码中，通过判断不同的宏定义，实现相应的代码逻辑：
```shell
add_definitions(-DDBUG -DREAL_COOL_ENGINEER)
```

## 1.6 添加 `include 目录`
&emsp;&emsp;设置头文件的搜索目录
```shell
include_directories(src/c)
```
# 2. 编译目标文件
&emsp;&emsp;编译目标的类型：**静态库**、**动态库** 和 **可执行文件**。
&emsp;&emsp;编写 CMakeList.txt 主要包括两步：
+ **编译**：确定编译目标所需要的源文件
+ **链接**：确定链接的时候，需要依赖的库

下面以开源项目来演示，项目的目录结构如下：

```shell
./cmake-template
├── CMakeLists.txt
├── src
│   └── c
│       ├── cmake_template_version.h
│       ├── cmake_template_version.h.in
│       ├── main.c
│       └── math
│           ├── add.c
│           ├── add.h
│           ├── minus.c
│           └── minus.h
└── test
    └── c
        ├── test_add.c
        └── test_minus.c
```
项目的构建任务：
+ 将 `math` 目录编译成 **静态库**，命名为 `math`
+ 编译 `main.c` 为 **可执行文件** `demo`，**依赖** `math` 静态库
+ 编译 `test` 目录下的 **测试** 程序，可以 **通过命令执行所有的测试**
+ 支持 **通过命令将编译产物 安装 及 打包**

## 2.1 编译静态库
&emsp;&emsp;项目目录路径 **`src/c/math`** 下的源文件编译为静态库，那么需要获取编译此静态库需要的 **文件列表**，可以使用 **`set`** 命令，或者 **`file`** 命令来进行设置。例如：
```shell
file(GLOB_RECURSE MATH_LIB_SRC src/c/math/*.c) # 获取源文件的文件列表，赋值给变量 MATH_LIB_SRC
        # GLOB_RECURSE <variable> [FOLLOW_SYMLINKS]
        # [LIST_DIRECTORIES true|false] [RELATIVE <path>] [CONFIGURE_DEPENDS]
        # [<globbing-expressions>...]
        # Generate a list of files that match the <globbing-expressions> and
        # store it into the <variable>.
add_library(math STATIC ${MATH_LIB_SRC}) # 添加目标库，并命名为 math
        # add_library(<name> [STATIC | SHARED | MODULE]
        #             [EXCLUDE_FROM_ALL]
        #             [<source>...])
        # Adds a library target called <name> to be build from the source files listed int the command invocation.
        # The <name> corresponds to the logical target name and must be globally unique within a project
        # The actual file name of the library built is constructed based on conventionss of the native platform
```
+ 使用 **`file`** 命令获取 `/src/c/math` 目录下 `所有的 *.c 文件`
+ 通过 **`add_library`** 命令编译名为 `math` 的静态库
    + 库名：`math`
    + **库的类型**： `STATIC` （如果为 `SHARED` 则编译的就是动态链接库)
## 2.2 编译可执行文件
&emsp;&emsp;通过 **`add_executable`** 命令来往 **构建系统** 中添加一个 **可执行构建目标**，需要指定编译需要的 **源文件**。
&emsp;&emsp;但对于 **可执行文件** 来说，有时候还会需要依赖其它的库，则需要使用 **`target_link_libraries`** 命令来声明构建此可执行文件需要 **链接** 的库。


```shell
add_executable(demo src/c/main.c)   # 可执行文件，名为 demo
    # add_executable(<name> [WIN32] [MACORX_BUNDLE]
    #                [EXCLUDE_FROM_ALL]
    #                [source1] [source2 ...])
    # Adds an executable target called <name> to be built from the source files
    # listed in the command invocation.
target_link_libraries(demo math)    # 为 可执行文件 demo 添加 依赖库 math
    # target_link_libraries(<target> ... <item>... ...)
    # Specify libraries of flags to use when linking a given target and/or its dependents.
    # The named <target> must have been created by a command such as add_executable() or add_library().
    # Each <item> may be:
    #   A library target name: The generated link line will have the full path to the linkable library file associated with the target.
    #   A full path to a library file: The generated link line will normally preserve the full path to the file.
```


+ 第一行，说明编译可执行文件 `demo` **需要的源文件**（可以指定多个源文件，此处只是以单个文件作为示例）；
+ 第二行，为 **可执行文件 `demo`** 添加 **依赖库 `math`**

此时可以在项目的根目录下执行构建和编译命令，并执行 `demo`：
```shell
# cmake -B cmake-build
# cmake --build cmake-build
# ./cmake-build/demo
Hello CMake!
10 + 24 = 34
40 - 96 = -56
```
# 3. 安装和打包
## 3.1 安装
&emsp;&emsp;指定当前项目在执行安装时，需要安装什么内容：
+ 通过 `install 命令` 来说明需要 **安装的内容** 和 **目标路径**
+ 通过设置 CMAKE_INSTALL_PREFIX 变量说明安装的路径

`3.15` 往后的版本可以使用 `cmake --install --prefix <install-path>` 覆盖指定安装路径：
```shell
install(TARGETS math demo
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)
    # install(TARGETS targets ... [EXPORT <export-name>]
    #         [[ARCHIVE | LIBRARY | RUNTIME | OBJECTS | FRAMEWORK | BUNDLE |
    #         PRIVATE_HEADER | PUBLIC_HEADER | RESOURCE]
    #         [destination <dir>
    #         [PERMISSIONS persissions...]
    #         [configurations [Debug | Release | ...]]
    #         [COMPONENT <component>]
    #         [NAMELINK_COMPONENT <component>]
    #         [OPTIONAL] [EXCLUDE_FROM_ALL]
    #         [NAMELINK_ONLY | NAMELINK_SKIP]
    #         [...]
    #         [INCLUDES DESTINATION [<dir> ...]]]]
    #         )
```
+ `TARGETS` 指定需要安装的 **目标列表**
+ `RUNTIME DESTINATION`：**可执行文件** 应该安装到安装目录的子目录
+ `LIBRARY DESTINATION`： **库文件** 应该安装到目录的子目录
+ `ARCHIVE DESTINATION`： **归档文件** 应该安装到目录的子目录

&emsp;&emsp;如果指定 `CMAKE_INSTALL_PREFIX` 为 `/usr/local`(不同系统有不同的默认值)，那么
+ `math` 库将会被安装到路径 `/usr/local/lib` 目录下
+ `demo` 可执行文件则在 `/usr/local/bin` 目录下

&emsp;&emsp;也可以使用 `install` 命令安装头文件
```shell
file(GLOB_RECURSE MATH_LIB_HEADER src/c/math/*.h)
install(FILES ${MATH_LIB_HEADERS} DESTINATION include/math)
```

&emsp;&emsp;如果要安装到当前项目的 output 文件夹下，可以执行
```shell
# cmake -B cmake-build -DCMAKE_INSTALL_PREFIX=./output
# cmake --build cmake-build
# cd cmake-build && make install && cd -
install the porject...
--install configuration: ""
--installing:.../cmake-template/output/lib/libmath.a
--installing:.../gitee/cmake-template/output/bin/demo
--installing:.../gitee/cmake-template/output/include/math/add.h
--installing:.../gitee/cmake-template/output/include/math/minus.h
```
&emsp;&emsp;可以看到安装了前面 `install 命令` 指定要安装的目录，并且 **不同类型的目标文件安装到不同的子目录。**
## 3.2 打包
&emsp;&emsp;执行 `include(CPack)` 启用相关的功能，在执行构建编译之后使用 `cpack 命令行工具` 进行打包安装。
&emsp;&emsp;打包的内容就是 `install 命令安装` 的内容，关键需要设置的变量有：

```shell
CPACK_GENERATOR             打包使用的压缩工具
CPACK_OUTPUT_FILE_PREFIX    打包安装的路径前缀
CPACK_INSTALL_PREFIX        打包压缩包内部目录前缀
CPACK_PACKAGE_FILE_NAME
```

例如：

```shell
include(CPack)
set(CPACK_GENERATOR "ZIP")
set(CPACK_PACKAGE_NAME "CMakeTemplate")
set(CPACK_SET_DESTDIR ON)
set(CPACK_INSTALL_PREFIX "")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
```

&emsp;&emsp;如果 `CPACK_OUTPUT_FILE_PREFIX` 设置为 `/usr/local/package`， `CPACK_INSTALL_PREFIX` 设置为 `real/cool/engineer`，`CPACK_PACKAGE_FILE_NAME` 设置为 `CMakeTemplate-1.0.0`，那么执行打包文件的生成路径为
```shell
/usr/local/package/CMakeTemplate-1.0.0.zip
```
&emsp;&emsp;此时，重新执行构建，使用 cpack 命令执行打包：
```shell
# cmake -B cmake-build -DCPACK_OUTPUT_FILE_PREFIX=`pwd`/output
# cmake --build cmake-build
# cd cmake-build && cpack && cd -
CPack:Create package using ZIP
CPack:install projects
CPack:-Run preinstall target for: CMakeTemplate
CPack:-Install project:CMakeTemplate
CPack:Create package
CPack:-package: /Users/Farmer/gitee/cmake-template/output/CMakeTemplate-1.0.0-Darwin.zip generated.
```
# 4. 测试
&emsp;&emsp;`CMake` 的测试功能使用起来有几个步骤：
1. 启用测试功能：`CMakeLists.txt` 中通过命令 `enable_testing()` 或者 `include(CTest)` 启用测试功能
2. 添加测试样例，指定测试名称和测试命令、参数
3. 构建编译完成后，使用 `ctest` 命令行工具运行测试

为了控制是否开启测试，可使用 option 命令设置一个开关，在开关打开时才进行测试，比如：
```shell
option(CMAKE_TEMPLATE_ENABLE_TEST "Whether to enable unit tests" ON)
if (CMAKE_TEMPLATE_ENABLE_TEST)
    message(STATUS "Unit tests enabled")
    enable_testing()
endif
```
## 4.1 编写测试程序
在示例代码中，针对 add.c 和 minus.c 实现了两个测试程序，如 test_add.c 的代码为：
```C++
#include<stdio.h>
#include<stdlib.h>
#include "math/add.h"

int main(int argc, char* argv[]) {
    if(argc != 4) {
        printf("Usage: test_add v1 v2 expected\n");
        return 1;
    }

    int x = atoi(argv[1]);
    int y = atoi(argv[2]);
    int expected = atoi(argv[3]);
    int res = add_int(x, y);

    if(res != expected) {
        return 1;
    }
    else {
        return 0;   # 对于测试程序，返回零，测试成功；否则，返回非零
    }
}
```
## 4.2 添加测试
使用 add_executable 命令生成测试程序，然后使用 add_test 命令添加单元测试：
```shell
add_executable(test_add test/c/test_add.c)
add_executable(test_minus test/c/test_minus.c)

target_link_libraries(test_add math)
target_link_libraries(test_minus math)

add_test(NAME test_add COMMAND test_add 10 24 34)
add_test(NAME test_minus COMMAND test_minus 40 96 -56)
```
## 4.3 执行测试
重新执行 cmake 命令更新构建系统，执行构建，再执行测试：
```shell
# cmake -B cmake-build
# cmake --build cmake-build
# cd cmake -build && ctest && cd -
Test project /Users/Farmer/gitee/cmake-template/cmake-build
    Start 1: test_add
1/2 Test #1: test_add .........................   Passed    0.00 sec
    Start 2: test_minus
2/2 Test #2: test_minus .......................   Passed    0.01 sec

100% tests passed, 0 tests failed out of 2
```
