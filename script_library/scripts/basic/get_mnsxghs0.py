import urllib3
urllib3.disable_warnings()
def menu():
    print('-'*20)
    print('网页侦测程序（GET请求)')
    print('http状态码含义：')
    print('1xx:信息，请求收到，继续处理。')
    print('2xx:成功，请求已成功被服务器接收、理解、并接受')
    print('3xx:重定向，需要后续操作才能完成这一请求')
    print('4xx:客户端错误，请求含有语法错误或者无法被执行')
    print('5xx:服务器错误，服务器在处理某个正确请求时发生错误')
    print('-'*20)

def url():
    name_url = input('请输入网名：')
    web_url = input('请输入网址：')

    if not web_url.startswith(('http://', 'https://')):
        web_url = 'http://' + web_url
    
    try:
        http = urllib3.PoolManager()
        r = http.request('GET', web_url, timeout=5.0)
        print(name_url, '请求状态码：', r.status)
    except Exception as e:
        print(f'请求失败: {e}')

def main():
    menu()
    while True:
        url()
        # 添加退出选项
        choice = input('是否继续检查？(y/n): ').lower()
        if choice != 'y':
            print('程序结束')
            break

if __name__ == "__main__":
    main()

