# SpiralMind Nexus – Integracja z innymi AI

## Możliwości połączeń

- **REST API**: Możesz wywoływać pipeline z dowolnego systemu (Python, JS, Java, bash, etc.)
- **WebSocket API**: Dwukierunkowa komunikacja w czasie rzeczywistym (np. streaming wyników, integracja z UI, orchestracja multi-agent)
- **Batch API**: Przetwarzanie wielu zadań naraz, integracja z systemami kolejkowymi (np. Celery, RabbitMQ, Kafka)
- **Możliwość federacji**: Łączenie wielu instancji SpiralMind Nexus w sieć (federated learning, multi-agent)
- **Integracja z LLM/AGI**: Możesz podłączyć zewnętrzne modele (np. OpenAI, Gemini, HuggingFace) jako pod-pipeline lub voting agent
- **Orkiestracja**: Możliwość budowy hybrydowych pipeline (np. łączenie z innymi AI przez API, voting, konsensus, fallback)

## Przykład integracji (Python)

```python
import requests
resp = requests.post('http://localhost:8000/analyze', json={"text": "Test", "mode": "BALANCED"})
print(resp.json())
```

## Przykład integracji (JavaScript)

```js
fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'Test', mode: 'CREATIVE' })
}).then(r => r.json()).then(console.log);
```

## Przykład federacji (pseudo)

- Instancja A analizuje tekst, przekazuje wynik do instancji B, która podejmuje decyzję końcową
- Możliwość budowy sieci agentów AI (multi-agent, federated learning)

## Kontakt
- [www.mtaquestwebsidex.com](https://www.mtaquestwebsidex.com)
- Autor: Patryk Sobierański
