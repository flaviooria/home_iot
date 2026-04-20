import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-4xl font-bold">Welcome to the Apolau13 IoT Dashboard</h1>
      <Link href="/admin" className="mt-6 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
        Go to Admin Dashboard
      </Link>
      <p className="mt-4 text-lg text-gray-600">Monitor and manage your IoT devices in real-time.</p>
    </main>
  )
}