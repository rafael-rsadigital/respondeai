"""Ponto de extensão para Google Business Profile.

A API real exige OAuth 2.0 e os IDs de conta/local. Este adaptador mantém a integração
fora do painel para que o MVP possa ser usado com dados importados sem publicar nada
sem aprovação explícita.
"""

from dataclasses import dataclass


@dataclass
class ExternalReview:
    external_id: str
    author: str
    rating: int
    text: str
    reviewed_at: str
    source: str = "google"


class GoogleBusinessAdapter:
    def __init__(self, access_token: str | None = None):
        self.access_token = access_token

    def fetch_reviews(self) -> list[ExternalReview]:
        raise NotImplementedError("Configurar OAuth e IDs do Google Business Profile antes de ativar a sincronização.")

    def publish_reply(self, external_id: str, reply: str) -> None:
        raise NotImplementedError("Implementar a chamada autenticada da API do Google Business Profile.")
