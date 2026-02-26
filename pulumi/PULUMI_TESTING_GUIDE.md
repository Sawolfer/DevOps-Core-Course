# Pulumi Testing Guide - Yandex Cloud

## ✅ Статус подготовки

- ✅ Service Account создан  
- ✅ key.json готов (`terraform/key.json`)
- ✅ SSH ключ готов (`~/.ssh/lab04_key`)
- ✅ Pulumi Python modules установлены
- ✅ Pulumi.dev.yaml настроена с Folder ID: `b1gsfpff6nb6v1a4q5g8`

---

## 🚀 Быстрый старт

### 1. Активировать окружение

```bash
cd pulumi/
source venv/bin/activate
export YC_SERVICE_ACCOUNT_KEY_FILE="../terraform/key.json"
```

### 2. Инициализировать Pulumi Stack

```bash
# Скачать Pulumi CLI (если ещё не установлен)
curl -fsSL https://get.pulumi.com | sh

# Или через Homebrew (в фоне уже работает)

# Инициализировать stack
export PATH=$HOME/.pulumi/bin:$PATH
pulumi stack init dev

# Или если уже инициализирован:
pulumi stack select dev
```

### 3. Проверить конфигурацию

```bash
pulumi config

# Должно вывести:
# KEY                 VALUE
# yandex:folder_id    b1gsfpff6nb6v1a4q5g8
# yandex:zone         ru-central1-a
```

### 4. Preview (сухой прогон - БЕЗ создания ресурсов!)

```bash
pulumi preview

# Ожидаемый вывод:
# Previewing update (dev)
# 
#  Type                        Name                    Plan
#  +   yandex:vpc:Network       devops-lab04-network    create
#  +   yandex:vpc:Subnet        devops-lab04-subnet     create
#  +   yandex:vpc:SecurityGroup devops-lab04-sg         create
#  +   yandex:compute:Instance  devops-lab04-vm         create
#
# Plan: 4 resources to create
```

**Этот шаг НЕ создаёт реальные ресурсы!** Это безопасно!

### 5. Развернуть инфраструктуру

```bash
pulumi up

# Выведет preview и спросит: "Do you want to perform this update?"
# Ответить: yes
# Ждать 2-3 минуты...
```

**Ожиданный результат:**
```
Updating (dev)

  Type                        Name                   Status
  +   yandex:vpc:Network       devops-lab04-network   created
  +   yandex:vpc:Subnet        devops-lab04-subnet    created
  +   yandex:vpc:SecurityGroup devops-lab04-sg        created
  +   yandex:compute:Instance  devops-lab04-vm        created

Outputs:
  instance_public_ip: 192.0.2.45
  instance_private_ip: 10.0.1.10
  ssh_command: ssh -i ~/.ssh/lab04_key ubuntu@192.0.2.45
  zone: ru-central1-a

Resources: 4 created

Duration: 2m35s
```

### 6. Получить IP адрес

```bash
pulumi stack output instance_public_ip

# Выведет:
# 192.0.2.45
```

### 7. Подключиться по SSH

```bash
# Способ 1: Используя output
SSH_IP=$(pulumi stack output instance_public_ip)
ssh -i ~/.ssh/lab04_key ubuntu@$SSH_IP

# Способ 2: Прямая команда
eval $(pulumi stack output -raw ssh_command)

# Первый раз система спросит про fingerprint:
# The authenticity of host 192.0.2.45 can't be established...
# Ответить: yes

# Если подключились:
ubuntu@instance-lab04:~$ 
```

### 8. Проверить ВМ на месте

```bash
# На ВМ:
ubuntu@instance-lab04:~$ whoami
ubuntu

ubuntu@instance-lab04:~$ uname -a
Linux instance-lab04 5.15.0-1234-yandex-cpt #1 SMP x86_64 GNU/Linux

ubuntu@instance-lab04:~$ cat /etc/os-release | head -1
NAME="Ubuntu"

# Выход
exit
```

### 9. Удалить инфраструктуру (очистка)

```bash
pulumi destroy

# Выведет план удаления и спросит подтверждение
# Ответить: yes
# Ждать 1-2 минуты

# Ожидаемый результат:
# Destroying (dev)
#
#  Type                        Name                   Status
#  -   yandex:compute:Instance  devops-lab04-vm        deleted
#  -   yandex:vpc:SecurityGroup devops-lab04-sg        deleted
#  -   yandex:vpc:Subnet        devops-lab04-subnet    deleted
#  -   yandex:vpc:Network       devops-lab04-network   deleted
#
# Resources destroyed: 4
```

---

## 🐛 Troubleshooting

### Ошибка 1: "command not found: pulumi"

**Решение:**
```bash
# Добавить Pulumi в PATH
export PATH=$HOME/.pulumi/bin:$PATH

# Или добавить в ~/.zshrc:
echo 'export PATH=$HOME/.pulumi/bin:$PATH' >> ~/.zshrc
source ~/.zshrc

# Проверить
pulumi version
```

### Ошибка 2: "No valid credentials found"

**Решение:**
```bash
# Убедиться что key.json правильно установлена
ls -la ../terraform/key.json

# Установить переменную окружения
export YC_SERVICE_ACCOUNT_KEY_FILE="$(cd ../terraform && pwd)/key.json"

# Проверить что она установлена
echo $YC_SERVICE_ACCOUNT_KEY_FILE
```

### Ошибка 3: "Module not found: pulumi_yandex"

**Решение:**
```bash
source venv/bin/activate
pip install -q pulumi-yandex
```

### Ошибка 4: "SSH: Connection refused"

**Решение:** ВМ загружается медленно, подождите 60 сек и попробуйте снова

```bash
sleep 60
ssh -i ~/.ssh/lab04_key ubuntu@$(pulumi stack output instance_public_ip)
```

### Ошибка 5: "Permission denied (publickey)"

**Решение:** Проверить права на SSH ключ

```bash
chmod 600 ~/.ssh/lab04_key
ssh -i ~/.ssh/lab04_key ubuntu@192.0.2.45
```

---

## 📊 Тестирование по этапам

### ✅ Проверка 1: Конфигурация
```bash
pulumi config
# Должна показать folder_id и zone
```

### ✅ Проверка 2: Preview
```bash
pulumi preview
# Должна показать 4 ресурса к созданию
```

### ✅ Проверка 3: Deployment
```bash
pulumi up
# Ресурсы создаются за 2-3 минуты
```

### ✅ Проверка 4: SSH Access
```bash
ssh -i ~/.ssh/lab04_key ubuntu@$(pulumi stack output instance_public_ip)
# Должна подключиться
whoami
# Должна вывести: ubuntu
```

### ✅ Проверка 5: Cleanup
```bash
pulumi destroy
# Все ресурсы удаляются
```

---

## 🎓 Что это демонстрирует?

1. **Infrastructure as Code (IaC)** - инфраструктура описана в коде
2. **Pulumi** - Python-based tools для IaC
3. **Yandex Cloud** - реальное облако (не эмулятор!)
4. **Automation** - всё создаётся одной командой
5. **Repeatability** - можно запустить снова и получить ту же инфраструктуру

---

## 💡 Дополнительные команды

```bash
# Посмотреть все stacks
pulumi stack ls

# Посмотреть историю изменений
pulumi history

# Получить все outputs
pulumi stack output

# Удалить stack полностью
pulumi stack rm dev

# Просмотреть код инфраструктуры
cat __main__.py
```

---

## ❓ Использованные компоненты

- **Pulumi**: Infrastructure as Code tool (Python)
- **Yandex Cloud**: Cloud provider
- **Yandex VPC**: Virtual Private Network
- **Yandex Compute**: Virtual machines
- **Ubuntu 22.04 LTS**: Operating system на ВМ

---

**Готово!** Теперь Pulumi полностью настроен и готов к тестированию! 🚀
