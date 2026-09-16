# Entrega 6 — Documentação e reprodutibilidade

Este documento controla a preparação da entrega final do Vigi. Ele não substitui
o [`README.md`](../../README.md), que será o manual canônico de instalação e
execução. Sua função é relacionar os critérios da atividade aos artefatos e às
evidências necessárias para afirmar que o sistema pode ser reproduzido por
terceiros.

## Significado dos estados

| Estado | Significado |
| --- | --- |
| Presente | O artefato existe no Git, mas ainda pode precisar de revisão |
| Implementado | Há código no checkout para a capacidade descrita |
| Testado automaticamente | Há teste executável; não comprova hardware real |
| Validado fisicamente | A equipe executou o teste na bancada e registrou evidência ligada a um SHA |
| Pendente | Falta artefato, correção ou evidência obrigatória |

## Matriz de conformidade inicial

Auditoria inicialmente realizada na branch `feat/sinalizacao-fisica` e
reconciliada em 16/09/2026 com `origin/main` no commit `f335140`. Os estados
abaixo descrevem a branch documental criada dessa base; não afirmam homologação
da montagem nem publicação da documentação no repositório remoto.

**Decisão de escopo:** a sinalização física por LEDs e buzzer foi desenvolvida
experimentalmente nessa branch, mas não será integrada à `main`. Ela não compõe
a arquitetura, a montagem, os testes nem as evidências exigidas para a Entrega 6.

| Critério da atividade | Artefato atual | Estado inicial | Evidência ou lacuna |
| --- | --- | --- | --- |
| Código-fonte desenvolvido | `edge/`, `backend/`, `frontend/`, `model_lifecycle/`, `scripts/`, `tests/` | Presente e testado automaticamente | 161 testes gerais e 33 testes do backend aprovados; frontend passou por lint e build |
| Esquemáticos elétricos | [`docs/esquematico/`](../esquematico/esquematico-eletrico.md), incorporado pelo PR #39 | Presente, porém não conforme | Inclui relé/solenoide fora do escopo, afirmações ainda sem evidência e circuito do sensor que requer revisão elétrica; não usar como instrução final até corrigir fonte Fritzing, imagem, texto e BOM |
| Instruções de montagem | Manual da câmera, sensor E18-D80NK, Raspberry Pi 5 e alimentação, a consolidar | Pendente | A montagem final não inclui LEDs nem buzzer e ainda precisa ser ensaiada fisicamente |
| Diagramas finais de arquitetura | [`docs/arquitetura/diagrama-arquitetural.md`](../arquitetura/diagrama-arquitetural.md) | Atualizado no working tree; render visual pendente | Revisão 0.8.0 inclui estação Edge modular, outbox contínua, MQTT autenticado, backend, SQLite e dashboard React; falta inspecionar a renderização dos três Mermaid |
| Pré-requisitos e recursos | [`README.md`](../../README.md) | Parcial | Lista extensa existe, mas mistura itens atuais e futuros e ainda não foi ensaiada em clone limpo |
| Dependências e instalação | `pyproject.toml`, `uv.lock`, `backend/pyproject.toml`, `backend/uv.lock`, README | Parcial | Edge/backend têm locks; Picamera2 depende do sistema; acesso DVC é externo e precisa de procedimento de autorização |
| Configuração | `.env.example`, `compose.yaml`, `Makefile`, `scripts/configurar_env.py`, README | Presente; ensaio limpo pendente | `make up` preserva valores existentes, completa chaves ausentes e gera credenciais locais; falta reproduzir em host sem configuração prévia |
| Execução | `Makefile`, `scripts/`, README | Presente; ensaio físico pendente | README separa serviços, estação contínua, inferência sem hardware, verificação e encerramento seguro |
| Resultado que confirma execução | `/health`, dashboard, API, logs e testes | Presente; evidência final pendente | README informa consultas e resultados observáveis; ainda é necessário registrar o ensaio integrado ligado ao SHA final |
| Código compreensível | Pacotes por aquisição, inferência, mensagens, orquestração e módulos do backend | Presente | Responsabilidades principais são localizáveis; o pacote experimental de atuação não fará parte da `main` |
| Reprodução completa por terceiro | Ainda sem evidência dedicada | Pendente | Exige clone limpo por terceiro e registro de sistema, versões, SHA, comandos, duração e bloqueios |

## Estado real que deve orientar a revisão

### Implementado neste checkout

- aquisição por Picamera2 ou OpenCV, inferência e contrato de decisão;
- sensor E18-D80NK e laço contínuo de inspeção;
- publicação MQTT, backend FastAPI, migrations e persistência SQLite;
- módulos de inspeções, estações/lotes, estados de dispositivo e alarmes;
- outbox SQLite e recuperação de contexto na CLI `scripts/infer.py`;
- outbox SQLite no fluxo contínuo iniciado por `scripts/run_conveyor.py`;
- sincronizador separado de pendências em `scripts/sync_outbox.py`;
- configuração segura do `.env` por `scripts/configurar_env.py`;
- captura configurável e gravação opcional dos quadros inspecionados;
- dashboard React servido por Nginx, com consumo REST/SSE do backend;
- testes automatizados com dublês de hardware.

### Limites que não podem ser ocultados

- a outbox protege eventos de inspeção, mas os alertas operacionais publicados
  separadamente não possuem a mesma fila persistente;
- o código experimental de LEDs e buzzer existe somente em branch separada,
  está excluído da versão final e não deve ser tratado como artefato da entrega;
- o acesso ao dataset e ao modelo depende do remote DVC e de autorização externa;
- a interface elétrica do E18-D80NK com a GPIO de 3,3 V ainda precisa ser
  confirmada e documentada conforme a montagem real;
- arquivos não rastreados no computador de desenvolvimento não fazem parte da
  entrega até serem revisados e adicionados deliberadamente.

## Evidência mínima para encerrar a entrega

1. SHA ou tag candidata e estado remoto verificados.
2. Sistema operacional, arquitetura, versões de Python, Docker, Compose e `uv`.
3. Instalação e execução a partir de clone limpo por pessoa externa à autoria do
   manual.
4. Resultado de testes, lint e smoke MQTT → backend → SQLite → API.
5. Foto da montagem comparável ao esquemático e à tabela de pinagem.
6. Vídeo ou registro contínuo do sensor, captura, inferência, publicação e
   encerramento seguro.
7. Resultado observado e responsável por cada item que dependa de credencial ou
   infraestrutura externa.

## Evidências da primeira fatia

Validações executadas em 16/09/2026, sem alterar código-fonte:

| Verificação | Resultado |
| --- | --- |
| Links locais do README, arquitetura, matriz, esquemático, plano e checklist | 28 links verificados; nenhum ausente |
| Higiene do diff | `git diff --check` aprovado |
| Testes gerais do Edge, modelo e CLIs | 161 aprovados após integrar `68642fc` |
| Testes do backend em Python 3.12 isolado | 33 aprovados, 1 integração MQTT ignorada e 1 aviso de depreciação do Starlette |
| Ruff e frontend | Ruff, lint TypeScript/ESLint e build de produção aprovados |
| Estrutura da arquitetura | 3 blocos Mermaid completos; renderização visual ainda pendente |
| Payload de inspeção do diagrama | Aceito por `InspectionCreateDTO` no ambiente Python 3.12 do backend |

A suíte do backend precisou ser executada fora da restrição do sandbox porque a
thread do `aiosqlite` não completava sequer uma conexão mínima nesse ambiente.
Ela utilizou Python 3.12 e ambiente virtual temporários em `/tmp`; nenhum arquivo
versionado foi modificado por essa preparação. O teste MQTT ignorado ainda deve
ser executado com broker isolado no checkpoint de reprodução por software.

## Próximos passos

O plano e a checklist executável estão em [`tasks/plan.md`](../../tasks/plan.md)
e [`tasks/todo.md`](../../tasks/todo.md). O primeiro checkpoint fecha as
divergências prioritárias do README; em seguida, arquitetura e hardware serão
atualizados antes dos ensaios de reprodução.
