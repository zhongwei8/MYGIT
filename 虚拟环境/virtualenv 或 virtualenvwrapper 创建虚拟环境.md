[virtualenv 和 virtualenvwrapper 介绍、安装和使用](https://segmentfault.com/a/1190000012030061)
# 1. 基于 `virtualenv`
+ 不同应用开发环境独立
+ 环境升级不影响其他，也不影响全局 python 环境
+ 防止系统中出现包管理混乱和版本冲突
1. 安装 `virtualenv`
```shell
pip install virtualenv
```
2. 创建虚拟环境根目录
在创建虚拟环境前，请确保已安装目标版本的`python`，如 `python3.8`
```shell
virtualenv my_venv_path python3.8 # 创建目录 my_venv_path ，作为虚拟环境的根目录
                                  # 然后把 python3.8 原样拷贝过来
```
3. 激活虚拟环境
```shell
source my_venv_path/bin/activate # 每次需要使用虚拟环境时，都需要执行此命令，麻烦死了。
```
4. 在虚拟环境下安装 numpy
```shell
pip3 install numpy
```
5. 退出当前虚拟环境
```shell
deactivate
```
# 2. 基于 virtualenvwrapper
&emsp;&emsp;当只需要一个虚拟环境时，virtualenv 是足够的。当需要创建多个虚拟环境，且需要在其中来回切换时，virtualenv 就显得不太方便、整洁。
&emsp;&emsp;virtualenvwrapper 是为了统一管理多个虚拟环境而生的。它是 virtualenv 的拓展管理包，将多个虚拟环境统一到一个根目录下。具体来说就是在一个根目录下，创建多个文件夹，每个文件夹都是一个虚拟环境，切换文件夹就相当于切换虚拟环境。

1. 安装 `virtualenvwrapper` 包
```shell
pip install virtualenvwrapper
```
2. 设置 `WORK_HOME` 环境变量
3. 创建虚拟环境
```shell
mkvirtualenv --python=python_path test_vir
    # --python 用于指定已有的 python 安装路径：python_path
    # test_dir：创建的虚拟环境名称
```
`python_path`参数：**已有的 python 版本路径**。`virtualenvwrapper` **把安装在路径 `python_path` 下 `python` 版本，原样复制到虚拟环境中去**。就是说，你得保证 `python_path` 路径下已经有一个 `python` 版本。



安装之后，并不能直接使用，我们需要配置之后才能使用相关命令。
首先找到对应的 virtualenvwrapper.sh 文件的路径：
```shell
sudo find / -name virtualenvwrapper.sh
```
找到之后，在 ~/.bashrc 中进行配置
```shell
export WORKON_HOME=~/.virtualenvs
source /usr/bin/virtualenvwrapper.sh
```


4. 配置 `shell`
```shell
export WORKON_HOME=my_venv_path/virtualenvs # 将虚拟环境的根目录，加入到环境变量中去
source /usr/bin/virtualenvwrapper.sh        # 激活虚拟环境管理工具
# find / -name virtualenvwrapper.sh         # 用于找到虚拟环境管理工具的执行路径
```


```shell
mkvirtualenv [path_name]    # 创建虚拟环境
rmvirtualenv [path_name]    # 删除虚拟环境
workon [path_name]          # 激活虚拟环境
deactivate                  # 退出当前虚拟环境
workon                      # 列出所有环境，或者 lsvirtualenv -b
```

# 3. 基于 pipenv
&emsp;&emsp;`virtualenvwrapper` 管理多个虚拟环境时，已经够用，但存在两个问题：
+ 在不同的平台上使用 `virtualenvwrapper`，存在一定的差别。
+ `virtualenvwrapper` 在管理 `requirements.txt` 和处理包之间依赖关系上，不太完美。

pipenv 的特性：
+ 集成了 pip, virtualenv 两者的功能，且完善了两者的一些缺陷。
+ pipenv 使用 Pipfile 和 Pipfile.lock 管理包的依赖关系
+ 使用哈希校验，方便安装和卸载包
+ 加载 .env 文件简化开发流程
+ **在不同 python 版本间，不同操作系统上，做到了命令的一致(只有这一点，才是使用者能切实感受到的便利性)**


1. 安装 `pipenv` 包
```shell
pip install pipenv
```
2. 创建虚拟环境
```shell
cd my_project
pipenv install          # 创建环境
pipenv install pandas   # 安装包

# 如果不存在 pipfile 文件，则会自动生成一个 pipfile 文件，
# 并且将库添加到该文件中，不必我们手动更新 requirements.txt 文件。
```
3. 激活 `Pipenv Shell`
```shell
pipenv shell            # 激活虚拟环境
python --version
```
4. 其他命令
```shell
python -c "s='https://mirrors.aliyun.com/pypi/simple';fn='Pipfile';pat=r'(\[\[source\]\]\s*url\s*=\s*\")(.+?)(\")';import re;fp=open(fn, 'r+');ss=fp.read();fp.seek(0);fp.truncate();fp.write(re.sub(pat, r'\1{}\3'.format(s), ss));fp.close();print('Done! Pipfile source switch to:\n'+s)"
```


-----------------------------------
# 2. [基于 virtualenvwrapper](https://blog.csdn.net/qq_769932247/article/details/112398650)

1. 安装虚拟环境管理工具包 `virtualwrapper`
```shell
pip3 install virtualenvwrapper
```
2. 配置 `~/.bashrc` 文件
```shell
export WORKON_HOME=~/.virtualenvs   # 指定虚拟环境根目录，~/.virtualenvs 是默认值，也可自定义
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3.8 # 指定 virtualenvwrapper 执行的默认 python 版本
export VIRTUALENVWRAPPER_VIRTUALENV=~/.local/bin/virtualenv # 指定 virtualenv 的路径
source ~/.local/bin/virtualenvwrapper # virtualenvwrapper.sh 所在目录
```
3. 执行 `~/.bashrc` 文件
```shell
source ~/.bashrc
```
4. 创建虚拟环境
```shell
mkvirtualenv venv3.8    # 使用默认的 /usr/bin/python3.8 版本创建 venv3.8 虚拟环境
                        # export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3.8，用于设置默认 python 版本
mkvirtualenv --python=/usr/bin/python3.8 venv3.8 # 用指定的 python 版本，创建虚拟环境 venv3.8
                        # 与上行代码等价，它显式地指定了需要用的 python 版本，更极客一些，推荐使用此方式。

```
5. 切换虚拟环境
```shell
workon venv3.8
```
&emsp;&emsp;**切换到对应的虚拟环境后，就可以按照正常的方法使用了，在此虚拟环境执行的操作，如安装包、使用包、卸载包，都在此虚拟环境下执行，与系统环境无关。**

6. 退出当前虚拟环境
```shell
deactivate
```
&emsp;&emsp;退出虚拟环境后，就退回到了系统环境。
# 3. [Python虚拟环境和包管理工具 Pipenv 的使用详解](https://www.cnblogs.com/PyKK2019/p/10787289.html)
1. 安装 pipenv
```shell
pip install pipenv
# pipenv 可用于检验是否安装成功
```
2. 创建虚拟环境
```shell
cd my_myproject     # 首先，进入项目工程所在的目录，
pipenv install      # (在当前项目工程目录下)创建虚拟环境
```
如果当前目录下，没有 Pipfile 和 Pipfile.lock，则会自动生成。否则，自动安装 Pipfile 中的所有依赖。
+ Pipfile ：保存着各个依赖包的版本信息，可以修改 url 的值，以修改源信息。
+ Pipfile.lock ：保存着依赖包的锁信息
3. 在虚拟环境下安装第三方包
```shell
pipenv install pandas
```
这里执行了两步操作
+ 将包安装到虚拟环境中，更新 Pipfile 里面的依赖包
+ 使用 sha256 算法更新 pipfile.lock 文件
默认情况下会加锁，速度很慢，可以使用如下命令不加锁加快速度
```shell
pipenv install pandas --skip-lock
```
4. 卸载第三方包
```shell
pipenv uninstall pandas
```
常用选项
```shell
pipenv -venv # 显示虚拟环境实际文件路径
pipenv --py # 显示虚拟环境 python 解释器所在路径
pipenv --where  # 显示项目文件所在路径
pipenv --rm     # 删除虚拟环境
pipenv install xxx --skip-lock  # 安装第三方依赖，但不加锁，以加快速度
pipenv run xxx.py # 在虚拟环境中运行 python 程序
```


# 4. [Python之Pipenv使用](https://blog.csdn.net/haiyanggeng/article/details/82382993?utm_medium=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-1.control&depth_1-utm_source=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-1.control)
1. 安装 pipenv 包
```shell
pip install pipenv
```
2. 创建虚拟环境
```shell
pipenv --python 3.8    #
```
这在项目目录中创建两个新文件
+ Pipfile：该文件是 TOML 格式，存放当前虚拟环境的配置信息，包括 python 版本，pypi 源以及依赖包，pipenv 根据该文件寻找项目的根目录
+ Pipfile.lock：该文件是对 Pipfile 的锁定，支持锁定项目不同版本所依赖的环境
3. 进入和退出虚拟环境
```shell
pipenv shell    # 激活虚拟环境
exit            # 退出虚拟环境
```
4. 安装包
pipenv 支持开发环境和生产环境依赖的分离
pip install 有多重作用：
+ 如果虚拟环境已经存在，则安装 Pipfile 中的依赖包
+ 如果虚拟环境不存在，但 Pipfile 存在，则根据 Pipfile 中 python 版本创建虚拟环境并安装依赖包
+ 如果虚拟环境和 Pipfile 都不存在，则根据系统默认 python 版本创建虚拟环境

```shell
pipenv install
pipenv install --dev    # 安装开发环境依赖
pipenv install [package_name]   # 指定包名
pipenv install -r requirements.txt  #
```
