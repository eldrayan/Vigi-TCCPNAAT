/**
 * Descrição: Renderiza a distribuição de não conformidades por tipo.
 * Autor: Leôncio Ferreira
 */

import { ArcElement, Chart, DoughnutController, Legend, Tooltip, type ChartConfiguration } from "chart.js";
import { useEffect, useRef } from "react";

import styles from "./NonconformityChart.module.scss";
Chart.register(DoughnutController, ArcElement, Legend, Tooltip);

interface NonconformityChartProps {
  data: Record<string, number>;
}

export function NonconformityChart({ data }: NonconformityChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    const configuration: ChartConfiguration<"doughnut"> = {
      type: "doughnut",
      data: {
        labels: Object.keys(data).map((item) => item.replaceAll("_", " ")),
        datasets: [
          {
            data: Object.values(data),
            backgroundColor: ["#00af87", "#f0a23a", "#d85d5d"],
            borderWidth: 0,
          },
        ],
      },
      options: {
        cutout: "68%",
        aspectRatio: 1,
        plugins: { legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 10 } } } },
      },
    };
    const chart = new Chart(canvasRef.current, configuration);
    return () => chart.destroy();
  }, [data]);

  return (
    <div className={styles.chart}>
      <canvas ref={canvasRef} aria-label="Distribuição de não conformidades" role="img" />
    </div>
  );
}
