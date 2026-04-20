import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CardStat({
  title,
  value,
  description,
  icon,
  classColor,
}: {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
  classColor?: string;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {/* Añadir color de icono */}
        {icon && <div className={`${classColor}`}>{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className={`text-2xl font-bold ${classColor}`}>{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}
