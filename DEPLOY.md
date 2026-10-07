# Deploy permanente

O projeto está configurado para o Vercel com runtime Python/Flask. O repositório `main` fica conectado ao projeto Vercel para novos deploys automáticos a cada push.

## Variáveis de ambiente

- `OPENAI_API_KEY`: opcional; sem ela, o sistema usa o gerador local.
- `OPENAI_MODEL`: opcional; padrão `gpt-4o-mini`.
- `FLASK_SECRET_KEY`: recomendado para substituir a chave local.

## Banco de dados

O MVP usa SQLite para demonstração. Em ambiente serverless, a camada de escrita local não deve ser considerada armazenamento permanente. Antes de uso operacional contínuo, migrar `db.py` para PostgreSQL/Neon/Supabase ou banco gerenciado equivalente e configurar `DATABASE_URL`.

## Google Business Profile

A publicação externa requer OAuth 2.0, IDs de conta/local e a implementação das chamadas no adaptador `integrations/google_business.py`.
