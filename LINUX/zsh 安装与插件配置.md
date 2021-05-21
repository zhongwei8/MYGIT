
1. 安装 `zsh` 和 `oh-My-Zsh`
```shell
sudo apt-get install zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```
2. [安装并配置 `powerlevel9k` 主题](https://www.thisfaner.com/p/powerlevel9k-zsh/)
```shell
# 1) 下载 powerlevel9k
git clone https://github.com/bhilburn/powerlevel9k.git ~/.oh-my-zsh/custom/themes/powerlevel9k
# 2) 配置 oh-my-zsh，修改 zsh 主题
# vim ~/.zshrc
ZSH_THEME="powerlevel9k/powerlevel9k"
```

3. 下载并安装 vscode
```shell
# 进入官网，下载 .deb 安装包：https://code.visualstudio.com/docs?dv=linux64
sudo dpkg -i 安装包名称
# sudo apt-get --fix-broken install 如果出现依赖问题，可以执行此命令
```

4. [安装 python3.8](https://www.cnblogs.com/daofaziran/p/12604726.html)
```shell
sudo apt-get install python3.8
# 建立软连接
sudo ln -fs /usr/bin/python3.8 /usr/bin/python3 # /usr/bin/python3 -> /usr/bin/python3.8
sudo ln -fs /usr/bin/python3.8 /usr/bin/python # /usr/bin/python -> /usr/bin/python3.8
sudo apt-get install python3-pip # 安装 pip
pip3 install --upgrade pip # 升级 pip
# 如果出现问题，使用命令：python3 -m pip install --upgrade pip

# which python
# whereis python
```
5 . [字体](https://blog.csdn.net/Fkylwj/article/details/97372301)

6. [更换 python 版本出现 ModuleNotFoundError: No module named 'apt_pkg'等错误](https://blog.csdn.net/starfish55555/article/details/93026394)
[更新 Python3.7 后出现ModuleNotFoundError: No module named 'apt_pkg'](https://www.jianshu.com/p/b7bdac560f7b)

7. [zsh 安装及优化](https://zhuanlan.zhihu.com/p/80487506)

8. [Ubuntu 16.04下安装zsh和oh-my-zsh
](https://www.cnblogs.com/EasonJim/p/7863099.html)
```shell
sudo apt-get install zsh
chsh -s /bin/zsh
sudo apt-get install apt
sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

sudo apt-get install autojump
vim .zshrc
# 在最后一行加上
. /usr/share/autojump/autojump.sh
source ~/.zshrc

git clone https://github.com/zsh-users/zsh-syntax-highlighting.git
echo "source ${(q-)PWD}/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" >> ${ZDOTDIR:-$HOME}/.zshrc

```
https://blog.csdn.net/lihaojia/article/details/111498800

9. [Ubuntu 下 Oh My Zsh 的最佳实践「安装及配置」](https://blog.csdn.net/weixin_34106122/article/details/91429490?utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-1.control&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-1.control)

https://www.thisfaner.com/p/powerlevel9k-zsh/



```shell
sudo update-alternatives --remove python /usr/bin/python2.7

update-alternatives --list python

sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7.1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.5.2
```
