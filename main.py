import requests
from bs4 import BeautifulSoup
import random
import os
import re
import time
import urllib.parse
import tkinter as tk
from tkinter import messagebox
import json
import jsonpath

# difficultty = {'入门':'1','普及-':'2','普及/提高-':'3','普及+/提高':'4','提高+/省选-':'5','省选/NOI-':'6','NOI/NOI+/CTSC':'7','尚无评定':'9'}

# 洛谷的问题网址，题目URL结构为 https://www.luogu.com.cn/problem/problemID
# 洛谷的题解网址，题解URL结构为 https://www.luogu.com.cn/problem/solution/problemID
# 洛谷的题目列表网址，题目列表URL结构为 https://www.luogu.com.cn/problem/list?page=pagenum

# json数据结构为题号-题目标题-标签-难度
# info.json为题目列表，格式为json，里面有题号，题目标题，标签，难度
# user_agents.txt为User-Agent列表，用于随机选择User-Agent
# 文件夹格式为题号-题目标题，目录下有题目和题解两个MD文件


# 请从浏览器中获取cookie
# 登录后更改cookie，否则无法爬取题解
cookie = {
    'login_referer': 'https%3A%2F%2Fwww.luogu.com.cn%2Fproblem%2FP1000',
    '_uid': '111884',
    '__client_id': '4f1bbbf98da6e49a6c98727320089c851c18d53c',
    'C3VK': 'aa6e71',
}


# 获取json格式的数据包
def Get_info():
    headers = {
        "authority": "www.luogu.com.cn",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua": "\"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Google Chrome\";v=\"116\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Cookie": "__client_id=a0306231cd05f9a814ca1bdf95c050400268bedf; _uid=0",
    }
    tag_url = 'https://www.luogu.com.cn/_lfe/tags'
    tag_html = requests.get(url=tag_url, headers=headers).json()
    tags_dicts = []
    tags_tag = list(jsonpath.jsonpath(tag_html, '$.tags')[0])
    for tag in tags_tag:
        if jsonpath.jsonpath(tag, '$.type')[0] == 1 or jsonpath.jsonpath(tag, '$.type')[0] == 4 or \
                jsonpath.jsonpath(tag, '$.type')[0] == 3:
            tags_dicts.append({'id': jsonpath.jsonpath(tag, '$.id')[0], 'name': jsonpath.jsonpath(tag, '$.name')[0]})

    arr = ['暂无评定', '入门', '普及−', '普及/提高−', '普及+/提高', '提高+/省选−', '省选/NOI−', 'NOI/NOI+/CTSC']
    ts = []
    # for page in range(1, 179):
    page = 1
    url = f'https://www.luogu.com.cn/problem/list?page={page}'
    html = requests.get(url=url, headers=headers).text
    urlParse = re.findall('decodeURIComponent\((.*?)\)\)', html)[0]
    htmlParse = json.loads(urllib.parse.unquote(urlParse)[1:-1])
    result = list(jsonpath.jsonpath(htmlParse, '$.currentData.problems.result')[0])
    for res in result:
        pid = jsonpath.jsonpath(res, '$.pid')[0]
        title = jsonpath.jsonpath(res, '$.title')[0]
        difficulty = arr[int(jsonpath.jsonpath(res, '$.difficulty')[0])]
        tags_s = list(jsonpath.jsonpath(res, '$.tags')[0])
        tags = []
        for ta in tags_s:
            for tags_dict in tags_dicts:
                if tags_dict.get('id') == ta:
                    tags.append(tags_dict.get('name'))
        wen = {
            "题号": pid,
            "题目": title,
            "标签": tags,
            "难度": difficulty
        }
        ts.append(wen)
    # 显示第几页已经保存
    print(f'第{page}页已经保存')
    # 将数据写入JSON文件
    with open('info.json', 'w', encoding='utf-8') as f:
        json.dump(ts, f, ensure_ascii=False, indent=4)


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
    # 开始爬取info pagenum从1到178
    print("正在爬取info...")
    Get_info()
    print("info爬取成功！")
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


# 创建函数，用于切换页面
def show_frame(frame):
    frame.tkraise()


def center_widgets(frame):
    # 创建开始按钮，并绑定点击事件
    def start_button_click():
        # left_range = left_range_entry.get()
        # right_range = right_range_entry.get()
        left_range = 1000
        right_range = 1049
        start_work(int(left_range), int(right_range))

    # 在 Frame 上创建一个内部 Frame，以包装输入框和按钮
    inner_frame = tk.Frame(frame)
    inner_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")  # 使用 grid 布局管理器

    # 在内部 Frame 上添加左范围输入框
    left_range_label = tk.Label(inner_frame, text="开始题号:1000")
    left_range_label.grid(row=0, column=0, pady=9)
    # left_range_entry = tk.Entry(inner_frame)
    # left_range_entry.grid(row=0, column=1, pady=9)

    # 在内部 Frame 上添加右范围输入框
    right_range_label = tk.Label(inner_frame, text="结束题号:1049")
    right_range_label.grid(row=1, column=0, pady=9)
    # right_range_entry = tk.Entry(inner_frame)
    # right_range_entry.grid(row=1, column=1, pady=9)

    # 在内部 Frame 上添加开始按钮
    start_button = tk.Button(inner_frame, text="开始爬取", command=start_button_click)
    start_button.grid(row=2, column=0, columnspan=2, pady=9)

    # 配置内部 Frame 的列和行以使其自适应居中
    inner_frame.columnconfigure(0, weight=1)
    inner_frame.columnconfigure(1, weight=1)
    inner_frame.rowconfigure(0, weight=1)
    inner_frame.rowconfigure(1, weight=1)
    inner_frame.rowconfigure(2, weight=1)


# 主函数，程序的开始
if __name__ == '__main__':
    # 创建主窗口
    root = tk.Tk()
    root.title("爬虫GUI")
    root.geometry("400x300")  # 设置窗口大小

    # 创建一个容器，用于承载不同的页面
    container = tk.Frame(root)
    container.pack(fill="both", expand=True)

    # 创建主页面
    main_frame = tk.Frame(container)
    main_frame.grid(row=0, column=0, sticky="nsew")

    # 在主页面上添加按钮，用于进入子页面1和子页面2
    crawler_button = tk.Button(main_frame, text="进入爬虫", command=lambda: show_frame(page1_frame))
    crawler_button.grid(row=0, column=0, pady=45)
    data_management_button = tk.Button(main_frame, text="数据管理", command=lambda: show_frame(page2_frame))
    data_management_button.grid(row=1, column=0, pady=45)

    #################################################
    # 创建子页面1（爬虫界面）
    page1_frame = tk.Frame(container)
    page1_frame.grid(row=0, column=0, sticky="nsew")  # 使用 grid 布局管理器

    # 在爬虫界面上添加返回首页按钮
    back_to_main_page1 = tk.Button(page1_frame, text="返回首页", command=lambda: show_frame(main_frame))
    back_to_main_page1.grid(row=0, column=0, pady=45)

    # 将输入框和按钮自适应居中
    center_widgets(page1_frame)
    #################################################

    # 创建子页面2
    page2_frame = tk.Frame(container)
    page2_frame.grid(row=0, column=0, sticky="nsew")

    # 在数据管理界面上添加返回首页按钮
    back_to_main_page1 = tk.Button(page2_frame, text="返回首页", command=lambda: show_frame(main_frame))
    back_to_main_page1.grid(row=0, column=0, pady=45)

    #################################################
    # 初始显示主页面
    show_frame(main_frame)

    # 运行主循环
    root.mainloop()