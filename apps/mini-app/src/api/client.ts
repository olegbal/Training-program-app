const API_URL = import.meta.env.VITE_API_URL ?? "/api";

export async function getHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_URL}/health`);
  if (!response.ok) {
    throw new Error("API health check failed");
  }
  return response.json() as Promise<{ status: string }>;
}
