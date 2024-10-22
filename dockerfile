# 使用官方的 Python 基础镜像
FROM python:3.10-slim

# worker floder
WORKDIR /app

# 安装必要的构建工具
RUN apt-get update && \
    apt-get install -y gcc g++ make && \
    apt-get clean

# 复制依赖文件
COPY src/requirements.txt .

# 安装依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY src .
COPY .env .

# 设置工作目录为 src
ENV PYTHONPATH=/app

RUN chmod -R g=u /app

# 启动命令
ENTRYPOINT ["sh", "start.sh"]