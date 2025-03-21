# Dockerfile可视化生成工具

这是一个简单易用的Dockerfile可视化生成工具，可以帮助用户通过Web界面轻松创建和配置Dockerfile，无需记忆各种Dockerfile指令的语法。

## 功能特点

- 支持常用的Dockerfile指令（FROM, RUN, COPY, ADD, WORKDIR等）
- 直观的Web界面，拖拽式操作
- 实时预览和帮助提示
- 可以下载生成的Dockerfile文件
- 适合Docker初学者和有经验的用户

## 系统要求

- Python 3.6+
- Flask及相关依赖

## 安装与使用

1. 克隆本仓库
```
git clone https://github.com/yourusername/dockerfile-generator.git
cd dockerfile-generator
```

2. 安装依赖
```
pip install -r requirements.txt
```

3. 运行应用
```
python app.py
```

4. 打开浏览器访问 http://localhost:5000

## 使用方法

1. 使用界面添加Dockerfile指令
2. 为每个指令填写相应内容
3. 点击"生成Dockerfile"按钮预览
4. 点击"下载Dockerfile"保存到本地
5. 将Dockerfile放在项目根目录下使用

## 技术栈

- Flask: Web框架
- Bootstrap: 前端UI
- Flask-WTF: 表单处理

## 贡献

欢迎任何形式的贡献，包括但不限于新功能、bug修复、文档改进等。请提交Pull Request或Issue。

## 许可证

MIT 