from components.base_components import PromptStrategy
from langchain_core.prompts import ChatPromptTemplate

class CommercialQualificationPrompt(PromptStrategy):
    def __init__(self):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
                Tu es un assistant commercial spécialisé dans l’analyse de profils professionnels.
                Scénarios :
                1) Match parfait → Convaincre
                2) Match partiel → Valoriser
                3) Match mais pas intéressé → Orienter
                4) Pas de match → Expliquer

                Réponse max 3 phrases.
                """),
            ("system", "Contexte:\n{context}"),
            ("human", "{question}")
        ])

    def build(self, question, context, state):
        return {"question": question, "context": "\n\n".join(context)}, self.prompt


class ReformulationPrompt(PromptStrategy):
    def build(self, question, context=None, state=None):
        context = context or []
        state = state or {}
        payload = {"qualification": question}
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
                Tu es un assistant conversationnel dont le rôle est uniquement de reformuler le besoin du recruteur. 
                Ne parle jamais de toi ni de ton expertise.
                Formule la reformulation en 2-3 phrases maximum.
                Termine toujours par : "Ai-je bien compris votre besoin ?"
            """),
            ("human", "{qualification}")
        ])
        return payload, prompt
