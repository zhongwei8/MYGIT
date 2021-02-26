import click

@click.command()
@click.option('--dir')          # 可选参数，默认为 None
@click.argument('file-path')    # 必需参数
@click.option('--sum/--no-sum', 
              default = False)  # 开关参数
@click.option('--shout',
              is_flag = True,
              default = False)  # 布尔参数，双划线
@click.option(
  '-c', '--check',
  is_flag = True,
  default = False)              # 布尔参数，单划线
@click.option('-s', '--string') # 单划线，参数，并给出全名

def info(dir, file_path, sum, shout, check, string):
  click.echo(f'dir, file_path = {dir}, {file_path}')
  click.echo(f'sum = {sum}')
  click.echo(f'shout = {shout}')
  click.echo(f'string = {string}')

if __name__ == '__main__':
  info()