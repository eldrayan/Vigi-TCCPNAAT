# Validação documental — Entrega 6

Base: `main` em `962e4b7effe579e1652dc56ec03e490264a45df3`, revisada na
branch `docs/entrega-6`. Verificação de software realizada em 17/09/2026
UTC, em computador Linux x86_64; não representa ensaio da Raspberry Pi.

## Critérios e evidências

| Critério | Evidência no repositório | Resultado e pendência |
| --- | --- | --- |
| Código-fonte desenvolvido | `edge/`, `backend/`, `frontend/`, `model_lifecycle/`, `scripts/` | Atendido: código organizado e disponível. |
| Esquemático elétrico | [Manual, artefatos históricos e parecer](esquematico/esquematico-eletrico.md) | Parcial: auditoria documental concluída e artefato histórico reprovado para montagem; circuito definitivo, variante do sensor, condicionamento e medições precisam de bancada. |
| Diagramas de arquitetura atualizados | [Componentes e sequência](arquitetura/diagrama-arquitetural.md) e diagrama do README | Atendido documentalmente: bancos distintos, serviços, contratos e contexto operacional conferidos no código. |
| Manual no README | [README](../README.md) | Atendido documentalmente: caminho de instalação, configuração, operação e verificação, com limitações explícitas. |
| Pré-requisitos e recursos | README: instalação inicial; manual elétrico: componentes | Parcial para reprodução física: versão exata do sistema, câmera/cabo e capacidade de armazenamento da bancada não medidos. |
| Dependências e instalação | README, `pyproject.toml`, `uv.lock`, Dockerfiles, [DVC](dvc-dagshub.md) | Atendido documentalmente; build Docker e recuperação do modelo verificados. Instalação limpa na Pi não executada. |
| Configuração | README, `.env.example`, [múltiplas estações](operacao/01-multiplas-estacoes.md) | Atendido: credenciais, ACL, contexto, lote e reinício do Edge explicados. |
| Instruções de montagem | [Manual de interfaces e checklist](esquematico/esquematico-eletrico.md) | Parcial: não constitui aprovação elétrica nem montagem validada. |
| Execução | README: reprodução ponta a ponta e exemplo por imagem | Atendido para software verificado; captura por sensor/câmera permanece pendente. |
| Resultado que confirma execução | `/health`, consulta de inspeções, [manual do dashboard](operacao/02-dashboard-e-diagnostico.md) | Atendido: ID de inspeção confrontado entre emissão e persistência na API. |
| Identificação das partes principais | Módulos, nomes, docstrings e árvore do README | Atendido. |

Não se certifica reprodução física integral ou nota máxima nesta revisão.
Os itens parciais dependem de evidências físicas, não de completar texto por suposição.

## Registro de correções e responsabilidades

| Achado / critério | Evidência inicial | Alteração e estado esperado | Responsável / dependência | Risco e validação |
| --- | --- | --- | --- | --- |
| Arquitetura desatualizada | Node-RED na imagem; outbox descrita como futura; bancos confundidos | Mermaid de componentes/seqüência incorporados, contratos reais e separação dos bancos | Agente arquitetura; código MQTT/API | Confundir ACK com persistência: revisado e testado pela API. |
| Hardware inconsistente | Componente de Pi 4B renomeado como Pi 5, terminais do sensor sem função e 3,44 V apresentados como seguros | Manual de interfaces, pinagem, checklist e parecer de reprovação para montagem | Agente hardware; correção do circuito e ensaio físico futuro | Não inventar circuito aprovado; divergências e resultado parcial explícitos. |
| Recuperação de artefatos | Link DVC ausente e autenticação pouco clara | Guia DVC novo, pull explícito, validação de manifesto/peso | Agente documentação técnica; acesso DagsHub | Quatro arquivos recuperados e manifesto carregado. |
| Instalação e manual principal | Roteiro disperso e pré-requisitos incompletos | README reorganizado, clone, ferramentas, CSI e resultados esperados | Orquestrador; integração dos guias | Build e Compose verificados; Pi permanece sem ensaio. |
| Operação de lotes | Painel sugeria atualização automática do Edge | Parar Edge, atualizar BATCH_CODE, reiniciar; preservar seed legado na ACL | Agente operação + revisão independente | Conferência em `scripts/run_conveyor.py` e migration 0007. |
| Teste por imagem | Atalho usa hostname; receptor não configura credenciais | Exemplo com componentes existentes, contexto explícito e publicador autenticado | Orquestrador; teste isolado | CLI problemática documentada, sem mudar produção; persistência confirmada. |
| Pitch/PoC e slides | Atuação mecânica e métricas sem evidência | Removidas afirmações incompatíveis; exemplos rotulados ilustrativos | Agente arquitetura + revisão independente | Busca de termos e revisão dos contratos. |
| Aceitação final | Matriz consolidada ausente | Este relatório e auditoria independente | Agente de validação sem participação nas edições | Achados corrigidos e verificações afetadas repetidas. |

## Verificações realizadas

- CI do PR: 167 testes gerais, 37 testes do backend, lint, build do frontend,
  recuperação dos artefatos MLOps e gate de qualidade do modelo aprovados.
- `git diff --check` e links relativos Markdown: aprovados.
- Quatro diagramas Mermaid renderizados com mermaid-cli; inspeção visual dos
  diagramas de arquitetura, sequência e hardware. Fontes ficam incorporadas nos Markdown.
- PNG e projeto Fritzing auditados contra a configuração do software. O caminho
  pretendido até BCM 17 foi identificado, mas o artefato foi reprovado para
  montagem pelas inconsistências registradas no manual elétrico.
- 32 testes existentes de manifesto, outbox, sincronização, contexto, sensor e
  configuração: aprovados. Usado ambiente Python já disponível no computador;
  isso não comprova instalação limpa do Edge na Raspberry.
- `models.dvc`: quatro arquivos recuperados; `ModelManifest.load` confirmou
  contrato e existência do peso operacional.
- Stack Compose exclusiva `vigi-docs-audit`: imagens construídas, frontend
  compilado, migrations aplicadas e três serviços saudáveis. API retornou
  `{"status":"healthy","database":"connected","mqtt":"connected"}`;
  frontend respondeu HTML pela porta de teste.
- Exemplo por imagem executado com a imagem já versionada nos slides. Inspeção
  `1789610785883383` apareceu na API com o mesmo ID, estação e lote. É um smoke
  de inferência/transporte/persistência; não mede acurácia nem latência na Pi.
- Tentativa inicial da CLI com contexto MQTT falhou por autenticação ausente
  no receptor; o procedimento documental foi corrigido e reexecutado com sucesso.
- Auditor independente reavaliou as correções e não identificou novos
  bloqueadores documentais; não repetiu o ensaio integrado do orquestrador.
- Containers e rede temporários encerrados/removidos ao concluir o ensaio;
  volumes de teste preservados. Nenhum serviço de outro projeto foi encerrado.

## Limitações conhecidas

- Validar circuito, alimentação, sensor, câmera e desempenho físico com a bancada.
- `scripts/infer.py` não configura credenciais no receptor de contexto MQTT;
  `make infer-image` também usa hostname em vez de repassar `DEVICE_ID`.
  O README fornece um teste autenticado com componentes já implementados.
- A tela de configuração de lote usa a primeira estação. Para outras estações,
  usar a API. O Edge contínuo exige reinício após mudança de lote.
- A interface de alarmes apresenta `%` também na recorrência de três eventos;
  o contrato do backend representa contagem nesse caso. Ajuste de interface
  está fora desta revisão documental; não interpretar essa contagem como taxa.
- Não foram alterados código de produção, modelos, ponteiros DVC ou requisitos
  para forçar aprovação. Metas de desempenho continuam sendo metas até medição.
