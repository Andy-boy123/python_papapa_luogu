import requests
from bs4 import BeautifulSoup
import random
import os
import re
import time
import urllib.parse
import tkinter as tk
from tkinter import messagebox

# 洛谷的问题网址，题目URL结构为 https://www.luogu.com.cn/problem/problemID
# 洛谷的题解网址，题解URL结构为 https://www.luogu.com.cn/problem/solution/problemID

# 从浏览器中获取cookie
# 登录后更改cookie，否则无法爬取题解
cookie = {
    'login_referer': 'https%3A%2F%2Fwww.luogu.com.cn%2Fproblem%2FP1000',
    '_uid': '111884',
    '__client_id': '4f1bbbf98da6e49a6c98727320089c851c18d53c',
    'C3VK': 'aa6e71',
}


def Get_MD(html):
    bs = BeautifulSoup(html, "html.parser")

    # 当网页中没有article标签时，重试
    core = bs.select("article")[0]
    while not core:
        print("正在重试...")
        core = bs.select("article")[0]

    md = str(core)
    md = re.sub("<h1>", "# ", md)
    md = re.sub("<h2>", "## ", md)
    md = re.sub("<h3>", "#### ", md)
    md = re.sub("</?[a-zA-Z]+[^<>]*>", "", md)
    return md


def Get_TJ_MD(html):
    soup = BeautifulSoup(html, "html.parser")
    encoded_content_element = soup.find('script')
    # 获取script标签中的内容
    encoded_content = encoded_content_element.text
    # print(encoded_content)
    # 定位第一个"的位置，从当前开始截取
    start = encoded_content.find('"')
    # 定位第二个"的后面一个位置，到那里结束截取
    end = encoded_content.find('"', start + 1)
    # 截取出题解的内容
    encoded_content = encoded_content[start + 1:end]
    # 对encoded_content进行decodeURIComponent解码为html源码
    decoded_content = urllib.parse.unquote(encoded_content)
    # 转为utf-8
    decoded_content = decoded_content.encode('utf-8').decode('unicode_escape')
    # 从第一个"content":"后面开始截取
    start = decoded_content.find('"content":"')
    # 从第一个'","type":"题解"'前面结束截取
    end = decoded_content.find('","type":"题解"')
    # 截取出题解的内容
    decoded_content = decoded_content[start + 11:end]
    # 将截取的内容返回
    return decoded_content


# 创建标题获取函数，将problemID作为参数传入
def Get_Problem_title(problemID):
    # 生成要访问的url
    url = 'https://www.luogu.com.cn/problem/P' + str(problemID)
    print('----------- 正在爬取 ' + str(problemID) + ' ------------')
    # 从user_agents.txt里随机选择一行，作为本次请求的User-Agent
    with open('user_agents.txt', 'r') as f:
        lines = f.readlines()
        custom_user_agent = random.choice(lines).strip()
    # 设置请求头
    headers = {
        'User-Agent': custom_user_agent,
    }
    # 创建请求
    r = requests.get(url, headers=headers)

    # 获取网页内容
    soup = BeautifulSoup(r.text, 'html.parser')

    # 获取题目标题
    title = soup.find('title').text
    # 将题目取到标题中-前的部分
    title = title.split('-')[0]
    # 将题目末尾空格去掉
    title = title.strip()

    # 结束函数
    return title


def start_work(anum, bnum):
    bnum += 1
    # problemID为题目编号，从1000开始到9617结束
    for problemID in range(anum, bnum):

        # 为了防止被封IP，每爬取一个题目就随机休眠一段时间
        time.sleep(random.randint(1, 3))

        # 获取url 格式为 https://www.luogu.com.cn/problem/P+题目编号
        url = 'https://www.luogu.com.cn/problem/P' + str(problemID)

        # 调用函数，传入题目编号,获取题目标题
        title = Get_Problem_title(problemID)
        # 打印提示信息
        print('题目标题：' + str(title))
        # 打印提示信息
        print('正在爬取题目...')

        # 获取html
        # 从user_agents.txt里随机选择一行，作为本次请求的User-Agent
        with open('user_agents.txt', 'r') as f:
            lines = f.readlines()
            custom_user_agent = random.choice(lines).strip()
        # 设置请求头
        headers = {
            'User-Agent': custom_user_agent,
        }
        # 创建请求
        r = requests.get(url, headers=headers, cookies=cookie)
        # 获取网页内容
        html = r.text

        # 判断是否爬取成功
        if html == 'error':
            print('题目爬取失败！')

        else:
            print('已获取题目网页源码！')

            # 调用函数，传入html，获取题目MD文件
            problemMD = Get_MD(html)
            print("获取题目MD文件成功！")

            # 将题目编号-题目标题作为文件名
            filename = 'P' + str(problemID) + '-' + str(title) + '.md'
            # 在data目录下新建以题目编号-题目标题为名的文件夹
            # 判断文件夹是否存在
            if not os.path.exists('data/' + 'P' + str(problemID) + '-' + str(title)):
                os.mkdir('data/' + 'P' + str(problemID) + '-' + str(title))
                print('已创建文件夹：P' + str(problemID) + '-' + str(title))
            else:
                print('文件夹已存在，无需创建！')
            # 将文件保存到data目录下
            with open('data/' + 'P' + str(problemID) + '-' + str(title) + '/' + filename, 'w', encoding='utf-8') as f:
                f.write(problemMD)
            # 打印提示信息
            print('题目爬取成功！')

        # 开始爬取题解
        print("正在爬取题解...")

        # 获取题解url
        url = 'https://www.luogu.com.cn/problem/solution/P' + str(problemID)

        # 创建请求
        r = requests.get(url, headers=headers, cookies=cookie)
        # 获取网页内容
        html = r.text
        # 判断是否爬取成功
        if html == 'error':
            print("题解爬取失败！")
        else:
            print("已获取题解网页源码！")

            # 调用函数，传入html，获取题解MD文件
            solutionMD = Get_TJ_MD(html)
            print("获取题解MD文件成功！")

            # 将题目编号-题目标题-题解作为文件名
            filename = 'P' + str(problemID) + '-' + str(title) + '-题解.md'
            # 将文件保存到data/problemID-title目录下
            # print(solutionMD)
            with open('data/' + 'P' + str(problemID) + '-' + str(title) + '/' + filename, 'w', encoding='utf-8') as f:
                f.write(solutionMD)

            # 打印提示信息
            print('题解爬取成功！')

    # 打印提示信息
    print('\n')
    print('所有题目爬取完毕！')

    # 弹出提示框，并提示爬取成功题目的数量
    messagebox.showinfo(title='提示', message='所有题目爬取完毕！')


# 创建开始按钮，并绑定点击事件
def start_button_click():
    left_range = left_range_entry.get()
    right_range = right_range_entry.get()
    start_work(int(left_range), int(right_range))


# 创建函数，用于处理进入爬虫页面的操作
def enter_crawler_page():
    # 在这里执行进入爬虫页面的操作
    # 创建主窗口
    root = tk.Tk()
    root.title("爬虫GUI")

    # 设置窗口大小和位置
    root.geometry("1600x800")  # 设置宽度和高度

    # 创建一个 Frame 作为容器，使用 Grid 布局管理器
    frame = tk.Frame(root)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # 放置在页面中间

    # 创建标签
    label = tk.Label(frame, text="请输入要爬取的题目范围:")
    label.grid(row=0, column=0, columnspan=2)  # 使用 columnspan 来合并列

    # 创建左范围输入框
    left_range_entry = tk.Entry(frame)
    left_range_entry.grid(row=1, column=0, padx=10, pady=5)  # 使用 padx 和 pady 调整位置

    # 创建右范围输入框
    right_range_entry = tk.Entry(frame)
    right_range_entry.grid(row=2, column=0, padx=10, pady=5)  # 使用 padx 和 pady 调整位置

    # 创建开始按钮，并绑定点击事件
    start_button = tk.Button(frame, text="开始爬取", command=start_button_click)
    start_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)  # 使用 padx 和 pady 调整位置

    pass


# 在这里执行进入数据管理页面的操作
def enter_data_management_page():
    pass


# 主函数，程序的开始
if __name__ == '__main__':
    # 调用start_work函数，传入题目编号范围
    # start_work(1000, 1050)

    # 创建主窗口
    root = tk.Tk()
    root.title("爬虫GUI")

    # 设置窗口大小和位置
    root.geometry("800x400")  # 设置宽度和高度

    # 创建按钮，一个用于进入爬虫页面，另一个用于进入已获取数据管理页面
    crawler_button = tk.Button(root, text="进入爬虫页面", command=enter_crawler_page)
    data_management_button = tk.Button(root, text="进入数据管理页面", command=enter_data_management_page)

    # 布局按钮，使用 pack() 或 grid() 根据需要进行布局
    crawler_button.pack(pady=20)
    data_management_button.pack(pady=20)

    # 运行主循环
    root.mainloop()
