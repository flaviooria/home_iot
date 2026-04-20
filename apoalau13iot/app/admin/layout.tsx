import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <div className="flex flex-col flex-1">
        <header className="flex h-14 items-center gap-4 border-b px-6 bg-background">
          <SidebarTrigger />
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground">Admin Panel</p>
          </div>
        </header>
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </SidebarProvider>
  )
}