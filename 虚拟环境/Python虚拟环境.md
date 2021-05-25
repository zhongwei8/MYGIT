# 1. 基于 `virtualenv`
1. 安装 `virtualenv` 包
```shell
pip install virtualenv
```
2. 创建虚拟运行环境
```shell
virtualenv my_venv_path
    # 如果不想使用系统的包，加上 --no-site-packages
```
3. 激活虚拟环境
```shell
source my_venv_path/bin/activate
```
4. 推出虚拟环境
```shell
deactivate
```
5. 删除虚拟环境
直接删除 `my_venv_path` 文件夹
6. 使用环境
进入环境后，一切操作和正常使用 python 一样。
# 2. 基于 virtualenvwrapper
&emsp;&emsp;`virtualenvwrapper` 是 `virtualenv` 的扩展包，用于更方便管理虚拟环境
+ 将所有虚拟环境整合到一个目录下
+ 管理(增、删、复)虚拟环境
+ 快速切换虚拟环境
1. 安装
```shell
pip install --user virtualenvwrapper
echo "source virtualenvwrapper.sh" >> ~/.bashrc
source ~/.bashrc
```
2. 创建虚拟环境
```shell
mkvirtualenv --python=python3.8 my_venv_path
```
3. 激活环境
```shell
workon  # 列出虚拟环境列表
workon [my_venv_path] # 切换虚拟环境
```
4. 退出环境
```shell
deactivate
```
5. 删除环境
```shell
rmvirtualenv my_venv_path
```
6. 其他有用指令
```shell
pip freeze # 查看当前安装库版本
pip freeze > requirements.txt # 当前安装库版本的所有包
pip install -r requirements.txt # 一键安装所有包

lsvirtualenv # 列举所有的环境
cdvirtualenv # 导航到当前激活的虚拟环境目录中，相当于 pushd 目录
cdsitepackages  # 导航到 site-packages 目录
lssitepackages # 显示 site-packages 目录中的内容
```
# 3 基于 `conda`
# 4 基于 `pipenv`
&emsp;&emsp;pipenv 是 Python 官方推荐的包管理工具。它综合了 virtualenv,pip 和 pyenv 三者的功能。能够自动为项目创建和管理虚拟环境。
&emsp;&emsp;pipenv 使用 Pipefile 和 Pipefile.lock 来管理依赖包，并且使用 pipenv 添加或删除包时，自动维护 Pipefile 文件，同时生成 pipefile.lock 来锁定安装包的版本和依赖信息，避免构建错误。相比 pip 需要手动维护 requirements.txt 中的安装包和版本，具有很大的进步。
1. 安装
```shell
pip install pipenv
```
2. 创建虚拟环境
```shell
cd my_project
pipenv install # 创建环境
pipenv install requests # 或者直接安装库
    # 如果不存在 pipfile，会生成一个 pipfile，并且如果有的库添加会自动编辑该文件，不需要我们手动更新 requirements.txt 文件。
```
3. 激活 `Pipenv Shell`
```shell
pipenv shell
python --version
```
