# Checklist executável — Entrega 6

## Tarefa 1: Inventariar o estado real do repositório

**Descrição:** Comparar código, configuração e documentação para identificar o
que está implementado, testado, validado fisicamente e ainda pendente.

**Critérios de aceitação:**

- [x] Código-fonte, documentação, infraestrutura e artefatos DVC foram localizados.
- [x] Divergências prioritárias foram registradas sem converter planos em fatos.
- [x] Branch, SHA e arquivos locais não rastreados foram preservados.

**Verificação:**

- [x] Conferência: `git status --short --branch`
- [x] Conferência: `git ls-files`
- [x] Revisão cruzada de README, arquitetura, hardware, Makefile, Compose e CLIs.

**Dependências:** Nenhuma.

**Arquivos envolvidos:** Somente leitura.

**Escopo estimado:** S.

## Tarefa 2: Criar o controle documental da Entrega 6

**Descrição:** Registrar plano, checklist e matriz que relaciona cada critério da
atividade a um artefato, uma evidência e uma pendência objetiva.

**Critérios de aceitação:**

- [x] Plano ordenado por dependências criado.
- [x] Cada tarefa possui aceitação e verificação.
- [x] Matriz distingue presença de arquivo, teste automático e validação física.

**Verificação:**

- [x] Links locais validados por script.
- [x] `git diff --check` sem erros.

**Dependências:** Tarefa 1.

**Arquivos envolvidos:**

- `tasks/plan.md`
- `tasks/todo.md`
- `docs/entrega-6/README.md`

**Escopo estimado:** M.

## Tarefa 3: Corrigir as divergências prioritárias do README

**Descrição:** Atualizar o estado de sensor, fila offline, backend e frontend,
além de ligar o README ao controle da Entrega 6 e registrar a exclusão da
sinalização experimental.

**Critérios de aceitação:**

- [x] Fila offline unitária e limite do laço contínuo estão descritos corretamente.
- [x] LEDs e buzzer estão explicitamente fora da versão destinada à `main`.
- [x] Dashboard React integrado pela `main` está identificado como implementado.

**Verificação:**

- [x] Busca não encontra as afirmações obsoletas catalogadas na matriz.
- [x] Links do README resolvem para arquivos existentes.
- [x] `git diff --check -- README.md` sem erros.

**Dependências:** Tarefas 1 e 2.

**Arquivos envolvidos:**

- `README.md`

**Escopo estimado:** S.

## Tarefa 4: Consolidar instalação e configuração no README

**Descrição:** Criar um caminho principal de clone limpo com pré-requisitos,
versões, configuração segura do `.env`, recuperação DVC e alternativas para
CSI/USB.

**Critérios de aceitação:**

- [ ] Pré-requisitos de host, Python, Docker, câmera e acesso DVC são explícitos.
- [ ] Comandos podem ser copiados na ordem apresentada.
- [ ] Segredos e caminhos pessoais não são exigidos no Git.

**Verificação:**

- [ ] Ensaio dos comandos em diretório temporário ou clone limpo.
- [ ] `make help` corresponde ao manual.
- [ ] Variáveis documentadas correspondem a `.env.example`, `compose.yaml` e
  `scripts/configurar_env.py`.

**Dependências:** Tarefa 3.

**Arquivos envolvidos:**

- `README.md`
- `.env.example`, somente se a auditoria comprovar divergência.
- `Makefile`, somente se faltar um comando necessário à reprodução.

**Escopo estimado:** M.

## Tarefa 5: Documentar execução e resultados observáveis

**Descrição:** Separar cenários de validação por software, inferência unitária,
fluxo MQTT até API, modo offline e operação contínua em hardware.

**Critérios de aceitação:**

- [ ] Cada cenário informa comando, pré-condição, saída esperada e falha comum.
- [ ] `/health`, inspeção persistida e resumo da API têm critérios verificáveis.
- [ ] Execução simulada não é apresentada como validação da bancada.

**Verificação:**

- [ ] Testes focados e suíte completa passam.
- [ ] Smoke do Compose passa quando o daemon estiver disponível.
- [ ] Saídas esperadas são comparadas às saídas observadas.

**Dependências:** Tarefa 4.

**Arquivos envolvidos:**

- `README.md`
- `docs/entrega-6/README.md`

**Escopo estimado:** S.

## Tarefa 6: Atualizar a arquitetura final

**Descrição:** Substituir o desenho proposto por vistas atuais de contexto,
containers/processos, módulos e sequência de uma inspeção.

**Critérios de aceitação:**

- [x] Componentes implementados correspondem à base recente da `main`.
- [x] Tópicos MQTT, rotas, bancos e módulos correspondem ao código.
- [x] Limites da outbox e do frontend estão explícitos.
- [x] Topologia de múltiplas estações e preview HTTP correspondem à `main`.

**Verificação:**

- [x] Cada nó do diagrama possui arquivo/configuração de origem identificável.
- [ ] Mermaid renderiza sem erro.
- [x] Payload de exemplo valida contra os DTOs atuais.

**Dependências:** Tarefas 1 e 3.

**Arquivos envolvidos:**

- `docs/arquitetura/diagrama-arquitetural.md`
- `README.md`, somente para atualizar o resumo e links.

**Escopo estimado:** S.

## Tarefa 7: Fechar BOM e esquemático elétrico

**Descrição:** Documentar a montagem elétrica final da câmera, do sensor
E18-D80NK e da Raspberry Pi 5, incluindo modelos, quantidades, conectores,
alimentação e proteção.

**Critérios de aceitação:**

- [ ] BOM identifica cada componente da montagem real.
- [ ] Esquemático mostra alimentação, terra comum, numeração BCM/J8 e interface do sensor.
- [ ] Valores elétricos correspondem à bancada, sem placeholders silenciosos.

**Verificação:**

- [ ] Revisão por integrante que montou o hardware.
- [ ] Continuidade e tensões conferidas com a placa desenergizada/energizada conforme o teste.
- [ ] Comparação entre esquemático e fotografia da montagem.

**Dependências:** Confirmações da equipe listadas em `tasks/plan.md` e validação
elétrica do circuito do sensor documentado pelo PR #39.

**Arquivos envolvidos:**

- Novo manual de montagem final em `docs/hardware/`.
- Novo esquemático em formato-fonte e exportação legível, se adotados.

**Escopo estimado:** M.

## Tarefa 8: Validar a montagem física

**Descrição:** Executar o guia completo na Raspberry Pi 5 e registrar o resultado
do sensor, câmera, inferência, MQTT, API e encerramento seguro.

**Critérios de aceitação:**

- [ ] Todos os estímulos do guia possuem resultado observado.
- [ ] SHA, sistema operacional, Python e versões relevantes são registrados.
- [ ] Falhas ou desvios são corrigidos ou declarados como pendência.

**Verificação:**

- [ ] Checklist do novo manual de montagem final preenchido.
- [ ] Foto/vídeo e logs ligados ao SHA testado.
- [ ] Nenhuma validação é inferida apenas dos testes simulados.

**Dependências:** Tarefas 4, 5 e 7.

**Arquivos envolvidos:**

- Novo manual de montagem final em `docs/hardware/`.
- Evidências aprovadas pela equipe em diretório a definir.

**Escopo estimado:** M.

## Tarefa 9: Executar ensaio de reprodutibilidade em clone limpo

**Descrição:** Pedir a uma pessoa técnica externa à implementação que siga apenas
o README e registre bloqueios, tempo e resultado.

**Critérios de aceitação:**

- [ ] Ambiente é preparado sem instruções orais adicionais.
- [ ] Fluxo por software chega ao resultado documentado.
- [ ] Bloqueios de acesso externo possuem diagnóstico e responsável claros.

**Verificação:**

- [ ] Registro do sistema, comandos, duração e SHA.
- [ ] Testes, lint e smoke final executados.
- [ ] Correções do manual reensaiadas desde o ponto inicial afetado.

**Dependências:** Tarefas 4, 5 e 6.

**Arquivos envolvidos:**

- `README.md`
- `docs/entrega-6/README.md`

**Escopo estimado:** M.

## Tarefa 10: Auditar a entrega final

**Descrição:** Executar a revisão de qualidade e confirmar que o repositório
publicado contém todos os artefatos da atividade.

**Critérios de aceitação:**

- [ ] Matriz não possui item obrigatório sem artefato ou pendência explícita.
- [ ] Links, comandos, versões, diagramas e estados são consistentes.
- [ ] Repositório final não contém segredos nem artefatos pessoais acidentais.

**Verificação:**

- [ ] `git diff --check` e verificador de links passam.
- [ ] Suítes Edge/backend e lint passam no SHA candidato.
- [ ] Branch/tag/remoto do repositório definitivo são conferidos.

**Dependências:** Tarefas 6, 8 e 9.

**Arquivos envolvidos:** documentação afetada pelas correções finais.

**Escopo estimado:** M.
