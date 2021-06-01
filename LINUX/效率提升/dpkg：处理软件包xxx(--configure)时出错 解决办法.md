1. 第一步：备份
```shell
sudo mv /var/lib/dpkg/info /var/lib/dpkg/info.bk
```
2. 第二步：新建
```shell
sudo mkdir /var/lib/dpkg/info
```
3. 第三步：更新
```shell
sudo apt-get update
sudo apt-get -f install
```

4. 第四步：替换
```shell
sudo mv /var/lib/dpkg/info/* /var/lib/dpkg/info.bk # 把更新的文件替换到备份文件夹
```
5. 第五步：删除
```shell
sudo rm -rf /var/lib/dpkg/info # 把自己新建的info文件夹删掉
```
6. 第六步：还原
```shell
sudo mv /var/lib/dpkg/info.bk /var/lib/dpkg/info    # 把备份的info.bk还原
```
