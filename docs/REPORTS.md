# Relatórios e checkpoints do pipeline de modelos

Os scripts do ciclo de vida do modelo produzem artefatos diferentes para
responder a perguntas diferentes: como o treinamento ocorreu, qual estado do
modelo deve ser usado, se ele atende aos critérios de qualidade e se pode se
tornar o modelo ativo.

## Checkpoints do treinamento

Um checkpoint contém os pesos aprendidos pela rede neural em determinado ponto
do treinamento. Ele permite usar ou retomar o modelo sem executar novamente
todo o treinamento.

O Ultralytics normalmente gera dois checkpoints no diretório da execução:

- `best.pt`: pesos da época que obteve o melhor resultado de validação;
- `last.pt`: pesos da última época executada.

Eles podem ser diferentes. Se as métricas piorarem nas últimas épocas, por
exemplo devido a overfitting, `best.pt` preserva um estado anterior melhor,
enquanto `last.pt` representa apenas o estado final cronológico.

O Vigi usa `model.trainer.best` como fonte do checkpoint selecionado. O script
de treinamento copia esse arquivo para `models/candidates/` com um nome que
identifica a execução, como:

```text
models/candidates/vigi-yolov8n-cls-baseline.pt
```

Um arquivo em `models/candidates/` ainda é um modelo candidato, não o modelo
ativo do sistema.

## Diretório da execução

`model.trainer.save_dir` indica a pasta criada pelo Ultralytics para uma
execução de treinamento. Dependendo da versão e configuração, ela pode conter:

```text
runs/classify/baseline/
├── weights/
│   ├── best.pt
│   └── last.pt
├── args.yaml
├── results.csv
├── results.png
├── confusion_matrix.png
└── vigi-training-summary.json
```

Esse diretório funciona como registro experimental: reúne parâmetros, métricas
por época, curvas, imagens diagnósticas e checkpoints. A composição exata dos
arquivos produzidos pelo Ultralytics pode variar entre versões.

## Resumo do treinamento

O script `scripts/treinar_modelo.py` acrescenta o arquivo
`vigi-training-summary.json` ao diretório da execução. Exemplo conceitual:

```json
{
  "checkpoint": "models/candidates/vigi-yolov8n-cls-tuned.pt",
  "run_directory": "runs/classify/tuned",
  "dataset_hash": "abc123...",
  "ultralytics_version": "8.4.146",
  "config": {
    "epochs": 100,
    "imgsz": 224
  }
}
```

O resumo registra:

- o checkpoint copiado;
- o diretório original da execução;
- a identificação do dataset utilizado;
- a versão do Ultralytics;
- a configuração aplicada ao treinamento.

Ele auxilia a reprodução e a investigação do treinamento, mas não comprova que
o modelo foi aprovado.

## Relatório de predições

Durante a calibração e a avaliação final, `scripts/avaliar_modelo.py` gera:

```text
reports/calibration/predictions.csv
reports/model-gate/predictions.csv
```

O arquivo contém uma linha por imagem avaliada:

```csv
path,expected,predicted,confidence
imagem-01.jpg,01_conforme,01_conforme,0.96
imagem-02.jpg,02_sem_tampa,01_conforme,0.63
```

O primeiro arquivo descreve as imagens do split `val`; o segundo descreve as
imagens do split `test`. Eles permitem identificar quais imagens foram
classificadas corretamente ou incorretamente. Durante a calibração, as
confidências das predições de validação também são usadas para selecionar o
`confidence_threshold`.

## Relatório de métricas

A calibração e a avaliação final também geram, respectivamente:

```text
reports/calibration/metrics.json
reports/model-gate/metrics.json
```

O relatório de calibração registra o threshold selecionado no split `val`. A
avaliação final recebe esse relatório, usa automaticamente o split `test` e
grava o mesmo threshold em `reports/model-gate/metrics.json`. Esse relatório
final consolida os resultados e a decisão do quality gate. Exemplo conceitual:

```json
{
  "accuracy": 0.94,
  "false_negative_rate": 0.08,
  "false_positive_rate": 0.12,
  "coverage": 0.91,
  "sample_count": 200,
  "quality_gate": {
    "accuracy_min": 0.90,
    "false_negative_rate_max": 0.10,
    "false_positive_rate_max": 0.15,
    "confidence_threshold": 0.72,
    "provisional": false,
    "approved": true
  }
}
```

Ele informa:

- a acurácia global;
- a taxa de falsos negativos;
- a taxa de falsos positivos;
- a cobertura acima do limiar de confiança;
- a quantidade de imagens avaliadas;
- o limiar de confiança utilizado;
- o resultado do quality gate.

Na promoção, o relatório final de teste é a fonte do `confidence_threshold`. O
script de promoção não recalcula nem permite substituir o limiar avaliado.

## Matriz de confusão

A avaliação pode produzir:

```text
reports/model-gate/confusion-matrix.png
```

A matriz mostra como cada classe real foi distribuída entre as classes
previstas. Ela ajuda a detectar, por exemplo, uma confusão recorrente entre
`03_tampa_torta` e `04_amassado`, mesmo quando a acurácia global parece
aceitável.

A matriz é um artefato diagnóstico. A decisão automática utiliza as métricas
numéricas do relatório.

## Manifesto do modelo ativo

Após a aprovação, `scripts/promover_modelo.py` gera:

```text
models/active/manifest.json
```

O manifesto não é um relatório de execução. Ele é o contrato operacional do
modelo promovido. Exemplo conceitual:

```json
{
  "model_path": "vigi-yolov8n-cls.pt",
  "format": "pytorch",
  "classes": [
    "01_conforme",
    "02_sem_tampa",
    "03_tampa_torta",
    "04_amassado"
  ],
  "confidence_threshold": 0.72,
  "image_size": 224,
  "dataset_hash": "abc123...",
  "ultralytics_version": "8.4.146",
  "metrics": {
    "accuracy": 0.94,
    "false_negative_rate": 0.08,
    "false_positive_rate": 0.12
  }
}
```

A inferência usa o manifesto para descobrir:

- qual arquivo de pesos carregar;
- qual formato de modelo utilizar;
- quais classes são válidas;
- qual limiar de confiança aplicar;
- qual tamanho de imagem utilizar.

Os pesos promovidos e o manifesto formam juntos o modelo ativo. Um não deve ser
atualizado sem o outro.

Nesta versão, somente checkpoints PyTorch `.pt` podem ser promovidos e usados
na inferência. TFLite não integra o contrato operacional.

## Relatório de benchmark

Na Raspberry Pi, `scripts/benchmark_modelo.py` pode gravar:

```text
reports/benchmark-pi.json
```

O relatório registra as execuções de aquecimento e medição, erros de inferência
e estatísticas como média, p50, p95 e maior latência. O contrato corrigido também
deve registrar:

- `successful_runs`: inferências medidas concluídas sem erro técnico;
- `inference_errors`: erros técnicos durante as medições;
- `warmup_errors`: erros técnicos durante o aquecimento;
- `within_500ms_ratio`: proporção das execuções medidas concluídas em até 500 ms;
- `latency_gate`: resultado final do gate de latência.

Baixa confiança e anomalias do produto são resultados concluídos, não erros de
inferência. Já qualquer `ERRO_INFERENCIA`, inclusive no aquecimento, reprova o
benchmark.

O benchmark mede a latência da inferência do modelo. Ele não homologa sozinho o
RNF01 completo, que também considera detecção pelo sensor, captura da imagem,
preparação da entrada, decisão e disponibilização do resultado.

## Visão geral

| Artefato | Finalidade |
| --- | --- |
| `best.pt` | Melhor estado do modelo segundo a validação |
| `last.pt` | Estado do modelo na última época |
| `vigi-training-summary.json` | Rastreabilidade da execução de treinamento |
| `predictions.csv` | Resultado individual de cada imagem avaliada |
| `metrics.json` | Métricas agregadas, limiar avaliado e quality gate |
| `confusion-matrix.png` | Diagnóstico visual dos erros entre classes |
| `manifest.json` | Contrato operacional do modelo ativo |
| `benchmark-pi.json` | Desempenho temporal do modelo no hardware de borda |
