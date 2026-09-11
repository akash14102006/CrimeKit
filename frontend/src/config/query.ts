/** TanStack Query defaults shared by all query hooks. */
export const queryDefaults = {
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
} as const;
