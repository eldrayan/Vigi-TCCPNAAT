import { Chart, ArcElement, Legend, Tooltip, type ChartConfiguration } from "chart.js";
import { useEffect, useRef } from "react";

Chart.register(ArcElement, Legend, Tooltip);

interface NonconformityChartProps { data: Record<string, number>; }

/** Exibe a distribuição dos defeitos físicos registrados no período. */
export function NonconformityChart({ data }: NonconformityChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    const configuration: ChartConfiguration<"doughnut"> = {
      type: "doughnut",
      data: {
        labels: Object.keys(data).map((item) => item.replaceAll("_", " ")),
        datasets: [{
          data: Object.values(data),
          backgroundColor: ["#00af87", "#f0a23a", "#d85d5d"],
          borderWidth: 0,
        }],
      },
      options: { cutout: "68%", plugins: { legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 10 } } } } },
    };
    const chart = new Chart(canvasRef.current, configuration);
    return () => chart.destroy();
  }, [data]);

  return <canvas ref={canvasRef} aria-label="Distribuição de não conformidades" role="img" />;
}
