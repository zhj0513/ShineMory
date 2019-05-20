import json
import sys
import argparse


parser = argparse.ArgumentParser()  # https://zhuanlan.zhihu.com/p/31274256
parser.add_argument('-v', '--value', nargs=2, type=int, help='the sum of 2 int')
args = parser.parse_args()  # 从命令行python xxxx xxx读取参数

f = open('f.json', 'w')
sys.stdout = f
a = {
    'masheng': 201526810212,
    'asdf': 'fads'
}
s = json.dumps(a)

if __name__ == '__main__':
    print(s)
    print('xxxxxx')

# 执行 python print_to_file.py xxx
# sys.argv 为['print_to_file.py', 'xxx'
