import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"

type Expense = {
  id: number
  desc: string
  category: string
  amount: number
  date: string
  user: string
}

async function getExpenses(): Promise<Expense[]> {
  try {
    // Determine the API URL based on environment (development vs production)
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8015/api"
    const res = await fetch(`${apiUrl}/expenses`, { cache: "no-store" })
    if (!res.ok) return []
    return res.json()
  } catch (e) {
    console.error("Error fetching expenses:", e)
    return []
  }
}

export default async function Dashboard() {
  const expenses = await getExpenses();
  
  // Calculate total dynamically based on fetched expenses
  const totalAmount = expenses.reduce((acc, exp) => acc + exp.amount, 0);

  return (
    <div className="flex min-h-screen w-full flex-col bg-muted/40">
      <div className="flex flex-col sm:gap-4 sm:py-4 sm:pl-14">
        <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6">
          <h1 className="text-xl font-semibold tracking-tight">MeuSaldo</h1>
          <div className="ml-auto flex items-center gap-2">
            <Button size="sm" variant="outline">
              Convidar Parceiro
            </Button>
            <Button size="sm">
              Conectar WhatsApp
            </Button>
          </div>
        </header>

        <main className="grid flex-1 items-start gap-4 p-4 sm:px-6 sm:py-0 md:gap-8 lg:grid-cols-3 xl:grid-cols-3">
          <div className="grid auto-rows-max items-start gap-4 md:gap-8 lg:col-span-2">
            <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-2 xl:grid-cols-4">
              <Card className="sm:col-span-2">
                <CardHeader className="pb-3">
                  <CardTitle>Gastos da Semana</CardTitle>
                  <CardDescription className="max-w-lg text-balance leading-relaxed">
                    Aqui está o resumo dos seus gastos compartilhados. Continue registrando via WhatsApp!
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold text-red-500">R$ {totalAmount.toFixed(2).replace('.', ',')}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Você (Nesta Semana)</CardDescription>
                  <CardTitle className="text-4xl">R$ 270,50</CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Parceiro (Nesta Semana)</CardDescription>
                  <CardTitle className="text-4xl">R$ 90,90</CardTitle>
                </CardHeader>
              </Card>
            </div>
            
            <Card>
              <CardHeader className="px-7">
                <CardTitle>Últimos Gastos</CardTitle>
                <CardDescription>Histórico sincronizado com o WhatsApp.</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Data</TableHead>
                      <TableHead>Descrição</TableHead>
                      <TableHead className="hidden md:table-cell">Categoria</TableHead>
                      <TableHead className="hidden sm:table-cell">Quem</TableHead>
                      <TableHead className="text-right">Valor</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {expenses.map((exp) => (
                      <TableRow key={exp.id}>
                        <TableCell>{exp.date}</TableCell>
                        <TableCell className="font-medium">{exp.desc}</TableCell>
                        <TableCell className="hidden md:table-cell">{exp.category}</TableCell>
                        <TableCell className="hidden sm:table-cell">{exp.user}</TableCell>
                        <TableCell className="text-right">R$ {exp.amount.toFixed(2).replace('.', ',')}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>
          
          <div>
            <Card className="overflow-hidden">
              <CardHeader className="bg-muted/50">
                <CardTitle>Integração WhatsApp</CardTitle>
                <CardDescription>Como registrar gastos?</CardDescription>
              </CardHeader>
              <CardContent className="p-6 text-sm">
                <div className="grid gap-3">
                  <div className="font-semibold">Basta enviar uma mensagem!</div>
                  <div className="text-muted-foreground">
                    Exemplos:
                    <ul className="list-disc ml-5 mt-2 space-y-1">
                      <li>"Gastei 50 no mercado"</li>
                      <li>"Conta de luz: 120"</li>
                      <li>"Resumo da semana"</li>
                    </ul>
                  </div>
                  <hr className="my-2" />
                  <div className="font-semibold">Automação de Cartão:</div>
                  <div className="text-muted-foreground">
                    Você pode usar o aplicativo MacroDroid para ler as notificações do seu banco e enviar automaticamente para o nosso robô!
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
