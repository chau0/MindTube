# MindTube Development Container
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        build-essential \
        curl \
        git \
        wget \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        sqlite3 \
        postgresql-client \
        redis-tools \
        ffmpeg \
        # For audio processing (ASR fallback)
        libsndfile1 \
        libsox-fmt-all \
        sox \
        # For PDF generation
        wkhtmltopdf \
        # For development tools
        tree \
        htop \
        jq \
        vim \
        nano \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 (for frontend development)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install global Node.js tools
RUN npm install -g \
    yarn \
    pnpm \
    @vercel/cli \
    typescript \
    ts-node \
    prettier \
    eslint

# Install Python development tools globally
RUN python -m pip install --upgrade pip setuptools wheel

# Create workspace directory
WORKDIR /workspaces/mindtube

# Copy requirements for faster rebuilds
COPY pyproject.toml ./
COPY requirements*.txt* ./

# Install Python dependencies
RUN pip install -e ".[dev]"

# Install pre-commit hooks system-wide
RUN git config --global init.defaultBranch main \
    && git config --global user.name "Dev Container" \
    && git config --global user.email "dev@mindtube.local"

# Create useful aliases
RUN echo 'alias ll="ls -alF"' >> /home/vscode/.bashrc \
    && echo 'alias la="ls -A"' >> /home/vscode/.bashrc \
    && echo 'alias l="ls -CF"' >> /home/vscode/.bashrc \
    && echo 'alias mt="make test"' >> /home/vscode/.bashrc \
    && echo 'alias ml="make lint"' >> /home/vscode/.bashrc \
    && echo 'alias mf="make format"' >> /home/vscode/.bashrc \
    && echo 'alias mdev="make dev"' >> /home/vscode/.bashrc

# Set up zsh aliases too
RUN echo 'alias ll="ls -alF"' >> /home/vscode/.zshrc \
    && echo 'alias la="ls -A"' >> /home/vscode/.zshrc \
    && echo 'alias l="ls -CF"' >> /home/vscode/.zshrc \
    && echo 'alias mt="make test"' >> /home/vscode/.zshrc \
    && echo 'alias ml="make lint"' >> /home/vscode/.zshrc \
    && echo 'alias mf="make format"' >> /home/vscode/.zshrc \
    && echo 'alias mdev="make dev"' >> /home/vscode/.zshrc

# Create data directories
RUN mkdir -p /workspaces/mindtube/data/cache \
    && mkdir -p /workspaces/mindtube/data/exports \
    && mkdir -p /workspaces/mindtube/data/logs \
    && chown -R vscode:vscode /workspaces/mindtube/data

# Switch to vscode user
USER vscode

# Set up Python path
ENV PYTHONPATH=/workspaces/mindtube/packages/core:$PYTHONPATH
ENV PATH=/home/vscode/.local/bin:$PATH

# Install user-level Python tools
RUN pip install --user \
    ipython \
    jupyter \
    jupyterlab \
    notebook

# Create useful directories
RUN mkdir -p /home/vscode/.config/git \
    && mkdir -p /home/vscode/bin

# Set working directory
WORKDIR /workspaces/mindtube

# Default command
CMD ["/bin/bash"]