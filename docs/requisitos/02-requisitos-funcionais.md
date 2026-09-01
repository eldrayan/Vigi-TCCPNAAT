> **Projeto:** Vigi — Sistema Embarcado para Inspeção e Triagem de Linhas de Envase  
> **Revisão:** 0.1.0  
> **Responsável:** Alan Mendes Vieira
> **Milestone:** Estruturação de Requisitos

---

### Registro de Alterações

| Versão | Responsável | Data | Alterações |
| :--- | :--- | :--- | :--- |
| **0.1.0** | Alan Mendes Vieira | 01/09/2026 | Elaboração inicial das Histórias de Usuário.

---

### Requisitos Funcionais

| Identificador | Descrição | Prioridade (MoSCoW) | Depende de |
| :--- | :--- | :--- | :--- |
| US01 | Como operário da linha, quero que **o sistema de visão computacional identifique recipientes sem tampa, com tampa frouxa ou deformidades no corpo antes da etapa final**, para que produtos defeituosos não cheguem às máquinas de empacotamento. | Deve ter | - |
| US02 | Como supervisor de produção, quero **receber alertas sonoros/visuais e no painel da linha sempre que a taxa de refugo ultrapassar o limite aceitável em um lote**, para intervir na máquina envasadora/rosqueadora antes que ocorra desperdício em massa. | Deve ter | US01 |
| US03 | Como supervisor de produção, quero **visualizar a contagem total de anomalias (sem tampa, tampa torta, frasco amassado) em tempo real**, para identificar e dar manutenção a estações críticas com antecedência. | Deveria ter | US01 |
| US04 | Como supervisor de produção, quero **receber relatórios categorizados pelo tipo de anomalia** (sem tampa, tampa torta, frasco amassado), para identificar qual estação do processo anterior está gerando mais falhas. | Deveria ter | US01 |
| US05 | Como supervisor de produção, quero que o **sistema armazene automaticamente cada ocorrência de anomalia detectada (com data, hora, tipo de anomalia, lote e estação)**, para que a equipe possa realizar análises estatísticas de longo prazo, identificar padrões de falhas e embasar melhorias no processo. | Poderia ter | US01 |
| US06 | Como técnico de automação, quero que **um mecanismo pneumático/braço ejetor desvie frascos defeituosos para uma esteira de refugo em tempo real**, para evitar travamentos mecânicos e paradas não programadas. | Não terá desta vez | US01 |
