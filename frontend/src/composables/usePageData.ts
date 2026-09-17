import { onMounted, ref } from "vue";

export function usePageData<T>(fileName: string) {
  const data = ref<T | null>(null);
  const loading = ref(true);
  const error = ref<string | null>(null);

  onMounted(async () => {
    try {
      const response = await fetch(`/data/${fileName}`);

      if (!response.ok) {
        const statusText =
          "statusText" in response && response.statusText
            ? ` ${response.statusText}`
            : "";
        throw new Error(
          `Failed to load ${fileName}: ${response.status}${statusText}`,
        );
      }

      data.value = (await response.json()) as T;
      error.value = null;
    } catch (err) {
      data.value = null;
      error.value =
        err instanceof Error ? err.message : `Failed to load ${fileName}`;
    } finally {
      loading.value = false;
    }
  });

  return { data, loading, error };
}
