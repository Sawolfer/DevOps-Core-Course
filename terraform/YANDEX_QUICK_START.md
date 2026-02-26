# Yandex Cloud Quick Start 🚀

Быстрая инструкция для запуска Terraform на Yandex Cloud.

## Шаг 1: Создай аккаунт Yandex Cloud

1. Перейди на https://cloud.yandex.ru/
2. Нажми "Создать аккаунт"
3. Подтверди номер телефона и промо-код
4. **Готово!** Получишь бесплатный tier с 1 ВМ

## Шаг 2: Получи Folder ID

```bash
# Способ 1: Через консоль
# https://console.cloud.yandex.ru/
# Сверху видишь Folder ID (похоже на: b1gg86q2uctbr0as5gzg)

# Способ 2: Через CLI
yc config get folder-id
```

## Шаг 3: Создай Service Account

```bash
# Замени FOLDER_ID на свой ID
FOLDER_ID="b1gg86q2uctbr0as5gzg"

# Создай service account
yc iam service-accounts create terraform --folder-id $FOLDER_ID

# Дай ему права (editor)
yc iam service-accounts list --folder-id $FOLDER_ID
# Скопируй ID вывода

# ACCOUNT_ID="ajef..." <- скопируй отсюда
ACCOUNT_ID="ajef1234567890"
yc resource-manager folders add-access-binding $FOLDER_ID \
  --role editor \
  --service-account-id $ACCOUNT_ID
```

## Шаг 4: Создай и скачай ключ

```bash
# Способ 1: Через CLI (проще)
yc iam service-accounts keys create key.json \
  --service-account-name terraform \
  --folder-id $FOLDER_ID

# Скопируй key.json в папку terraform/
cp key.json ~/Documents/GitHub/DevOps-Core-Course/terraform/

# Способ 2: Через консоль
# https://console.cloud.yandex.ru/
# Service accounts → terraform → Create JSON key
```

## Шаг 5: Сгенерируй SSH ключ

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/lab04_key -N ""

# Проверь
ls -la ~/.ssh/lab04_key*
```

## Шаг 6: Отредактируй terraform.tfvars

```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars

# Отредактируй в любом редакторе:
# - yandex_folder_id = "твой-folder-id"
# - yandex_key_file = "./key.json"
```

## Шаг 7: Запусти Terraform

```bash
cd terraform/

# Инициализируй
terraform init

# Проверь конфигурацию
terraform validate

# Предпросмотр
terraform plan

# Создай инфраструктуру
terraform apply
# Подтверди: yes
```

## Шаг 8: Подключись по SSH

```bash
# Получи IP
terraform output instance_public_ip

# Подключись (замени IP)
ssh -i ~/.ssh/lab04_key ubuntu@IP_АДРЕС
```

## Всё! ✅

Твоя ВМ на Yandex Cloud работает!

$$\text{VM Status: }{\color{green}\checkmark}\text{ Running}$$

## Если что-то не работает

### Ошибка: No valid credentials found
```bash
# Проверь путь к key.json
ls -la terraform/key.json

# Либо установи переменную окружения
export YC_SERVICE_ACCOUNT_KEY_FILE="$(pwd)/key.json"
```

### Ошибка: Permission denied
```bash
# Проверь права на файл ключа
chmod 600 key.json

# Проверь права на SSH ключ
chmod 600 ~/.ssh/lab04_key
```

### SSH не подключается
```bash
# Подожди 30-60 секунд (VM еще загружается)
sleep 30

# Попробуй еще раз
ssh -i ~/.ssh/lab04_key ubuntu@IP
```

## Очистить всё (если нужно)

```bash
# Удали ВМ и всё остальное
terraform destroy
# Подтверди: yes
```

---

**Вопросы?** Смотри `terraform/README.md` 📖
