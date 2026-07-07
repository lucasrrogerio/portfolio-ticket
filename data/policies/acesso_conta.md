# Política de Acesso e Segurança de Contas

## 1. Redefinição de Senha
- Clientes que esquecerem a senha podem solicitar a recuperação diretamente na tela inicial de login, clicando em "Esqueci minha senha".
- Um link seguro será enviado para o e-mail cadastrado.
- O link possui validade de **15 minutos**. Se expirar, o cliente deverá solicitar um novo.

## 2. Bloqueio Preventivo de Conta
Para garantir a segurança dos dados, nosso sistema possui proteção contra ataques de força bruta.
- A conta será **bloqueada automaticamente após 5 tentativas consecutivas de login incorretas**.
- O desbloqueio ocorre de forma **automática após 30 minutos**. 
- O suporte técnico de Nível 1 **NÃO** tem permissão para remover esse bloqueio antes dos 30 minutos. O cliente deve ser instruído a aguardar e, em seguida, usar a função de redefinir senha.

## 3. Autenticação em Dois Fatores (2FA)
A autenticação 2FA é recomendada para todos os clientes, mas obrigatória para contas com plano "Enterprise".

### Perda do dispositivo 2FA
Caso o cliente perca acesso ao aplicativo gerador de códigos (como Google Authenticator ou Authy):
- **Caminho Feliz:** O cliente deve usar um dos "Códigos de Recuperação" de uso único, que foram fornecidos na tela durante a ativação do 2FA.
- **Caminho Exceção (Sem códigos):** Se o cliente não salvou os códigos de recuperação, o ticket deve ser escalado IMEDIATAMENTE para a equipe de **Segurança da Informação (Nível 3)**.
  - O operador humano de Nível 3 solicitará uma cópia de documento com foto e comprovante de endereço.
  - A Inteligência Artificial **NÃO DEVE** tentar resetar ou desabilitar o 2FA em nenhuma circunstância. Deve apenas escalar a solicitação.
