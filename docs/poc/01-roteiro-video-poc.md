# Entrega 2: Roteiro de demonstração da PoC do Vigi

Duração prevista: 5 minutos.

Versão: rascunho inicial para validação, 11/09/2026.

Vínculo: [issue #13](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/13), entregável de roteiro da demonstração prática.

Dependência de execução: [issue #11](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/11), modelo e pipeline de inferência na Raspberry Pi 5.

## 1. Objetivo e recorte

Mostrar a classificação visual de recipientes em funcionamento. Quem assistir deve conseguir identificar a entrada, acompanhar a inferência e relacionar o resultado à amostra apresentada.

Este vídeo é a PoC da Entrega 2, com publicação prevista como não listado no YouTube. O [pitch final de até 15 minutos: Entrega 3](../pitch/01-roteiro-pitch.md) é outro vídeo, com roteiro próprio. O [README: Entrega 4](../../README.md) organiza o esboço da documentação. Esses materiais também fazem parte da issue #13.

A sequência proposta começa com o recipiente na bancada. A câmera fornece a imagem ao modelo na Raspberry Pi 5, e a classe prevista aparece na tela ou no terminal. Essa montagem mostra a inferência funcionando com outro elemento da arquitetura, a câmera, e pode ser demonstrada antes da integração completa do sistema.

A preparação do roteiro pode seguir enquanto a equipe finaliza a issue #11. Para gravar, será preciso verificar o modelo e sua execução na bancada. O código disponível nesta revisão contém o coletor de dataset, que não executa inferência. Seu comando não deve ser usado para apresentar o classificador.

A case pode aparecer na apresentação da montagem. O dashboard cabe como saída adicional se já receber a inferência; sua ausência não impede este recorte da PoC. A explicação mais ampla sobre autonomia local, montagem compacta e supervisão fica no pitch final.

## 2. Preparação da bancada e da tela

- Separar um recipiente conforme e outro com um defeito visível pertencente às classes efetivamente disponíveis no modelo. Preferir `sem_tampa` pela facilidade de identificação visual, se essa classe estiver operacional.
- Manter iluminação, fundo e enquadramento consistentes. Identificar as amostras como A e B para relacionar cada entrada à respectiva saída.
- Mostrar a case e confirmar como a Raspberry Pi e a câmera estão acomodadas. Apontar também os elementos externos, sem dizer que toda a instalação ocupa apenas a case. Explicar onde o processamento acontece. Se houver notebook conectado por acesso remoto, identificá-lo como tela de acesso, quando esse for seu papel real.
- Organizar a gravação para mostrar a bancada e a saída legível, por enquadramento conjunto ou captura de tela com imagem da bancada sobreposta. Mostrar o quadro realmente usado pelo modelo, quando disponível.
- Usar o terminal ou a janela de inferência existente. O vídeo pode ser gravado sem criar um dashboard.
- Ensaiar o acionamento real, manual ou contínuo, e declará-lo na fala. Só atribuir a captura ao sensor E18-D80NK se essa integração estiver funcionando.

### Dados a preencher após a entrega da issue #11

| Item | Registro para o ensaio |
| --- | --- |
| Responsável pela apresentação e pela operação | A definir com a equipe |
| Modelo, versão e caminho dos pesos usados | A confirmar |
| Classes presentes no modelo exportado | A confirmar |
| Equipamento que executa a inferência | Confirmar Raspberry Pi 5; registrar se for outro |
| Câmera e forma de captura/acionamento | A confirmar |
| Comando real de execução e diretório de trabalho | A preencher após teste na bancada |
| Saída disponível | Confirmar classe, score e eventual tempo medido |
| Evidência do ensaio | Registrar amostras, saídas reais e limitações observadas |
| Case e montagem | Confirmar componentes internos e externos; medir dimensões se forem citadas |
| Dashboard | Registrar se está integrado, se é interface com dados simulados ou se ainda está previsto |
| Conectividade no ensaio | Registrar uso de internet, rede local e acesso remoto; só declarar offline para as funções testadas |

## 3. Roteiro de gravação: 00:00 a 05:00

Adapte as falas ao ensaio e preencha os campos entre colchetes com informações verificadas. O tempo de cada bloco inclui a narração, a operação da bancada, a troca de amostras e as pausas para leitura da tela.

### 00:00 a 00:30: Apresentação e objetivo (30 s)

Imagem/ação: apresentador e bancada, com o nome Vigi e a identificação "Entrega 2: Prova de Conceito".

> Este é o Vigi, um projeto de inspeção visual de recipientes em linhas de envase. Queremos distinguir recipientes conformes de outros com defeitos visíveis, como a falta de tampa. Nesta prova de conceito, vamos testar esse funcionamento inicial: fornecer uma imagem ao modelo, executar a inferência e mostrar a classificação na tela.

### 00:30 a 01:10: Elementos e caminho da informação (40 s)

Imagem/ação: mostrar a case na bancada e apontar o recipiente, a câmera, a Raspberry Pi e a tela. Exibir brevemente o fluxo `Câmera → Inferência na Raspberry Pi → Resultado`.

Após confirmar a montagem, adaptar a fala:

> Esta case acomoda [componentes confirmados]. A câmera fornece a imagem do recipiente, e a Raspberry Pi 5 executa localmente o modelo [nome e versão], treinado para distinguir [classes disponíveis]. A imagem e o resultado aparecem nesta tela. A captura é [manual/contínua/acionada pelo sensor]. Assim, acompanhamos a câmera e a inferência funcionando juntas.

Usar apenas a modalidade real de captura e as informações exibidas. Processamento local não comprova segurança nem funcionamento offline. Se o resultado for visualizado por acesso remoto, informar que essa visualização usa a rede local.

### 01:10 a 02:20: Primeiro ciclo: recipiente conforme (70 s)

Imagem/ação, em sequência contínua:

1. Mostrar a amostra A e explicar por que ela é visualmente conforme.
2. Posicioná-la diante da câmera e mostrar sua imagem de entrada.
3. Iniciar a execução pelo comando validado ou evidenciar o próximo ciclo, caso o processo já esteja rodando.
4. Acompanhar o processamento e manter o resultado legível por alguns segundos, sem corte entre entrada e saída.

> Esta é a amostra A, com a tampa posicionada e sem o defeito que vamos mostrar depois. A imagem na tela será usada nesta execução. Agora [ação real que inicia o ciclo]. O programa passa a imagem ao modelo, que retorna a classificação [classe observada] para essa amostra. [Se disponível: o score exibido foi valor observado.]

Compare a previsão com a condição da amostra. Se houver divergência, descreva o erro em vez de ler a fala prevista para um acerto. O score de uma previsão não é a acurácia do modelo.

### 02:20 a 03:30: Segundo ciclo: defeito visível (70 s)

Imagem/ação, em sequência contínua:

1. Retirar A, mostrar a amostra B e apontar o defeito visível.
2. Apresentar B à câmera, preservando as condições da bancada.
3. Repetir o ciclo e mostrar a nova saída, distinguindo-a do resultado anterior.
4. Comparar a classe retornada com o defeito apresentado.

> Esta é a amostra B, que apresenta [defeito visível]. Vamos fazer uma nova inferência com a mesma câmera e o mesmo enquadramento. Para esta imagem, o modelo retornou [classe observada]. [Se houver acerto: a classificação corresponde ao defeito mostrado.]

Em caso de erro ou instabilidade, descreva o que ocorreu e a limitação observada. Ao repetir o teste, mostre novamente a entrada e a execução. Preserve a saída real na gravação, sem substituí-la por texto na edição.

### 03:30 a 04:15: Leitura do resultado e alcance da prova (45 s)

Imagem/ação: manter a saída real visível e apontar seus campos. Se o dashboard já estiver integrado, mostrar o evento de uma das amostras e relacioná-lo à inferência por identificador ou horário, dentro destes 45 segundos. Se houver tempo disponível, repetir A, sem tratar a repetição como avaliação estatística.

Se o painel tiver apenas dados simulados, reservá-lo para a explicação do pitch, onde será identificado como protótipo de interface. Na PoC, preservar a saída real da inferência. Se ainda estiver previsto, citar o dashboard no encerramento como parte a integrar.

> A classe é a previsão do modelo para a imagem apresentada. [Se disponível: este score acompanha a previsão; ele não representa a acurácia global.] Nos ciclos que mostramos, observamos [resumo fiel dos resultados]. Esses testes mostram o funcionamento inicial da captura com a inferência nesta bancada. Para avaliar a qualidade do modelo, ainda precisamos considerar os testes com imagens que ficaram fora do treinamento.

Se a saída mostrar um tempo medido, explique a que intervalo ele se refere. O RNF01 considera toda a inspeção, da detecção à disponibilização do resultado; medir apenas a inferência não comprova esse requisito. Os dois exemplos do vídeo também não bastam para comprovar a meta de acurácia do RNF06.

### 04:15 a 05:00: Limites e próxima etapa técnica (45 s)

Imagem/ação: voltar à bancada ou ao fluxo simplificado. Identificar visualmente o trecho demonstrado e as integrações futuras.

Adaptar a fala ao que estiver funcionando:

> Nesta PoC, usamos [componentes realmente usados] e mostramos os resultados das amostras. O próximo passo é [integração ainda pendente, por exemplo: ligar o gatilho do sensor à captura e à inferência]. Depois, estão previstos o registro dos eventos no SQLite e o envio por MQTT para o backend e o dashboard. [Citar somente o que de fato falta integrar.] Também precisamos ampliar os testes de classificação e medir o tempo do ciclo.

Os atuadores estão fora do escopo atual do projeto. Por isso, a rejeição mecânica de recipientes não deve ser anunciada como próxima entrega.

## 4. Alternativa se a captura integrada ainda não estiver disponível

Se a captura integrada ainda não funcionar, use uma imagem já capturada. Mostre qual arquivo será usado, inicie o processamento e mantenha a gravação até a saída, sem cortes no ciclo. Informe que a entrada é um arquivo e em qual equipamento a inferência está rodando.

O teste com arquivo demonstra a inferência sobre uma imagem. Para mostrar a câmera funcionando com o modelo e buscar o nível Avançado, será preciso gravar o ciclo com captura integrada ou usar outro elemento da arquitetura conectado à inferência. Uma execução apenas em notebook ou ambiente remoto não valida a inferência embarcada na Raspberry Pi.

## 5. Conferência com os critérios da atividade

| Critério informado pela plataforma | Evidência planejada no vídeo |
| --- | --- |
| Entrada ou início da execução identificável | Amostras A e B, imagem de entrada e acionamento visível |
| Tecnologia principal funcionando | Execução real do modelo durante os dois ciclos |
| Resultado produzido | Classe prevista legível e vinculada à amostra correspondente |
| Entrada, execução e resultado em uma sequência acompanhável | Ciclos contínuos de 01:10 a 03:30, sem cortes internos |
| Tecnologia central com outro elemento da arquitetura | Câmera fornecendo a imagem ao pipeline de inferência |
| Explicação da entrada, funcionamento, resultado e função dos elementos | Apresentação da montagem e narração dos ciclos |
| Próxima etapa ou função ainda não integrada/implementada | Encerramento com pendências concretas verificadas no ensaio |
| Artefato solicitado | Link do vídeo não listado no YouTube, com cerca de 5 minutos |

Para atender ao nível Avançado, a gravação precisa mostrar as evidências planejadas na tabela.

## 6. Checklist do ensaio e da entrega

- [ ] Confirmar com o responsável pela issue #11 os pesos, classes, comando e ambiente de execução.
- [ ] Executar os dois ciclos na bancada e preencher os dados pendentes deste roteiro.
- [ ] Validar o roteiro e dividir apresentação/operação com a equipe.
- [ ] Conferir se a imagem mostrada corresponde à entrada real da inferência.
- [ ] Confirmar a câmera integrada, ou declarar explicitamente a alternativa utilizada.
- [ ] Ajustar as falas de resultado, limitações e próxima etapa ao estado observado.
- [ ] Confirmar a apresentação da case e a função de cada componente mostrado.
- [ ] Se usar o dashboard, verificar que o evento mostrado veio da inferência gravada.
- [ ] Identificar a conexão usada e evitar afirmações de segurança, acesso restrito ou autonomia offline sem verificação.
- [ ] Ensaiar com cronômetro para aproximadamente 5 minutos, preservando o tempo de leitura das saídas.
- [ ] Conferir áudio e legibilidade; manter cada ciclo sem cortes entre entrada e resultado.
- [ ] Revisar a gravação completa e confirmar que não há métricas ou integrações apresentadas sem evidência.
- [ ] Publicar o vídeo como não listado no YouTube e testar o acesso pelo link sem a conta do autor.
- [ ] Registrar o link final e enviá-lo à plataforma da atividade.

Link do vídeo: pendente de gravação e publicação.

## 7. Referências e alinhamento da issue

- [Issue #13: documentação e roteiros](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/13).
- [Issue #11: treinamento e inferência](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/11).
- [Arquitetura do Vigi](../arquitetura/diagrama-arquitetural.md).
- [Requisitos funcionais: US01](../requisitos/02-requisitos-funcionais.md).
- [Requisitos não funcionais: RNF01 e RNF06](../requisitos/03-requisitos-nao-funcionais.md).
- Critérios da Entrega 2 fornecidos na solicitação desta atividade.

A issue #13 pede uma demonstração com sensor e SQLite/MQTT/Node-RED. Para a Entrega 2, este roteiro cobre a inferência inicial; o fluxo completo da issue continua pendente. A apresentação segue a arquitetura documentada, com FastAPI e React para supervisão, sem Node-RED. Para concluir a issue #13, também será preciso finalizar os demais entregáveis e validá-los com a equipe.
