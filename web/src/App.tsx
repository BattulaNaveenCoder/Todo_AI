import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000, // 30 seconds before refetch
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <main style={{ padding: "2rem", fontFamily: "system-ui, sans-serif" }}>
        <h1>Todo AI</h1>
        <p>App is running. Ready for Phase 1.</p>
      </main>
    </QueryClientProvider>
  );
}

export { App };
