# TASK-035: CI/CD Pipeline

## Task Information
- **ID**: TASK-035
- **Phase**: 7 - Documentation & Deployment
- **Estimate**: 75 minutes
- **Dependencies**: TASK-034
- **Status**: 🔴 Backlog

## Description
Set up continuous integration and deployment pipeline using GitHub Actions to automate testing, code quality checks, security scanning, and deployment processes.

## Acceptance Criteria
- [ ] Create GitHub Actions workflow
- [ ] Add automated testing
- [ ] Add code quality checks
- [ ] Implement automated deployment
- [ ] Add security scanning
- [ ] Create release automation
- [ ] Test pipeline thoroughly

## Implementation Details

### Main CI/CD Workflow
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

env:
  PYTHON_VERSION: "3.11"
  NODE_VERSION: "18"

jobs:
  test:
    name: Test Suite
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]
    
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        pip install -e .

    - name: Run linting
      run: |
        ruff check .
        ruff format --check .

    - name: Run type checking
      run: mypy mindtube/

    - name: Run tests
      env:
        REDIS_URL: redis://localhost:6379/0
        AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
        AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
      run: |
        pytest --cov=mindtube --cov-report=xml --cov-report=html

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install safety bandit semgrep

    - name: Run safety check
      run: safety check --json

    - name: Run bandit security scan
      run: bandit -r mindtube/ -f json -o bandit-report.json

    - name: Run semgrep scan
      run: |
        semgrep --config=auto mindtube/ --json --output=semgrep-report.json

    - name: Upload security reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: security-reports
        path: |
          bandit-report.json
          semgrep-report.json

  docker:
    name: Docker Build
    runs-on: ubuntu-latest
    needs: [test, security]
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to Docker Hub
      if: github.event_name != 'pull_request'
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: mindtube/mindtube
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        target: production
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [docker]
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment..."
        # Add actual deployment commands here

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [docker]
    if: github.event_name == 'release'
    environment: production
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Deploy to production
      run: |
        echo "Deploying to production environment..."
        # Add actual deployment commands here

  release:
    name: Create Release
    runs-on: ubuntu-latest
    needs: [test, security, docker]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      if: startsWith(github.ref, 'refs/tags/')
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*

    - name: Create GitHub Release
      if: startsWith(github.ref, 'refs/tags/')
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        draft: false
        prerelease: false
```

### Code Quality Workflow
```yaml
# .github/workflows/code-quality.yml
name: Code Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  quality:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Run ruff linting
      run: ruff check . --output-format=github

    - name: Run ruff formatting check
      run: ruff format --check .

    - name: Run mypy type checking
      run: mypy mindtube/ --show-error-codes

    - name: Run complexity analysis
      run: |
        pip install radon
        radon cc mindtube/ --min B

    - name: Check import sorting
      run: |
        pip install isort
        isort --check-only mindtube/

    - name: Check docstring coverage
      run: |
        pip install docstr-coverage
        docstr-coverage mindtube/ --fail-under=80
```

### Security Workflow
```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2 AM

jobs:
  security:
    name: Security Analysis
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install security tools
      run: |
        python -m pip install --upgrade pip
        pip install safety bandit semgrep

    - name: Run safety check for dependencies
      run: |
        pip install -r requirements.txt
        safety check --json --output safety-report.json
      continue-on-error: true

    - name: Run bandit for code security
      run: |
        bandit -r mindtube/ -f json -o bandit-report.json
      continue-on-error: true

    - name: Run semgrep for SAST
      run: |
        semgrep --config=auto mindtube/ --json --output=semgrep-report.json
      continue-on-error: true

    - name: Upload security artifacts
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          safety-report.json
          bandit-report.json
          semgrep-report.json

    - name: Comment PR with security results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          
          let comment = '## 🔒 Security Scan Results\n\n';
          
          try {
            const banditReport = JSON.parse(fs.readFileSync('bandit-report.json', 'utf8'));
            comment += `**Bandit**: ${banditReport.results.length} issues found\n`;
          } catch (e) {
            comment += '**Bandit**: Report not available\n';
          }
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
```

### Performance Testing Workflow
```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  performance:
    name: Performance Testing
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        pip install -e .

    - name: Run performance tests
      env:
        REDIS_URL: redis://localhost:6379/0
      run: |
        pytest tests/performance/ -v --benchmark-only --benchmark-json=benchmark.json

    - name: Store benchmark result
      uses: benchmark-action/github-action-benchmark@v1
      with:
        tool: 'pytest'
        output-file-path: benchmark.json
        github-token: ${{ secrets.GITHUB_TOKEN }}
        auto-push: true
        comment-on-alert: true
        alert-threshold: '200%'
        fail-on-alert: true
```

### Deployment Scripts
```bash
#!/bin/bash
# scripts/deploy-staging.sh

set -e

echo "🚀 Deploying to staging environment..."

# Set environment
export ENVIRONMENT=staging
export IMAGE_TAG=${GITHUB_SHA:-latest}

# Deploy using docker-compose
docker-compose -f docker-compose.staging.yml pull
docker-compose -f docker-compose.staging.yml up -d

# Wait for health check
echo "⏳ Waiting for application to be healthy..."
timeout 60 bash -c 'until curl -f http://staging.mindtube.com/api/v1/health; do sleep 2; done'

echo "✅ Staging deployment complete!"
echo "🌐 Application available at: http://staging.mindtube.com"
```

```bash
#!/bin/bash
# scripts/deploy-production.sh

set -e

echo "🚀 Deploying to production environment..."

# Backup current deployment
echo "📦 Creating backup..."
kubectl create backup production-backup-$(date +%Y%m%d-%H%M%S)

# Set environment
export ENVIRONMENT=production
export IMAGE_TAG=${GITHUB_REF_NAME:-latest}

# Deploy using Kubernetes
kubectl apply -f k8s/production/

# Wait for rollout
kubectl rollout status deployment/mindtube-api

# Run health checks
echo "🏥 Running health checks..."
kubectl run health-check --rm -i --restart=Never --image=curlimages/curl -- \
  curl -f http://mindtube-api:8000/api/v1/health

echo "✅ Production deployment complete!"
echo "🌐 Application available at: https://api.mindtube.com"
```

### Release Automation
```yaml
# .github/workflows/release.yml
name: Release

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release (e.g., 1.2.3)'
        required: true
        type: string
      prerelease:
        description: 'Is this a prerelease?'
        required: false
        type: boolean
        default: false

jobs:
  release:
    name: Create Release
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine bump2version

    - name: Update version
      run: |
        bump2version --new-version ${{ github.event.inputs.version }} patch
        git push origin main --tags

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*

    - name: Create GitHub Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: v${{ github.event.inputs.version }}
        release_name: Release v${{ github.event.inputs.version }}
        draft: false
        prerelease: ${{ github.event.inputs.prerelease }}
        body: |
          ## Changes in this Release
          
          <!-- Add release notes here -->
          
          ## Installation
          
          ```bash
          pip install mindtube==${{ github.event.inputs.version }}
          ```
          
          ## Docker
          
          ```bash
          docker pull mindtube/mindtube:${{ github.event.inputs.version }}
          ```
```

### GitHub Repository Configuration
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "maintainer-username"
    assignees:
      - "maintainer-username"

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug Report
description: File a bug report
title: "[Bug]: "
labels: ["bug", "triage"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!

  - type: input
    id: version
    attributes:
      label: Version
      description: What version of MindTube are you running?
      placeholder: ex. 1.0.0
    validations:
      required: true

  - type: textarea
    id: what-happened
    attributes:
      label: What happened?
      description: Also tell us, what did you expect to happen?
      placeholder: Tell us what you see!
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Steps to reproduce
      description: How can we reproduce this issue?
      placeholder: |
        1. Run command '...'
        2. See error
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Relevant log output
      description: Please copy and paste any relevant log output.
      render: shell
```

### Branch Protection Rules
```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "test",
      "security",
      "docker"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  },
  "restrictions": null
}
```

## Testing

### Pipeline Testing
```bash
#!/bin/bash
# scripts/test-pipeline.sh

set -e

echo "🧪 Testing CI/CD pipeline locally..."

# Test linting
echo "Running linting checks..."
ruff check .
ruff format --check .

# Test type checking
echo "Running type checks..."
mypy mindtube/

# Test security scanning
echo "Running security scans..."
safety check
bandit -r mindtube/

# Test Docker build
echo "Testing Docker build..."
docker build -t mindtube:test .

# Test application startup
echo "Testing application startup..."
docker run --rm -d --name mindtube-test -p 8080:8000 mindtube:test
sleep 10

# Test health endpoint
if curl -f http://localhost:8080/api/v1/health; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

# Cleanup
docker stop mindtube-test

echo "✅ Pipeline tests completed successfully!"
```

## Verification Steps
1. [ ] GitHub Actions workflows are created
2. [ ] All tests run successfully in CI
3. [ ] Code quality checks pass
4. [ ] Security scans complete without critical issues
5. [ ] Docker images build and deploy correctly
6. [ ] Release automation works
7. [ ] Branch protection rules are configured
8. [ ] Deployment scripts function properly

## Dependencies
- TASK-034 (Docker configuration) for containerized deployments
- GitHub repository with appropriate permissions
- Docker Hub or container registry access
- PyPI account for package publishing
- Staging and production environments

## Notes
- Configure secrets in GitHub repository settings
- Set up branch protection rules for main branch
- Configure deployment environments with appropriate approvals
- Monitor pipeline performance and optimize as needed
- Implement proper rollback procedures for failed deployments