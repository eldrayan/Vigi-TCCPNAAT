/**
 * Descrição: Exibe os cards de monitoramento dos dispositivos da linha.
 * Autor: Leôncio Ferreira
 */

import { Camera, Cpu, Radio } from "lucide-react";

import type { PageData } from "../../app/page-types";
import { PageSection } from "../layout/PageSection";
import styles from "./StationsPage.module.scss";

function Status({ value }: { value?: string }) {
  const label = value === "ONLINE" ? "Online" : value === "IDLE" ? "Em espera" : value === "ERROR" ? "Erro" : value === "OFFLINE" ? "Offline" : "Sem status";
  const style = value === "ONLINE" ? styles.online : value === "ERROR" ? styles.error : styles.offline;
  return <span className={style}><i aria-hidden="true" />{label}</span>;
}

function Peripheral({ icon: Icon, name, status }: { icon: typeof Radio; name: string; status?: string }) {
  return <div className={styles.peripheral}><div><Icon size={14} /><span>{name}</span></div><Status value={status} /></div>;
}

export function StationsPage({ stations }: PageData) {
  return <PageSection title="Estações" description="Acompanhe o estado e a conectividade dos dispositivos de inspeção.">
    <div className={styles.grid}>{stations.map((station) => {
      const online = station.status?.connection === "ONLINE";
      return <article className={styles.card} key={station.id}>
        <header><div><h3>{station.name}</h3><p>{station.code} · {station.device_id}</p></div><Status value={online ? "ONLINE" : "OFFLINE"} /></header>
        <div className={styles.peripherals}><Peripheral icon={Radio} name="Sensor" status={station.status?.sensor} /><Peripheral icon={Camera} name="Câmera" status={station.status?.camera} /><Peripheral icon={Cpu} name="Processamento" status={station.status?.processing} /></div>
      </article>;
    })}</div>
  </PageSection>;
}
