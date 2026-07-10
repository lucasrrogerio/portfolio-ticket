from app.services.rag_service import buscar_documentos_similares

resultado = buscar_documentos_similares("quais as vantagens de ser enterprise?")
print("RESULTADO DA BUSCA:")
print(resultado)
