1. 更新编译器
```shell
sudo apt-get update
sudo apt-get install -y build-essential
```
2. 重新安装 `python3-apt`
```shell
sudo apt remove python3-apt
sudo apt autoremove
sudo apt autoclean
sudo apt install python3-apt
```
