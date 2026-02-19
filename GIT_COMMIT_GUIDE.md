# Git Commit Guide for Lab 04

## ✅ ДОБАВИТЬ В ГИТ (git add)

### Terraform Code
- `terraform/main.tf` - инфраструктура 
- `terraform/variables.tf` - переменные
- `terraform/outputs.tf` - выходные значения
- `terraform/cloud-init.sh` - скрипт инициализации
- `terraform/README.md` - документация
- `terraform/YANDEX_QUICK_START.md` - быстрый старт
- `terraform/setup-yandex.sh` - скрипт установки
- `terraform/.gitignore` - правила исключения (если есть)
- `terraform/.tflint.hcl` - linting rules
- `terraform/terraform.tfvars.example` - пример конфигурации ⚠️ БЕЗ реальных значений!

### Pulumi Code
- `pulumi/__main__.py` - Python код инфраструктуры
- `pulumi/requirements.txt` - Python зависимости
- `pulumi/Pulumi.yaml` - конфиг проекта
- `pulumi/README.md` - документация
- `pulumi/PULUMI_TESTING_GUIDE.md` - гайд тестирования (НОВЫЙ!)
- `pulumi/QUICK_START.sh` - быстрый старт (НОВЫЙ!)
- `pulumi/test.sh` - тестовый скрипт (НОВЫЙ!)
- `pulumi/test_pulumi.py` - Python тест (НОВЫЙ!)

### CI/CD
- `.github/workflows/terraform-ci.yml` - GitHub Actions для Terraform

### Документация
- `docs/LAB04.md` - НОВЫЙ! Полное описание Lab 04
- `.gitignore` - обновлённые правила исключения
- `README.md` (если обновлён)

---

## ❌ НЕ ДОБАВЛЯТЬ (должны быть в .gitignore)

### Секреты и Ключи
- ❌ `terraform/key.json` - API ключ Yandex! НИКОГДА!
- ❌ `~/.ssh/lab04_key` - приватный SSH ключ
- ❌ `terraform/terraform.tfvars` - реальные значения конфега
- ❌ Любые `.env` файлы с паролями

### Terraform состояние
- ❌ `terraform/.terraform/` - кэш провайдера
- ❌ `terraform/.terraform.lock.hcl` - локальный лок
- ❌ `terraform/terraform.tfstate` - состояние с данными!
- ❌ `terraform/terraform.tfstate.backup`
- ❌ `crash.log` - логи краша

### Pulumi состояние
- ❌ `pulumi/.pulumi/` - локальное состояние
- ❌ `pulumi/venv/` - виртуальное окружение
- ❌ `pulumi/Pulumi.dev.yaml` - конфиг со значениями ⚠️ ЕСЛИ он содержит секреты
- ❌ `pulumi/__pycache__/` - Python кэш

### IDE файлы
- ❌ `.vscode/`
- ❌ `.idea/`
- ❌ `.DS_Store` (macOS)
- ❌ `*.swp`, `*.swo` (Vim)

---

## 📋 Команды для коммита

### Проверить что будет добавлено
```bash
git add -n terraform/ pulumi/ .github/ docs/ .gitignore
# Выведет список файлов БЕЗ их добавления
```

### Добавить по категориям

**1. Terraform:**
```bash
git add terraform/main.tf
git add terraform/variables.tf
git add terraform/outputs.tf
git add terraform/cloud-init.sh
git add terraform/README.md
git add terraform/YANDEX_QUICK_START.md
git add terraform/setup-yandex.sh
git add terraform/.tflint.hcl
git add terraform/terraform.tfvars.example
```

**2. Pulumi:**
```bash
git add pulumi/__main__.py
git add pulumi/requirements.txt
git add pulumi/Pulumi.yaml
git add pulumi/README.md
git add pulumi/PULUMI_TESTING_GUIDE.md
git add pulumi/QUICK_START.sh
git add pulumi/test.sh
git add pulumi/test_pulumi.py
```

**3. CI/CD:**
```bash
git add .github/workflows/terraform-ci.yml
```

**4. Документация:**
```bash
git add docs/LAB04.md
git add app_python/docs/LAB04.md  # Если обновлён
git add .gitignore
```

### Или одной командой (безопасно):
```bash
# Проверить
git status

# Добавить только нужные файлы (исключит .gitignore'д файлы)
git add terraform/__main__.py terraform/variables.tf terraform/outputs.tf \
        terraform/cloud-init.sh terraform/README.md terraform/setup-yandex.sh \
        pulumi/__main__.py pulumi/requirements.txt pulumi/Pulumi.yaml \
        .github/workflows/terraform-ci.yml docs/LAB04.md .gitignore
```

---

## 🔍 Проверка перед коммитом

### Убедиться что НЕ будут добавлены секреты:
```bash
git diff --cached | grep -i "password\|secret\|key\|token"
# Должно быть пусто!
```

### Проверить список файлов которые будут добавлены:
```bash
git diff --cached --name-only
```

### Если случайно добавил секрет:
```bash
# Отменить staging
git reset HEAD <file>

# Удалить из истории (если уже закоммитил)
git rm --cached terraform/key.json
echo "terraform/key.json" >> .gitignore
git commit --amend
```

---

## 💾 Финальный коммит

```bash
# Проверить что добавлено
git status

# Коммитить
git commit -m "Lab 04: Infrastructure as Code (Terraform & Pulumi) - Yandex Cloud"

# Или более подробно:
git commit -m "
Lab 04: Infrastructure as Code Implementation

- Terraform setup for Yandex Cloud
  * main.tf: VPC, Subnet, Security Group, Compute Instance
  * variables.tf: Configurable parameters
  * outputs.tf: VM IP and SSH command
  * cloud-init.sh: Automated SSH setup
  * Documentation and quick start guides

- Pulumi setup (Python) for same infrastructure
  * __main__.py: Yandex Cloud resources in Python
  * Pulumi.yaml: Project configuration
  * Testing guides and automation scripts

- CI/CD: GitHub Actions workflow for Terraform validation

- Documentation: Complete Lab 04 report with best practices

Cloud: Yandex Cloud (Free tier, $0)
Cost: $0 (within free tier limits)
"

# Отправить на GitHub
git push origin main
```

---

## ⚠️ ВАЖНЫЕ ПРАВИЛА

### 🚫 Никогда не коммитить:
1. **API ключи** (key.json, aws_key.pem и т.д.)
2. **Приватные SSH ключи** (id_rsa, lab04_key и т.д.)
3. **Passwords/Tokens** (даже тестовые!)
4. **.tfstate файлы** (содержат состояние с секретами!)
5. **Большие файлы** (venv/, node_modules/, .terraform/)

### ✅ Всегда коммитить:
1. **Код инфраструктуры** (main.tf, __main__.py и т.д.)
2. **Конфигурационные шаблоны** (terraform.tfvars.example)
3. **Документацию** (README.md, гайды и т.д.)
4. **requirements.txt** (зависимости)
5. **.gitignore** (правила исключения)
6. **Скрипты** (setup.sh, test.sh и т.д.)

### 🔐 Для секретов используй:
1. GitHub Secrets (для CI/CD)
2. Environment variables (локально)
3. Secret managers (для production)
4. НИКОГДА - в коде или .gitignore'д файлах не закоммиченных!

---

## Итого - что добавляем:

```
✅ Добавить:
   - terraform/*.tf (код)
   - terraform/*.sh (скрипты)
   - terraform/*.md (документация)
   - pulumi/__main__.py (код)
   - pulumi/Pulumi.yaml (конфиг)
   - pulumi/*.md, *.sh (документация и скрипты)
   - .github/workflows/*.yml (CI/CD)
   - docs/LAB04.md (документация)
   - .gitignore (обновлённый)

❌ Не добавлять:
   - terraform/key.json (КЛЮЧ!)
   - terraform/.terraform/ (кэш)
   - terraform/terraform.tfstate (состояние)
   - pulumi/.pulumi/ (состояние)
   - pulumi/venv/ (окружение)
   - ~/.ssh/lab04_key (приватный ключ)
```
