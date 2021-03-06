<!--
 * @Author: your name
 * @Date: 2021-03-06 12:38:55
 * @LastEditTime: 2021-03-06 14:48:46
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /my_github/创建文件/file_operation.md
-->
# 1. open

```python
f = open(name, mode, buffering) # 按照模式 mode 打开 name 文件
    # 'w': 写文件，已存在的同名文件被清空，不存在则创建一个
    # 'r': 读文件，不存在则报错
    # 'a': 在文件尾部添加内容，不存在则创建文件，存在则直接在尾部添加
    # 'wb': 写二进制文件
    # 'rb': 读取二进制文件

f.read([size])  # size 未指定则返回整个文件，如果文件大小 > 2 倍内存则有问题，读到文件末尾时返回 ""
f.readline()            # 返回一行
f.readlines([size])     # 返回包含 size 行的列表，size 未指定则返回全部行

for line in f: print(line)  # 通过迭代器访问

f.write('hello\n')          # 如果要写入字符串以外的数据，先将它转换为字符串

f.seek(偏移量, [起始位置])      # 移动文件指针，以字节为单位

f.tell()                        # 返回一个整数，表示当前文件指针相对于文件头的字节数

f.close()                       # 关闭文件
```

# 2. pathlib

```python
PurePath.parts
PurePath.drive
PurePath.root
PurePath.anchor

PurePath.parents
PurePath.parent
PurePath.name
PurePath.suffix
PurePath.suffixes
PurePath.stem

PurePath.is_absolute()
PurePath.is_relative_to(*other)
PurePath.match(pattern)
PurePath.relative_to(*other)


PurePath.with_name(name)
PurePath.with_stem(stem)
PurePath.with_suffix(suffix)

Path.stat()
Path.exists()   # os.path.exists(path), 判断目录是否存在

Path.glob(pattern)
Path.rglob(pattern)

Path.is_dir()
Path.is_file()

Path.iterdir()

Path.mkdir(mode=0o777, parents=False, exist_ok=False)
    # os.makedirs(path), 创建多级目录
    # os.mkdir(path), 创建单级目录
Path.touch(mode=0o666, exist_ok=True)

Path.open(mode='r', buffering=-1, encoding=None, errors=None, newline=None)
Path.read_text()    # 打开 Path 路径下的文件，以 str 格式读取文件内容，等同 open 操作的 'r' 格式
Path.write_text()   # 对 Path 路径下的文件进行写操作，等同 open 操作文件的 'w' 格式

Path.reanme(target)
Path.replace(target)
Path.issolve(strict=False)
```