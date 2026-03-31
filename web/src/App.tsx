import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { TodosPage } from "./pages/TodosPage";

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
      {/* Global page shell — padding and font applied once here */}
      <main style={{ padding: "2rem", fontFamily: "system-ui, sans-serif" }}>
        <TodosPage />
      </main>
    </QueryClientProvider>
  );
}

export { App };
