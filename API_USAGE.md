# SpiralMind Nexus – API Usage Guide

Ten plik opisuje, jak korzystać z REST API oraz WebSocketów systemu SpiralMind Nexus.

## REST API

- Endpoint: `/analyze` (POST)
  - Parametry: `text` (str), `mode` (str, opcjonalnie: BALANCED/VERIFICATION/CREATIVE), `context` (dict, opcjonalnie)
  - Zwraca: decyzja, confidence, success, liczba iteracji, tryb pipeline, czas przetwarzania, timestamp

- Endpoint: `/analyze/batch` (POST)
  - Parametry: `items` (lista obiektów jak wyżej)
  - Zwraca: lista wyników + statystyki batcha

- Endpoint: `/health` (GET)
  - Zwraca: status, wersja, czy config załadowany, uptime

## WebSocket API

- Endpoint: `/ws/stream`
  - Połączenie dwukierunkowe, obsługuje JSON:
    - Wysyłasz: `{ "text": "Twój tekst", "mode": "BALANCED" }`
    - Otrzymujesz: wyniki analizy, statusy, błędy

## Przykład użycia (Python)

```python
import requests
resp = requests.post('http://localhost:8000/analyze', json={"text": "Test", "mode": "CREATIVE"})
print(resp.json())
```

## Przykład użycia (JavaScript, WebSocket)

```js
const ws = new WebSocket('ws://localhost:8000/ws/stream');
ws.onmessage = (e) => console.log(e.data);
ws.onopen = () => ws.send(JSON.stringify({text: "Test", mode: "BALANCED"}));
```

## Dokumentacja Swagger

- Dostępna pod `/docs` (Swagger UI) i `/redoc` (ReDoc)

## Integracja z innymi systemami

- Możesz łączyć się przez REST/WebSocket z dowolnego języka
- Możliwa integracja z innymi AI przez API (np. orchestracja, batch processing, federacja wyników)

## Kontakt i wsparcie

- [www.mtaquestwebsidex.com](https://www.mtaquestwebsidex.com)
- Autor: Patryk Sobierański
