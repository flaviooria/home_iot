import { statsMock } from "@/app/admin/lib/stats-mock";
import CardStat from "./components/card-stat";

export default function AdminPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Panel de Control</h1>
        <p className="text-muted-foreground text-sm">
          Resumen general de tu infraestructura IoT
        </p>
      </div>

      {/* Grid de Tarjetas de Resumen */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsMock.map((stat, index) => (
          <CardStat
            key={index}
            title={stat.title}
            value={stat.value}
            description={stat.change}
            icon={<stat.icon className="h-4 w-4" />}
            classColor={stat.classColor}
          />
        ))}
      </div>

      {/* Aquí podrías poner una lista de "Actividad Reciente" o "Últimos Dispositivos Agregados" */}
    </div>
  );
}
