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
reconciliada em 16/09/2026 com `origin/main` no commit `962e4b7`. Os estados
abaixo descrevem a branch documental criada dessa base; não afirmam homologação
da montagem nem publicação da documentação no repositório remoto.

**Decisão de escopo:** a sinalização física por LEDs e buzzer foi desenvolvida
experimentalmente nessa branch, mas não será integrada à `main`. Ela não compõe
a arquitetura, a montagem, os testes nem as evidências exigidas para a Entrega 6.

| Critério da atividade | Artefato atual | Estado inicial | Evidência ou lacuna |
| --- | --- | --- | --- |
| Código-fonte desenvolvido | `edge/`, `backend/`, `frontend/`, `model_lifecycle/`, `scripts/`, `tests/` | Presente e testado automaticamente | 167 testes gerais e 37 testes do backend aprovados; frontend passou por lint e build |
| Esquemáticos elétricos | [`docs/esquematico/`](../esquematico/esquematico-eletrico.md), incorporado pelo PR #39 | Presente, revisão elétrica pendente | O escopo documental foi limitado a Raspberry Pi, câmera e sensor; o circuito ainda requer conferência elétrica e evidência da montagem real |
| Instruções de montagem | [`docs/esquematico/esquematico-eletrico.md`](../esquematico/esquematico-eletrico.md) | Presente; validação física pendente | O guia identifica componentes, pinagem lógica, procedimento seguro e checklist; o circuito definitivo ainda precisa de revisão e ensaio na bancada |
| Diagramas finais de arquitetura | [`docs/arquitetura/diagrama-arquitetural.md`](../arquitetura/diagrama-arquitetural.md) | Presente e renderizado | Diagramas de componentes, sequência e contratos foram renderizados e inspecionados; não certificam a montagem física |
| Pré-requisitos e recursos | [`README.md`](../../README.md) | Presente | Inclui Raspberry Pi OS 64 bits, câmera CSI/USB, sensor, alimentação, armazenamento, rede, pacotes do sistema, Docker, Compose, Git e `uv` |
| Dependências e instalação | `pyproject.toml`, `uv.lock`, `backend/pyproject.toml`, `backend/uv.lock`, README e [`docs/dvc-dagshub.md`](../dvc-dagshub.md) | Presente; ensaio limpo na Pi pendente | Há clone, instalação, ambiente CSI, autenticação e diagnóstico DVC; a instalação completa ainda não foi repetida por terceiro na Raspberry Pi |
| Configuração | `.env.example`, `compose.yaml`, `Makefile`, `scripts/configurar_env.py`, README | Presente; ensaio limpo pendente | Credenciais, portas, câmera, estação, lote e múltiplas estações estão documentados; falta reprodução independente em host sem configuração prévia |
| Execução | `Makefile`, `scripts`, README e manuais de [`múltiplas estações`](../operacao/01-multiplas-estacoes.md) e [`dashboard`](../operacao/02-dashboard-e-diagnostico.md) | Presente; ensaio físico pendente | O fluxo por software foi verificado; sensor e câmera reais ainda dependem da bancada |
| Resultado que confirma execução | [`docs/validacao-entrega-6.md`](../validacao-entrega-6.md), `/health`, dashboard, API, logs e testes | Presente para software; evidência física pendente | Smoke registrou saúde dos serviços e o mesmo `inspection_id` da emissão até a API; não comprova montagem, acurácia ou latência na Pi |
| Código compreensível | Pacotes por aquisição, inferência, mensagens, orquestração e módulos do backend | Presente | Responsabilidades principais são localizáveis; o pacote experimental de atuação não fará parte da `main` |
| Reprodução completa por terceiro | README e relatório de validação | Parcial | A reprodução por software foi ensaiada no ambiente de auditoria; ainda exige clone limpo por terceiro e ensaio físico na Raspberry Pi |

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
- preview HTTP da câmera na porta configurável `PREVIEW_PORT`;
- operação com múltiplas estações Edge conectadas ao broker central;
- criação manual de alarmes pelo dashboard/API;
- republicação do último status da estação após reconexão MQTT;
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

## Evidências consolidadas

Validações executadas entre 16 e 17/09/2026, sem alterar código-fonte:

| Verificação | Resultado |
| --- | --- |
| Links locais da documentação versionada | 110 links Markdown e 10 referências de assets dos slides verificados; nenhum ausente |
| Higiene do diff | `git diff --check` aprovado |
| Testes gerais do Edge, modelo e CLIs | 167 aprovados após integrar `962e4b7` |
| Testes do backend em Python 3.12 isolado | 37 aprovados, 1 integração MQTT ignorada e 1 aviso de depreciação do Starlette |
| Ruff e frontend | Ruff, lint TypeScript/ESLint e build de produção aprovados |
| Estrutura da arquitetura | Diagramas Mermaid renderizados e inspecionados visualmente |
| Payload de inspeção do diagrama | Aceito por `InspectionCreateDTO` no ambiente Python 3.12 do backend |
| Smoke integrado | Compose saudável e o mesmo `inspection_id` confirmado da emissão até a API, conforme [`docs/validacao-entrega-6.md`](../validacao-entrega-6.md) |
| Artefatos MLOps | Modelo recuperado pelo DVC/DagsHub e manifesto/peso validados; dataset e modelo também passaram pelos gates do CI |

A suíte do backend precisou ser executada fora da restrição do sandbox porque a
thread do `aiosqlite` não completava sequer uma conexão mínima nesse ambiente.
Ela utilizou Python 3.12 e ambiente virtual temporários em `/tmp`; nenhum arquivo
versionado foi modificado por essa preparação. O teste MQTT ignorado ainda deve
ser executado com broker isolado no checkpoint de reprodução por software.

## Próximos passos

O plano e a checklist executável estão em [`tasks/plan.md`](../../tasks/plan.md)
e [`tasks/todo.md`](../../tasks/todo.md). O manual, a arquitetura e o ensaio por
software foram consolidados; as pendências restantes dependem principalmente
da montagem física e do ensaio independente em clone limpo.
