from __future__ import annotations

import os


def local_reply(author: str, rating: int, text: str) -> str:
    name = author.split()[0] if author else "Olá"
    if rating >= 4:
        return f"Olá, {name}! Muito obrigado pela avaliação e pelo carinho. Ficamos felizes em saber que sua experiência foi positiva. Será um prazer receber você novamente!"
    if rating == 3:
        return f"Olá, {name}. Obrigado por compartilhar sua experiência. Sentimos que alguns pontos poderiam ter sido melhores e vamos analisar a demora mencionada para aprimorar nosso atendimento."
    return f"Olá, {name}. Sentimos muito pelo problema relatado. Agradecemos por nos sinalizar: queremos entender o que aconteceu e encontrar uma solução. Por favor, entre em contato conosco pelo canal de atendimento para que possamos ajudar."


def generate_reply(author: str, rating: int, text: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return local_reply(author, rating, text)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        prompt = (
            "Você escreve respostas em português brasileiro para avaliações de clientes. "
            "Seja cordial, humano, objetivo e nunca invente fatos, descontos ou soluções. "
            "Para notas 1 ou 2, reconheça o problema e convide o cliente para um canal privado. "
            "Não mencione que a resposta foi gerada por IA. Retorne somente a resposta.\n\n"
            f"Cliente: {author}\nNota: {rating}/5\nAvaliação: {text}"
        )
        result = client.chat.completions.create(model=model, temperature=0.4, max_tokens=180, messages=[{"role": "user", "content": prompt}])
        return result.choices[0].message.content.strip()
    except Exception:
        return local_reply(author, rating, text)
