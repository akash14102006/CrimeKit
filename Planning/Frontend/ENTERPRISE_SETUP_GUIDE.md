# ENTERPRISE SETUP GUIDE - Developer Environment Configuration

**Setting up your development environment? Follow this comprehensive guide (15-30 minutes).**

---

## 🖥️ SYSTEM REQUIREMENTS

### Operating System
- macOS 12+ (Intel or Apple Silicon)
- Windows 10+ (WSL2 recommended)
- Ubuntu 20.04 LTS+

### Minimum Hardware
- 8GB RAM (16GB recommended)
- 256GB disk space (SSD recommended)
- CPU: Any modern multi-core processor

---

## 📦 INITIAL SETUP (macOS/Linux)

### Step 1: Install Homebrew (macOS only)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Required Tools
```bash
# macOS
brew install git node@18 postgresql docker pnpm

# Ubuntu/Linux
sudo apt update
sudo apt install -y git nodejs npm postgresql docker.io
npm install -g pnpm
```

### Step 3: Verify Installation
```bash
git --version          # Should be 2.40+
node --version         # Should be 18.x or 20.x
npm --version          # Should be 9.x+
pnpm --version         # Should be 8.x+
docker --version       # Should be 24.x+
```

---

## 💻 WINDOWS-SPECIFIC SETUP

### Step 1: Enable WSL2
1. Open PowerShell as Administrator
2. Run: `wsl --install`
3. Restart your computer
4. Open WSL2 terminal

### Step 2: Install in WSL2
```bash
sudo apt update
sudo apt install -y git nodejs npm postgresql docker.io build-essential curl
npm install -g pnpm
```

### Step 3: Verify Installation
```bash
git --version
node --version
npm --version
pnpm --version
docker --version
```

---

## 🔐 Git Configuration

### Step 1: Configure Git Identity
```bash
git config --global user.name "Your Full Name"
git config --global user.email "your.email@company.com"
```

### Step 2: Setup SSH Keys
```bash
# Generate key (press Enter for all prompts)
ssh-keygen -t ed25519 -C "your.email@company.com"

# Display public key
cat ~/.ssh/id_ed25519.pub
```

### Step 3: Add SSH Key to GitHub
1. Go to GitHub Settings → SSH and GPG keys
2. Click "New SSH key"
3. Paste your public key
4. Click "Add SSH key"

### Step 4: Configure Git Hooks
```bash
# Create .git-hooks directory
mkdir -p ~/.git-hooks

# Configure git to use this directory
git config --global core.hooksPath ~/.git-hooks
```

---

## 📁 PROJECT SETUP

### Step 1: Clone Repository
```bash
git clone git@github.com:company/project-name.git
cd project-name
```

### Step 2: Setup Node.js Project
```bash
# Install dependencies
pnpm install

# Verify installation
pnpm list | head -20
```

### Step 3: Environment Configuration
```bash
# Copy environment template
cp .env.example .env.local

# Edit with your settings
# Set: DATABASE_URL, API_PORT, etc.
nano .env.local
```

### Step 4: Database Setup
```bash
# Create database (if needed)
createdb project_name_dev

# Run migrations
pnpm run migrations:run

# Seed database (if available)
pnpm run seed
```

### Step 5: Verify Setup
```bash
# Start development server
pnpm run dev

# In another terminal, test the API
curl http://localhost:3000/health
```

---

## 🛠️ IDE CONFIGURATION

### Visual Studio Code Setup

#### Step 1: Install VS Code
- Download from: https://code.visualstudio.com/
- Install for your operating system

#### Step 2: Install Essential Extensions
```
Extensions to install (Cmd+Shift+X):
- ESLint (by Microsoft)
- Prettier (by Prettier)
- TypeScript Vue Plugin
- Git Graph
- GitHub Copilot (optional)
- Thunder Client (for API testing)
```

#### Step 3: Configure VS Code Settings
Create `.vscode/settings.json`:
```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true
}
```

#### Step 4: Open Project
1. Open VS Code
2. File → Open Folder
3. Select project directory
4. Accept "Recommended Extensions" prompt

### Other IDEs
- **WebStorm:** Download from https://www.jetbrains.com/webstorm/
- **Cursor:** Download from https://cursor.sh/
- **Vim/Neovim:** Use with appropriate plugins

---

## 🐳 DOCKER SETUP

### Step 1: Install & Start Docker
```bash
# macOS: Already installed via Homebrew
# Windows: Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Linux: Already installed via apt

# Start Docker service
# (macOS/Windows: Docker Desktop will auto-start)
# (Linux: sudo systemctl start docker)
```

### Step 2: Verify Docker
```bash
docker --version
docker run hello-world
```

### Step 3: Docker Compose Setup
```bash
# Already included with Docker Desktop
# On Linux, install:
sudo apt install -y docker-compose

# Verify
docker-compose --version
```

### Step 4: Setup Local Services
```bash
# In project directory
docker-compose up -d

# View running services
docker-compose ps

# Check logs
docker-compose logs -f
```

---

## 🗄️ DATABASE SETUP

### PostgreSQL Configuration

#### Step 1: Start PostgreSQL
```bash
# macOS (if using Homebrew)
brew services start postgresql

# Windows (WSL2): Already running
# Linux: sudo systemctl start postgresql
```

#### Step 2: Verify Connection
```bash
psql --version
psql postgres
```

#### Step 3: Create Development Database
```bash
# Connect to PostgreSQL
psql postgres

# In psql:
CREATE DATABASE project_name_dev;
CREATE DATABASE project_name_test;

# Exit
\q
```

#### Step 4: Connect Your Project
```bash
# Set DATABASE_URL in .env.local
DATABASE_URL="postgresql://user:password@localhost:5432/project_name_dev"

# Run migrations
pnpm run migrations:run
```

#### Step 5: Verify Database
```bash
# Connect to database
psql project_name_dev

# List tables
\dt

# Exit
\q
```

---

## 🔑 API & SERVICE SETUP

### Step 1: Get API Keys
Contact your team lead for:
- GitHub Personal Access Token
- API authentication credentials
- Service-specific keys

### Step 2: Configure Environment
```bash
# Edit .env.local and add:
GITHUB_TOKEN=your_token_here
API_KEY=your_key_here
SECRET_KEY=your_secret_here
```

### Step 3: Secure Your Keys
```bash
# Add .env.local to .gitignore
echo ".env.local" >> .gitignore

# Never commit secrets!
git status  # Verify .env.local is NOT shown
```

### Step 4: Verify Access
```bash
# Test API connectivity
pnpm run test:api

# Or manually test
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.company.com/test
```

---

## 🚀 VERIFY COMPLETE SETUP

### Checklist
```bash
# 1. Git is configured
git config user.name
git config user.email

# 2. SSH key works
ssh -T git@github.com  # Should succeed

# 3. Node.js is installed
node --version
pnpm --version

# 4. Project dependencies installed
pnpm list | head -20

# 5. Database is running
psql -l  # List databases

# 6. Development server starts
pnpm run dev  # Should start without errors

# 7. Tests pass
pnpm run test  # Should pass

# 8. Linter runs
pnpm run lint  # Should complete

# 9. Build succeeds
pnpm run build  # Should complete
```

### Success Criteria
- ✅ All commands above succeed
- ✅ Development server runs on port 3000
- ✅ Database has tables
- ✅ API responds to requests
- ✅ Tests pass
- ✅ No linter errors

---

## ⚡ USEFUL COMMANDS

### Development
```bash
# Start development server
pnpm run dev

# Run tests
pnpm run test

# Run tests with coverage
pnpm run test:coverage

# Watch mode
pnpm run test:watch

# Lint code
pnpm run lint

# Format code
pnpm run format

# Build for production
pnpm run build
```

### Database
```bash
# Create migration
pnpm run migrations:create your_migration_name

# Run migrations
pnpm run migrations:run

# Rollback migration
pnpm run migrations:revert

# Seed database
pnpm run seed

# Reset database (dev only!)
pnpm run database:reset
```

### Git
```bash
# Check status
git status

# Stage changes
git add .

# Commit changes
git commit -m "Your message"

# Push to remote
git push

# Pull latest
git pull

# View branches
git branch -a
```

---

## 🐛 TROUBLESHOOTING

### Issue: "pnpm: command not found"
```bash
# Solution: Install pnpm globally
npm install -g pnpm

# Verify
pnpm --version
```

### Issue: "Cannot find module 'typescript'"
```bash
# Solution: Reinstall dependencies
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Issue: "Permission denied" when running tests
```bash
# Solution: Make scripts executable
chmod +x scripts/*.sh
```

### Issue: "Database connection refused"
```bash
# Solution: Check PostgreSQL is running
# macOS: brew services list
# Linux: sudo systemctl status postgresql

# Start if needed:
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

### Issue: "Port 3000 already in use"
```bash
# Solution: Kill existing process
# macOS/Linux:
lsof -i :3000
kill -9 PID

# Or use different port:
PORT=3001 pnpm run dev
```

### Issue: "Cannot create SSL connection"
```bash
# Solution: Update SSL certificates
# macOS: /Applications/Python 3.x/Install Certificates.command

# Or disable for development (careful!):
DATABASE_URL="postgresql://...?sslmode=disable"
```

### Still Stuck?
1. Check logs: `pnpm run dev 2>&1 | tail -50`
2. Search repository issues on GitHub
3. Ask team on #dev-setup Slack channel
4. Contact your tech lead

---

## 🔐 SECURITY BEST PRACTICES

### Do ✅
- [ ] Keep .env.local in .gitignore
- [ ] Use strong passwords
- [ ] Enable 2FA on GitHub
- [ ] Use SSH keys instead of HTTPS
- [ ] Rotate API keys regularly
- [ ] Never commit secrets
- [ ] Use HTTPS for external APIs
- [ ] Verify SSL certificates

### Don't ❌
- [ ] Commit .env files
- [ ] Share API keys
- [ ] Use weak passwords
- [ ] Commit secrets to git
- [ ] Use same password everywhere
- [ ] Disable SSL verification in production
- [ ] Leave debugged code in git

---

## 🎓 LEARNING RESOURCES

- [Node.js Docs](https://nodejs.org/docs/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Documentation](https://react.dev/)
- [NestJS Docs](https://docs.nestjs.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Docs](https://docs.docker.com/)

---

## 📞 GETTING HELP

**Environment issues?**
→ Search #dev-setup channel on Slack

**Configuration questions?**
→ Ask your team lead or tech lead

**Git/GitHub help?**
→ Check [GIT_MASTER_PROMPT.md](../01_INTELLIGENCE/SKILLS/GIT_MASTER_PROMPT.md)

**General setup help?**
→ Reference [ENTERPRISE_SETUP_GUIDE.md](ENTERPRISE_SETUP_GUIDE.md) again

---

## ✅ NEXT STEPS

After completing this setup:

1. **Read:** [START_HERE.md](START_HERE.md) - Project orientation
2. **Review:** [Your domain skills](../01_INTELLIGENCE/SKILLS/) - Learn standards
3. **Build:** Follow [FEATURE_DEVELOPMENT_WORKFLOW](../02_EXECUTION/WORKFLOWS/FEATURE_DEVELOPMENT_WORKFLOW.md)
4. **Submit:** Follow [CODE_REVIEW_WORKFLOW](../02_EXECUTION/WORKFLOWS/CODE_REVIEW_WORKFLOW.md)

---

**Setup Complete!** 🎉

You're ready to start building. Welcome to the team!

**Last Updated:** June 2026  
**Questions?** See [WHICH_FILE_TO_READ.md](WHICH_FILE_TO_READ.md)

