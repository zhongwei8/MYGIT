[ubantu 安装 python 虚拟环境——基于 virtualenvwrapper](https://blog.csdn.net/qq_769932247/article/details/112398650)
1. 安装 `virtualenv`
```shell
pip3 install virtualenv
```
2. 安装 `virtualenvwrapper`
```shell
pip3 install virtualenvwrapper
```
3. 配置 `~/.bashrc` 文件
```shell
# vim ~/.bashrc # 进入 ~/.bashrc 并在最后加入：
export WORKON_HOME=~/.virtualenvs # 指定虚拟环境存放目录：~/.virtualenvs (可自定义)
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3.8 # 指定 virtualenvwrapper 执行的 python 版本
export VIRTUALENVWRAPPER_VIRTUALENV=~/.local/bin/virtualenv # 指定 virtualenv 的路径
source ~/.local/bin/virtualenvwrapper.sh # virtualenvwrapper.sh 所在目录
```
4. 激活配置
```shell
source ~/.bashrc
```
5. 创建虚拟环境
```shell
mkvirtualenv venv3.8    # 使用刚刚配置过默认的 python3.8 版本创建
mkvirtualenv --python=/usr/bin/python3.8 venv3.8 # 指定虚拟环境的 python 版本创建，可以是日任意的 python 版本
```
6. 常使用的 `virtualenvwrapper` 命令
```shell
mkvirtualenv venv3.8    # 创建名为 venv3.8 的虚拟环境
workon venv3.8          # 切换到某个虚拟环境 venv3.8
deactivate              # 推出当前虚拟环境
rmvirtualenv venv3.8    # 删除某个虚拟环境
lsvirtualenv            # 列出所有虚拟环境
cdvirtualenv            # 进入到虚拟环境所在的目录
```
