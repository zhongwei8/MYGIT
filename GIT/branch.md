# 1. 查看分支
```git
git branch      # 查看本地分支
git remote -v   # 查看远程分支，包含远程分支的链接
git branch -a   # 查看本地分支和远程分支
git branch -vv  # 查看分支的详细信息
```
# 2 将远程仓库的指定分支拉取到本地
## 2.1 `checkout` 版
```git
git checkout -b local_branch_name origin/remote_branch_name
# 自动创建一个新的本地分支，并与指定的远程分支关联起来
```
## 2.2 `pull` 版
```git
git pull origin <remote_branch_name>:<local_branch_name>
# 将远程分支 remote_branch_name 拉取到本地分支 local_branch_name 上
```
# 3 推送到远程仓库
```git
git push origin <local_branch>:<remote_branch>
# 将当前本地分支推送到远程指定分支上
```
# 4 建立本地与远程的关联
## 4.1 push 版
```git
git push --set-upstream origin <local_branch>

// 简写方式
git push -u origin <local_branch>

```
## 4.2 branch 版
```git
git branch -set-upstream local_branch_name origin/remote_branch_name

git branch --set-upstream-to=origin/remote_branch_name local_branch_name
```
1. 场景：修改远程分支名称
```git
git branch -m oldName newName       # 1. 重命名本地分支
git push --delete origin oldName    # 2. 删除远程分支
git push origin newName             # 3. 上传新命名的本地分支
git branch --set-upstream-to origin/newName # 4. 把修改后的本地分支与远程分支关联
```
2. 场景：将新的本地分支推送到远程
```git
git push --set-upstream origin/remote_branch your_branch
```
3. 关联远程仓库
```git
git init                # 初始化本地仓库
git remote add origin git@github.com:zhongwei8/MYGIT.git    # 为本地仓库添加远程仓库名

git push --set-upstream origin master   # 将本地分支推送到远程分支
```

# 4. 从远程仓库获取
## 4.1 首次获取
```git
#克隆文件到本地仓库，此时克隆的远程仓库的 master 分支到本地仓库。
git clone git@github.com:zhongwei8/MYGIT.git
# 查看本地仓库和远程仓库的信息
git branch -a
# 克隆远程仓库的某个分支
git checkout -b local_branch origin/remote_branch
```
## 4.2 创建本地分支并切换
```git
git checkout -b local_branch
```
## 4.3 提交本地分支到远程仓库
```git
git push origin local_branch_name
```
## 4.4 创建本地分支与远程分支的关联
```git
git branch -set-upstream local_branch_name origin/remote_branch_name

```
