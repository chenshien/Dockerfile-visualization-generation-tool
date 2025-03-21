from flask import Flask, render_template, request, flash, redirect, url_for, send_file, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Optional
import os
import tempfile
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dockerfile-generator-secret-key'
bootstrap = Bootstrap(app)

# Dockerfile预设模板
DOCKERFILE_TEMPLATES = {
    'python': '''FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]''',

    'nodejs': '''FROM node:14-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["node", "index.js"]''',

    'nginx': '''FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]''',

    'golang': '''FROM golang:1.17-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o main .

FROM alpine:latest

WORKDIR /app
COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]''',

    'java': '''FROM maven:3.8-openjdk-11 AS builder

WORKDIR /app
COPY pom.xml .
COPY src ./src

RUN mvn package -DskipTests

FROM openjdk:11-jre-slim

WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]'''
}

# Dockerfile指令的基础表单
class DockerInstructionForm(FlaskForm):
    instruction_type = SelectField('指令类型', choices=[
        ('FROM', 'FROM - 指定基础镜像'),
        ('RUN', 'RUN - 执行命令'),
        ('COPY', 'COPY - 复制文件'),
        ('ADD', 'ADD - 添加文件'),
        ('WORKDIR', 'WORKDIR - 设置工作目录'),
        ('ENV', 'ENV - 设置环境变量'),
        ('EXPOSE', 'EXPOSE - 暴露端口'),
        ('CMD', 'CMD - 容器启动命令'),
        ('ENTRYPOINT', 'ENTRYPOINT - 入口点'),
        ('VOLUME', 'VOLUME - 定义卷'),
        ('USER', 'USER - 指定用户'),
        ('LABEL', 'LABEL - 添加元数据'),
        ('ARG', 'ARG - 定义构建参数'),
        ('HEALTHCHECK', 'HEALTHCHECK - 健康检查'),
    ])
    content = TextAreaField('指令内容', validators=[DataRequired()])

class DockerfileForm(FlaskForm):
    instructions = FieldList(FormField(DockerInstructionForm), min_entries=1)
    add_instruction = SubmitField('添加指令')
    generate_dockerfile = SubmitField('生成Dockerfile')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = DockerfileForm()
    
    if request.method == 'POST':
        if 'add_instruction' in request.form and form.validate():
            form.instructions.append_entry()
            return render_template('index.html', form=form)
        
        elif 'generate_dockerfile' in request.form and form.validate():
            dockerfile_content = generate_dockerfile_content(form.instructions.data)
            # 创建临时文件并写入Dockerfile内容
            temp_dir = tempfile.mkdtemp()
            dockerfile_path = os.path.join(temp_dir, 'Dockerfile')
            
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            return render_template('result.html', dockerfile_content=dockerfile_content, dockerfile_path=dockerfile_path)
    
    # 确保初始状态至少有一个指令表单
    if len(form.instructions) == 0:
        form.instructions.append_entry()
    
    return render_template('index.html', form=form, templates=DOCKERFILE_TEMPLATES)

@app.route('/download/<path:filepath>')
def download_file(filepath):
    return send_file(filepath, as_attachment=True, download_name='Dockerfile')

@app.route('/template/<template_name>')
def get_template(template_name):
    """获取预设的Dockerfile模板"""
    if template_name in DOCKERFILE_TEMPLATES:
        return jsonify({'success': True, 'template': DOCKERFILE_TEMPLATES[template_name]})
    else:
        return jsonify({'success': False, 'error': '模板不存在'}), 404

@app.route('/help')
def help_page():
    """显示帮助和教程页面"""
    return render_template('help.html')

@app.route('/parse-template', methods=['POST'])
def parse_template():
    """解析Dockerfile模板文本，返回指令列表"""
    data = request.json
    if not data or 'template' not in data:
        return jsonify({'success': False, 'error': '无效的请求数据'}), 400
    
    template_text = data['template'].strip()
    instructions = []
    
    # 解析模板文本
    lines = template_text.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            parts = line.split(' ', 1)
            if len(parts) == 2:
                instruction_type = parts[0]
                content = parts[1]
                
                valid_instructions = [choice[0] for choice in DockerInstructionForm.instruction_type.kwargs['choices']]
                if instruction_type in valid_instructions:
                    instructions.append({
                        'instruction_type': instruction_type,
                        'content': content
                    })
    
    return jsonify({'success': True, 'instructions': instructions})

def generate_dockerfile_content(instructions):
    """根据用户输入生成Dockerfile内容"""
    content = []
    
    for instruction in instructions:
        instruction_type = instruction['instruction_type']
        instruction_content = instruction['content']
        
        # 对不同类型的指令进行格式化
        if instruction_type in ['CMD', 'ENTRYPOINT'] and not instruction_content.startswith('['):
            # 如果用户没有使用JSON数组格式，我们将它转换为数组格式
            parts = instruction_content.split()
            formatted_content = f"{instruction_type} [{', '.join([f'\"' + part + '\"' for part in parts])}]"
        else:
            formatted_content = f"{instruction_type} {instruction_content}"
        
        content.append(formatted_content)
    
    return '\n'.join(content)

if __name__ == '__main__':
    app.run(debug=True) 