# Software for Pioneer Particle

### Установка проекта

Клонируйте репозиторий с GitHub:

`git clone https://github.com/warnaz/particle_pioneer.git`

Для установки необходимых библиотек, выполните следующую команду:
`pip install -r requirements.txt`


### Запуск проекта
`python run.py`


## Конфигурация

В файлах `data/keys.txt` и `data/proxies.txt` необходимо указать приватные ключи и прокси соответственно. Формат: один к одному.

## API ключ сервиса 2Captcha

Для работы программы требуется API ключ от сервиса [2Captcha](https://2captcha.com/). Укажите ваш API ключ в переменной `TWO_API_KEY` в файле `.env`.
