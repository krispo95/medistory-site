# Сайт Medistory

Генератор маркетингового сайта: посадочная страница и страница поддержки
на трёх языках. Адрес страницы поддержки обязателен для App Store Connect.

## Собрать

```bash
python3 build.py            # результат в docs/
python3 -m http.server -d docs 8000   # посмотреть на localhost:8000
```

## Поправить тексты

Все формулировки лежат в `build.py`, в словаре `CONTENT` — по языку на блок.
Разметку трогать не нужно. Там же наверху:

- `EMAIL` — адрес поддержки,
- `PRIVACY_URL` — политика конфиденциальности,
- `APPSTORE_URL` — ссылка на приложение. Пока пусто, кнопка ведёт на почту;
  после публикации впишите адрес, и кнопка станет «Скачать».

## Опубликовать

Ссылки внутри относительные, поэтому сайт работает и в корне домена,
и в подпапке (как `github.io/medistory-site/`).

```bash
git init && git add -A && git commit -m "Сайт Medistory"
git remote add origin git@github.com:<аккаунт>/medistory-site.git
git push -u origin main
```

В настройках репозитория: Pages → Deploy from a branch → `main` → папка `/docs`.

## Что положить в App Store Connect

- Support URL: `https://<адрес сайта>/support.html`
- Marketing URL: `https://<адрес сайта>/`
- Privacy Policy URL: адрес из `PRIVACY_URL`
