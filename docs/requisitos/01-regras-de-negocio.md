> **Projeto:** Vigi — Sistema Embarcado para Inspeção e Triagem de Linhas de Envase  
> **Revisão:** 0.1.1  
> **Responsável:** Elder Rayan Oliveira Silva  
> **Milestone:** Estruturação de Requisitos

---

### Registro de Alterações

| Versão | Responsável | Data | Alterações |
| :--- | :--- | :--- | :--- |
| **0.1.0** | Elder Rayan Oliveira Silva | 31/08/2026 | Elaboração inicial das Regras de Negócio. |
| **0.1.1** | Elder Rayan Oliveira Silva | 04/09/2026 | Ajuste de rastreabilidade e alinhamento com USs e RNFs. |

---

## Regras de Negócio

As Regras de Negócio (RN) estabelecem as políticas de operação, critérios de decisão de qualidade e diretrizes de conformidade da fábrica, independentemente da tecnologia de implementação:

| Identificador | Descrição | Prioridade | Requisitos Relacionados |
| :--- | :--- | :--- | :--- |
| **RN01** | **Inspeção Unitária Obrigatória:** Todo recipiente que cruzar o ponto de sensoriamento da esteira deve ser inspecionado pelo sistema antes de prosseguir para a etapa seguinte do processo. | Alta | US01, RNF01, RNF02 |
| **RN02** | **Política de Descarte por Incerteza (*Fail-Safe*):** Caso a análise visual não obtenha índice de confiabilidade suficiente ou ocorra falha/timeout na captura, o recipiente deve ser tratado preventivamente como não-conforme e direcionado para refugo. | Alta | US01, RNF05, RNF07 |
| **RN03** | **Segregação de Não-Conformidades:** Todo recipiente identificado como não-conforme deve acionar a sinalização de alerta local e o comando de desvio da esteira antes de atingir a extremidade da linha. | Alta | US02, US06 |
| **RN04** | **Autonomia Operacional Offline:** A decisão de inspeção e a atuação de descarte local devem funcionar de forma desacoplada da infraestrutura de rede externa, armazenando eventos localmente durante eventuais quedas de conexão. | Alta | US05, RNF03, RNF04 |
| **RN05** | **Alarme de Não-Conformidades Recorrentes:** Caso o sistema detecte um número consecutivo pré-definido de recipientes defeituosos, deve ser emitido um alerta de criticidade alta no painel de monitoramento para intervenção operacional. | Média | US02 |
| **RN06** | **Auto-diagnóstico na Inicialização:** Ao ser inicializado, o sistema deve executar auto-checagem de prontidão dos sensores físicos e do módulo de visão antes de autorizar a operação em regime contínuo. | Média | US01, RNF05 |
| **RN07** | **Reconhecimento Obrigatório de Alarmes Críticos:** Alarmes gerados por falhas consecutivas ou anomalias críticas exigem confirmação explícita do operador no painel para que o estado de alerta seja normalizado. | Média | US02, RNF11 |
| **RN08** | **Rastreabilidade e Imutabilidade de Registros:** Cada ciclo de inspeção deve gerar um registro imutável com identificador sequencial e carimbo de data/hora (*timestamp*) para auditoria de lote e cálculo de OEE. | Média | US05, RNF03 |
| **RN09** | **Identificação de Ociosidade de Linha:** Se a esteira permanecer sem detecção de recipientes por intervalo contínuo superior a 5 minutos, o status operacional do sistema deve transicionar automaticamente para "Linha Ociosa / Em Espera". | Baixa | US02, US03 |
| **RN10** | **Retenção e Expiração de Histórico Local:** Os registros de eventos armazenados no buffer local devem ser mantidos por período mínimo operacional de 30 dias antes de qualquer compactação ou descarte de histórico. | Baixa | US05, RNF03 |
