# Plano de Implementação: Entrega 6 — Documentação e Reprodutibilidade

## Visão geral

Esta entrega transforma o repositório em um manual técnico reproduzível para
uma pessoa que não participou do desenvolvimento. O trabalho será concluído em
fatias verificáveis: primeiro se fixa o estado real do projeto; depois são
consolidados o manual, a arquitetura e a montagem elétrica; por fim, um ensaio
em clone limpo e um ensaio físico produzem as evidências que permitem declarar
a reprodução concluída.

O planejamento foi iniciado em 16/09/2026 e transferido para a branch
`docs/entrega-6`, criada da `origin/main` e atualizada até o commit `f335140`.
A implementação experimental de LEDs e buzzer não será integrada à `main` e
fica explicitamente fora da Entrega 6.

## Decisões de documentação

- O `README.md` da raiz será o caminho canônico de instalação e execução. Os
  documentos especializados serão referenciados por ele, sem duplicar passos
  que possam divergir.
- Toda capacidade será rotulada como **implementada**, **testada
  automaticamente**, **validada fisicamente** ou **pendente**. Código e teste
  simulado não serão apresentados como prova de funcionamento na bancada.
- A arquitetura final mostrará o estado implementado, incluindo o dashboard
  React integrado pela `main`. Funcionalidades futuras ficarão separadas, sem
  aparecer no fluxo executável como se já existissem.
- O esquemático só será fechado depois da confirmação dos modelos e valores dos
  componentes. Pinagem conhecida pode ser documentada agora; valores elétricos
  não confirmados não serão inventados.
- Credenciais do remote DVC e segredos de CI não farão parte do manual. O texto
  explicará como configurá-los localmente e quem deve conceder o acesso.

## Dependências entre as fases

```text
Inventário do estado real
    ├── Manual canônico no README
    ├── Arquitetura final implementada
    └── Esquemático e montagem elétrica
             │
             └── Ensaio físico na Raspberry Pi 5

Manual + arquitetura + hardware
             │
             └── Ensaio em clone limpo e revisão final
```

## Lista de tarefas

As tarefas detalhadas e seus critérios de aceitação estão em
[`tasks/todo.md`](./todo.md).

### Fase 1 — Base rastreável

- [x] Tarefa 1: inventariar artefatos, fatos implementados e lacunas.
- [x] Tarefa 2: criar o plano e a matriz de conformidade da Entrega 6.
- [x] Tarefa 3: corrigir as divergências prioritárias do README.

### Checkpoint — Base rastreável

- [x] Links locais da nova documentação resolvem corretamente.
- [x] Nenhuma capacidade planejada aparece como implementada.
- [x] Diff contém apenas documentação da Entrega 6.

### Fase 2 — Manual e arquitetura

- [ ] Tarefa 4: consolidar pré-requisitos, instalação e configuração no README.
- [ ] Tarefa 5: documentar execução e resultados observáveis por cenário.
- [ ] Tarefa 6: atualizar diagramas e contratos da arquitetura implementada.

### Checkpoint — Reprodução por software

- [ ] Uma pessoa consegue executar testes e o fluxo sem hardware a partir de um
  clone limpo.
- [ ] Mosquitto, backend, SQLite e API possuem verificações de saúde e resultado
  documentadas.
- [ ] Limitações da fila de alertas e da autenticação da API estão explícitas.

### Fase 3 — Hardware e evidências

- [ ] Tarefa 7: fechar lista de materiais e esquemático elétrico.
- [ ] Tarefa 8: validar montagem, câmera e sensor na Raspberry Pi 5.
- [ ] Tarefa 9: registrar versões, SHA, resultados e evidências do ensaio.

### Checkpoint — Reprodução física

- [ ] Terceiro consegue montar a bancada sem depender de informação oral.
- [ ] Fotografias e/ou vídeo permitem comparar a montagem real ao esquemático.
- [ ] Resultado de cada teste físico está ligado ao SHA executado.

### Fase 4 — Fechamento

- [ ] Tarefa 10: executar auditoria final de links, comandos, segredos e
  consistência.
- [ ] Tarefa 11: atualizar a matriz para o estado comprovado e preparar a versão
  final do repositório.

### Checkpoint — Entrega pronta

- [ ] Todos os critérios da atividade possuem artefato e evidência associados.
- [ ] Testes e lint passam no SHA candidato.
- [ ] O estado publicado do repositório é conferido separadamente do estado
  local.

## Riscos e mitigações

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Modelo e dataset dependem de remote DVC restrito | Alto | Documentar o fluxo de autorização, conferir ponteiros e ensaiar com uma identidade sem configuração prévia |
| Esquemático integrado inclui relé/solenoide fora do escopo e circuito ainda não validado | Alto | Corrigir fonte Fritzing, imagem, texto e BOM; manter somente sensor, câmera, alimentação e componentes realmente usados e medidos |
| Diagrama atual mistura implementação e visão futura | Alto | Produzir diagrama "como está" e mover evolução planejada para seção própria |
| Alertas operacionais não usam a outbox das inspeções | Médio | Documentar o limite e não prometer entrega offline dos alertas |
| Dashboard recente ainda não foi ensaiado no hardware alvo | Médio | Executar lint/build e validar o fluxo integrado via Compose na Raspberry Pi 5 |
| Testes simulados serem confundidos com homologação física | Alto | Manter estados de evidência separados e exigir registro de ensaio na Raspberry Pi 5 |
| Instruções variarem entre `Makefile`, `.env.example` e README | Médio | Eleger o README como índice canônico e conferir cada comando contra a CLI/Compose |

## Questões abertas que exigem confirmação da equipe

- Qual é o modelo exato da Raspberry Pi 5, da câmera e da fonte usados na
  montagem final?
- Qual circuito de condicionamento foi realmente usado entre o E18-D80NK e a
  GPIO de 3,3 V?
- A case final possui desenho, dimensões, material e instruções de fixação?
- Qual commit/tag será declarado como versão definitiva e pública da entrega?
