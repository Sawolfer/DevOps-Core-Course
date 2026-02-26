# Git Commit - Что добавлять?

## 🚀 Быстрый ответ

### ✅ ДОБАВИТЬ В ГИТ:
```bash
# Terraform код + документация
git add terraform/main.tf
git add terraform/variables.tf
git add terraform/outputs.tf
git add terraform/cloud-init.sh
git add terraform/README.md
git add terraform/YANDEX_QUICK_START.md
git add terraform/setup-yandex.sh
git add terraform/.tflint.hcl
git add terraform/terraform.tfvars.example

# Pulumi код + документация
git add pulumi/__main__.py
git add pulumi/requirements.txt
git add pulumi/Pulumi.yaml
git add pulumi/README.md
git add pulumi/PULUMI_TESTING_GUIDE.md
git add pulumi/QUICK_START.sh
git add pulumi/test.sh
git add pulumi/test_pulumi.py

# CI/CD + Документация
git add .github/workflows/terraform-ci.yml
git add docs/LAB04.md
git add .gitignore
```

### ❌ НЕ ДОБАВЛЯТЬ (в .gitignore):
- `terraform/key.json` ← **API ключ!**
- `terraform/.terraform/` ← кэш
- `terraform/terraform.tfstate*` ← состояние
- `terraform/terraform.tfvars` ← реальные значения
- `pulumi/.pulumi/` ← состояние
- `pulumi/venv/` ← окружение
- `~/.ssh/lab04_key` ← приватный ключ

---

## 📋 ПОЛНЫЙ КОММИТ:

```bash
# Проверить
git status

# Добавить все нужные файлы
git add terraform/main.tf terraform/variables.tf terraform/outputs.tf \
        terraform/cloud-init.sh terraform/README.md terraform/YANDEX_QUICK_START.md \
        terraform/setup-yandex.sh terraform/.tflint.hcl terraform/terraform.tfvars.example \
        pulumi/__main__.py pulumi/requirements.txt pulumi/Pulumi.yaml \
        pulumi/README.md pulumi/PULUMI_TESTING_GUIDE.md pulumi/QUICK_START.sh \
        pulumi/test.sh pulumi/test_pulumi.py \
        .github/workflows/terraform-ci.yml docs/LAB04.md .gitignore

# Проверить что добавлено
git diff --cached --name-only

# Коммитить
git commit -m "Lab 04: Infrastructure as Code (Terraform & Pulumi on Yandex Cloud)"

# Отправить
git push origin main
```

---

## 🔐 ЗОЛОТОЕ ПРАВИЛО:

**НИКОГДА не коммитить:**
- ❌ API ключи (key.json, credentials и т.д.)
- ❌ Приватные SSH ключи
- ❌ .tfstate файлы
- ❌ Пароли в коде
- ❌ .env файлы с секретами

**Всегда коммитить:**
- ✅ Код инфраструктуры (.tf, .py)
- ✅ Конфиг шаблоны (.tfvars.example)
- ✅ Документ ацию (README, guides)
- ✅ requirements.txt (зависимости)
- ✅ .gitignore (правила)

---

Смотри полный гайд в: `GIT_COMMIT_GUIDE.md`
