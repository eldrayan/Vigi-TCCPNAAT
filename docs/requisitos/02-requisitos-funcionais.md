> **Projeto:** Vigi — Sistema Embarcado para Inspeção e Triagem de Linhas de Envase  
> **Revisão:** 0.2.0
> **Responsável:** Alan Mendes Vieira
> **Milestone:** Estruturação de Requisitos

---

### Registro de Alterações

| Versão | Responsável | Data | Alterações |
| :--- | :--- | :--- | :--- |
| **0.1.0** | Alan Mendes Vieira | 01/09/2026 | Elaboração inicial das Histórias de Usuário.
| **0.2.0** | Squad Vigi | 08/09/2026 | Inclusão de classificação explícita, dashboard, sincronização e diagnóstico. |

---

### Requisitos Funcionais

| Identificador | Descrição | Prioridade (MoSCoW) | Depende de |
| :--- | :--- | :--- | :--- |
| US01 | Como operário da linha, quero que **o sistema classifique cada recipiente como conforme ou não conforme e, quando não conforme, informe o tipo `SEM_TAMPA`, `TAMPA_TORTA` ou `AMASSADO`**, para identificar claramente o defeito antes da etapa final. | Deve ter | `Nenhum` |
| US02 | Como supervisor de produção, quero **receber alertas sonoros/visuais e no painel da linha sempre que a taxa de refugo ultrapassar o limite aceitável em um lote**, para intervir na máquina envasadora/rosqueadora antes que ocorra desperdício em massa. | Deve ter | US01 |
| US03 | Como supervisor de produção, quero **visualizar a contagem total de anomalias (sem tampa, tampa torta, frasco amassado) em tempo real**, para identificar e dar manutenção a estações críticas com antecedência. | Deveria ter | US01 |
| US04 | Como supervisor de produção, quero **receber relatórios categorizados pelo tipo de anomalia** (sem tampa, tampa torta, frasco amassado), para identificar qual estação do processo anterior está gerando mais falhas. | Deveria ter | US01 |
| US05 | Como supervisor de produção, quero que o **sistema armazene automaticamente cada ocorrência de anomalia detectada (com data, hora, tipo de anomalia, lote e estação)**, para que a equipe possa realizar análises estatísticas de longo prazo, identificar padrões de falhas e embasar melhorias no processo. | Poderia ter | US01 |
| US06 | Como técnico de automação, quero que **um mecanismo pneumático/braço ejetor desvie frascos defeituosos para uma esteira de refugo em tempo real**, para evitar travamentos mecânicos e paradas não programadas. | Não terá desta vez | US01 |
| US07 | Como supervisor de produção, quero **visualizar totais de inspeções, conformes, não conformes e taxa de conformidade**, para acompanhar rapidamente a qualidade da produção. | Deve ter | US01 |
| US08 | Como supervisor de produção, quero **filtrar o histórico por período, lote e tipo de anomalia**, para investigar ocorrências específicas. | Deveria ter | US05 |
| US09 | Como técnico de automação, quero que **os eventos armazenados localmente sejam sincronizados automaticamente após o restabelecimento da comunicação**, para evitar perda ou duplicação de dados. | Deve ter | US05 |
| US10 | Como operador, quero **visualizar o estado do sensor, da câmera, da unidade de processamento e da comunicação com o sistema de supervisão**, para identificar falhas operacionais. | Deve ter | US01 |
| US11 | Como operador, quero **reconhecer alarmes críticos no dashboard, registrando data, hora e responsável**, para garantir rastreabilidade da intervenção. | Deveria ter | US02 |

---

### Documentos Complementares

* [05. Levantamento de Requisitos Técnicos](05-requisitos-tecnicos.md)
* [Diagrama Arquitetural do Sistema](../arquitetura/diagrama-arquitetural.md)
