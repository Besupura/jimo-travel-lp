
interface ImportMeta {
  readonly env: {
    readonly VITE_API_URL: string;
    readonly BASE_URL: string;
    readonly NODE_ENV: string;
    [key: string]: string;
  };
}
