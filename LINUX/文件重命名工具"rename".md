# 1. 文件重新命名
```shell
rename 's/abc/A/g' *.txt    # 把所有 .txt 文件中的字串 "abc" 修改为 "A"
rename 's/ /_/' *           # 把所有文件中的空格字符，替换为下划线“_”
rename 's/^/a_/' *          # 在所有文件名中，添加前缀 "a_"
rename 'y/a-z/A-Z/' *       # 大写所有字母
rename 's/\.txt$//' *.txt   # 删除所有 txt 的文件后缀名
```
