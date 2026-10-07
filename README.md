# Review Reply MVP

MVP em Python para extrair/importar avaliações, gerar sugestões de resposta e publicar somente após comando explícito.

## O que já funciona

- Painel web local em Flask;
- SQLite sem configuração adicional;
- Avaliações de demonstração para testar o fluxo;
- Importação de avaliações via JSON;
- Geração de resposta por regras locais;
- Geração opcional via OpenAI quando `OPENAI_API_KEY` estiver configurada;
- Edição da sugestão;
- Aprovação individual;
- Publicação individual somente após aprovação;
- Histórico de alterações e ações;
- Adaptador preparado para integrar Google Business Profile.

## Executar

```bash
cd /home/ubuntu/review-reply-mvp
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:8000`.

Para usar OpenAI:

```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4o-mini"
```

Sem a chave, o sistema usa o gerador local, suficiente para o MVP.

## Importar avaliações

O endpoint `POST /api/reviews/import` aceita:

```json
{
  "reviews": [
    {
      "external_id": "google-123",
      "author": "Maria",
      "rating": 5,
      "text": "Atendimento excelente!",
      "reviewed_at": "2026-10-07T12:00:00"
    }
  ]
}
```

## Próxima integração

O arquivo `integrations/google_business.py` define a interface para buscar e responder avaliações no Google Business Profile. Para ativá-la, será necessário configurar OAuth e os identificadores da conta/local do Google. O MVP deliberadamente não publica nada automaticamente.

## Estrutura

- `app.py`: rotas web e API;
- `db.py`: schema e persistência SQLite;
- `reply_generator.py`: geração local e OpenAI;
- `integrations/`: adaptadores de plataformas externas;
- `templates/`: painel;
- `tests/`: testes básicos do fluxo de aprovação/publicação.
