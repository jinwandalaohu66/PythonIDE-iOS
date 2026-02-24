# 宣传页推送到 GitHub

本地宣传页已准备好，按以下步骤完成推送。

## 第一步：在 GitHub 创建公开仓库

1. 打开 https://github.com/new  
2. 填写：
   - **Repository name**：`PythonIDE-Landing`
   - **Description**：面向 iOS 的 Python & JavaScript 开发环境 - 宣传页
   - 选择 **Public**
   - **不要**勾选 "Add a README"、"Add .gitignore"、"Choose a license"
3. 点击 **Create repository**

## 第二步：推送

在终端执行：

```bash
cd /Users/mac/Desktop/PythonIDE/landing-page
git push -u origin main
```

按提示完成 GitHub 登录或认证后即可推送成功。

## 第三步：配置仓库（可选）

推送完成后，在 GitHub 仓库页面：

1. 点击 **About** → 齿轮 → 填写 Description、Topics
2. **Settings** → **General** → 启用 **Discussions**
