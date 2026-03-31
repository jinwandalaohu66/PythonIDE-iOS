import random    

while True:
    a = input()
    if a == '你好' or a == '早上好' or a == '晚上好' or a == '中午好' or a[1] == '好':
        print('你好,我是你的聊天伙伴豆沙包，输入打开控制台，打开控制台')
    elif a == '再见' or a == '拜拜':
        print('再见')
        break
    elif a == '打开控制台':
        print('问普通疑问句前面加1问：,问是或否的问题前面要加2问：')
    else:
        if a[0] == '1':
            print('我不知道啊!')
        else:
            choices = ["yes", "no"]
            result = random.choice(choices)
            print(result)
