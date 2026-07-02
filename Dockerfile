# 使用 CentOS 7 作为基础镜像（与 RHEL 7 兼容）
FROM centos:7

# 设置工作目录
WORKDIR /app

# 安装编译工具和 Python 依赖
RUN yum groupinstall -y "Development Tools" && \
    yum install -y \
    wget \
    gcc \
    zlib-devel \
    bzip2-devel \
    openssl-devel \
    ncurses-devel \
    sqlite-devel \
    readline-devel \
    tk-devel \
    gdbm-devel \
    db4-devel \
    libpcap-devel \
    expat-devel \
    xz-devel \
    libffi-devel \
    && yum clean all

# 编译安装 Python 3.12
RUN wget https://www.python.org/ftp/python/3.12.3/Python-3.12.3.tgz && \
    tar -xzf Python-3.12.3.tgz && \
    cd Python-3.12.3 && \
    ./configure --enable-optimizations --enable-shared && \
    make -j$(nproc) && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.12.3*

# 更新 pip
RUN python3.12 -m pip install --upgrade pip

# 安装应用依赖
RUN python3.12 -m pip install \
    PySide6==6.6.3.1 \
    pyais \
    attrs \
    packaging \
    altgraph \
    pyinstaller

# 复制应用代码
COPY ais_sender.py /app/ais_sender.py

# 使用 PyInstaller 打包（生成单文件可执行程序）
RUN python3.12 -m PyInstaller \
    --onefile \
    --name="ais_sender" \
    --hidden-import=PySide6.QtCore \
    --hidden-import=PySide6.QtGui \
    --hidden-import=PySide6.QtWidgets \
    --hidden-import=pyais.encode \
    --add-data="/usr/local/lib/python3.12/site-packages/PySide6/Qt/plugins:/PySide6/Qt/plugins" \
    /app/ais_sender.py

# 设置输出目录为工作目录
WORKDIR /app/dist

# 默认命令
CMD ["bash"]
