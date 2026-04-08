import TodoPage from './pages/TodoPage'

const App = () => {
  return (
    <main className="relative min-h-screen overflow-hidden">
      {/* Decorative blobs */}
      <div className="pointer-events-none fixed -top-40 -right-40 h-96 w-96 rounded-full bg-primary-400/20 blur-3xl" />
      <div className="pointer-events-none fixed top-1/3 -left-40 h-96 w-96 rounded-full bg-accent-400/15 blur-3xl" />
      <div className="pointer-events-none fixed -bottom-40 right-1/4 h-80 w-80 rounded-full bg-primary-300/25 blur-3xl" />
      <TodoPage />
    </main>
  )
}

export default App
