# Software for Pioneer Particle

## The bot doesn't work. Go here: https://github.com/warnaz/Pioneer-Particle-testnet

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

## macKey и device_id

Для работы софта нужны 2 параметра: macKey и device_id. Они отслеживают действия пользователей, поэтому использовать множество адресов для одних и тех же macKey и device_id не рекомендуется. 

Эти параметры генерирует сам Particle Pioneer. Я создал маленькое видео(20 секунд), чтобы вам легче было найти их: 
https://youtu.be/-XiWKmLvYSA

Их вам нужно будет добавить в файл config.py в переменные MAC_KEY и DEVICE_ID
